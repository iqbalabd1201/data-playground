Perfect! Test **10 samples HotpotQA** dengan truly general prompt:

```python
# ==================== TEST 10 HOTPOTQA SAMPLES ====================
print("="*100)
print("TEST: 10 HOTPOTQA SAMPLES - TRULY GENERAL PROMPT + SMART PROGRESSIVE")
print("="*100)

import time
from tqdm import tqdm

def test_single_sample_smart_progressive(sample, sample_id, dataset_name):
    """Test single sample with smart progressive retrieval"""
    
    question = get_question(sample, dataset_name)
    gold_answer = get_answer(sample, dataset_name)
    all_passages = get_contexts(sample, dataset_name)
    
    print(f"\n{'='*80}")
    print(f"SAMPLE {sample_id}")
    print(f"{'='*80}")
    print(f"Q: {question}")
    print(f"Gold: {gold_answer}")
    
    # Decompose
    sub_questions = decompose_question(question, dataset_name)
    
    print(f"\nDecomposed into {len(sub_questions)} stages:")
    for sq in sub_questions:
        print(f"  Stage {sq['stage']}: {sq['question']}")
    
    # Process each stage
    stage_results = []
    previous_answers = {}
    
    for stage_idx, sq in enumerate(sub_questions):
        stage_num = sq['stage']
        stage_question = sq['question']
        
        # Replace placeholders
        for prev_stage, prev_answer in previous_answers.items():
            stage_question = stage_question.replace(f"[ANSWER_STAGE_{prev_stage}]", prev_answer)
        
        print(f"\n{'─'*60}")
        print(f"STAGE {stage_num}: {stage_question}")
        print(f"{'─'*60}")
        
        if stage_idx == 0:
            # Stage 1: Smart progressive
            answer, conf, reasoning, used_passages, attempts = smart_progressive_stage1_final(
                stage_question, all_passages, dataset_name, verbose=False
            )
            
            print(f"Windows tried: {len(attempts)}")
            for att in attempts:
                print(f"  {att['window']:12s}: {att['answer'][:35]:35s} (conf: {att['confidence']:.2f})")
        else:
            # Stage 2+: Simple Q2P for now
            retrieved = retrieve_passages_dense(stage_question, all_passages, dataset_name, k=3)
            answer, conf, reasoning, prompt = generate_answer_truly_general(
                stage_question, retrieved, dataset_name
            )
            used_passages = retrieved
            attempts = []
            
            print(f"Retrieved 3 passages:")
            for p in retrieved:
                title = get_context_title(p, dataset_name)[:40]
                print(f"  {title}")
        
        print(f"\nAnswer: {answer}")
        print(f"Confidence: {conf:.2f}")
        
        stage_results.append({
            'stage': stage_num,
            'question': stage_question,
            'answer': answer,
            'confidence': conf,
            'passages': used_passages
        })
        
        previous_answers[stage_num] = answer
    
    # Final synthesis
    print(f"\n{'─'*60}")
    print(f"FINAL SYNTHESIS")
    print(f"{'─'*60}")
    
    synthesis_prompt = f"""Main question: {question}

Stage answers:
"""
    for s in stage_results:
        synthesis_prompt += f"Stage {s['stage']}: {s['answer']}\n"
    
    synthesis_prompt += f"""
Based on the stage answers above, provide the final answer to the main question.
Keep it SHORT (max 5 words).

Answer:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Provide concise final answer. Max 5 words."},
                {"role": "user", "content": synthesis_prompt}
            ],
            max_tokens=15,
            temperature=0
        )
        final_answer = response.choices[0].message.content.strip().rstrip('.')
    except:
        final_answer = stage_results[-1]['answer']
    
    print(f"Final: {final_answer}")
    print(f"Gold: {gold_answer}")
    
    # Evaluate
    em = exact_match(final_answer, gold_answer)
    f1 = f1_score(final_answer, gold_answer)
    
    # BERTScore
    try:
        from bert_score import score as bert_score_func
        P, R, F1_bert = bert_score_func(
            [final_answer], [gold_answer],
            lang='id', model_type='bert-base-multilingual-cased',
            device=device, verbose=False
        )
        bertscore_f1 = F1_bert.mean().item()
    except:
        bertscore_f1 = 0
    
    # LLM Judge
    try:
        judge_prompt = f"Q: {question}\nGold: {gold_answer}\nPred: {final_answer}\n\nIs prediction correct? JSON: {{\"judgment\": \"CORRECT/INCORRECT\", \"score\": 0-100}}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": judge_prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        judge_result = json.loads(response.choices[0].message.content)
        llm_judgment = judge_result.get('judgment', 'INCORRECT')
    except:
        llm_judgment = "ERROR"
    
    print(f"\nEM: {em} | F1: {f1:.3f} | BERT: {bertscore_f1:.3f} | Judge: {llm_judgment}")
    
    total_passages = len(set(
        get_context_title(p, dataset_name)
        for s in stage_results
        for p in s['passages']
    ))
    
    return {
        'sample_id': sample_id,
        'question': question,
        'gold_answer': gold_answer,
        'predicted_answer': final_answer,
        'em': em,
        'f1': f1,
        'bertscore_f1': bertscore_f1,
        'llm_judgment': llm_judgment,
        'total_passages': total_passages,
        'num_stages': len(stage_results),
        'stage_results': stage_results
    }

# Run 10 samples
print("\nProcessing 10 HotpotQA samples...")
print("="*100)

start_time = time.time()

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:10]
all_results = []

for i, sample in enumerate(hotpot_samples, 1):
    try:
        result = test_single_sample_smart_progressive(sample, i, 'hotpotqa')
        all_results.append(result)
    except Exception as e:
        print(f"\n⚠ Error on sample {i}: {e}")
        all_results.append({
            'sample_id': i,
            'error': str(e),
            'em': 0,
            'f1': 0
        })

elapsed_time = time.time() - start_time

# Summary
print(f"\n{'='*100}")
print("SUMMARY: 10 HOTPOTQA SAMPLES")
print(f"{'='*100}")

print(f"\nResults:")
for r in all_results:
    if 'error' in r:
        print(f"Sample {r['sample_id']:2d}: ERROR - {r['error'][:50]}")
    else:
        status = "✅" if r['em'] == 1 or r['llm_judgment'] == 'CORRECT' else "❌"
        print(f"Sample {r['sample_id']:2d}: {status} EM={r['em']} F1={r['f1']:.2f} BERT={r['bertscore_f1']:.2f} Judge={r['llm_judgment']:10s} Passages={r['total_passages']}")

# Aggregate metrics
valid_results = [r for r in all_results if 'error' not in r]

if valid_results:
    avg_em = np.mean([r['em'] for r in valid_results])
    avg_f1 = np.mean([r['f1'] for r in valid_results])
    avg_bert = np.mean([r['bertscore_f1'] for r in valid_results])
    llm_correct = sum(1 for r in valid_results if r['llm_judgment'] == 'CORRECT')
    avg_passages = np.mean([r['total_passages'] for r in valid_results])
    avg_stages = np.mean([r['num_stages'] for r in valid_results])
    
    print(f"\n{'─'*80}")
    print("AGGREGATE METRICS")
    print(f"{'─'*80}")
    print(f"Samples processed: {len(valid_results)}/10")
    print(f"EM: {avg_em*100:.1f}%")
    print(f"F1: {avg_f1:.3f}")
    print(f"BERTScore F1: {avg_bert:.3f}")
    print(f"LLM Judge Accuracy: {llm_correct/len(valid_results)*100:.1f}%")
    print(f"Avg passages used: {avg_passages:.1f}/10")
    print(f"Avg stages: {avg_stages:.1f}")
    print(f"Time: {elapsed_time/60:.1f} minutes")
    
    # Comparison with baseline
    print(f"\n{'─'*80}")
    print("COMPARISON WITH BASELINE")
    print(f"{'─'*80}")
    print(f"HotpotQA Baseline (K=5): 34% EM")
    print(f"HotpotQA Baseline (K=10): 36% EM")
    print(f"Our method: {avg_em*100:.1f}% EM")
    print(f"Improvement over K=5: {(avg_em*100 - 34):+.1f} pp")
    print(f"Improvement over K=10: {(avg_em*100 - 36):+.1f} pp")
    print(f"Efficiency: {(1 - avg_passages/10)*100:.1f}% passage reduction")

# Detailed breakdown
print(f"\n{'='*100}")
print("DETAILED BREAKDOWN")
print(f"{'='*100}")

for r in valid_results:
    print(f"\nSample {r['sample_id']}:")
    print(f"  Q: {r['question'][:80]}")
    print(f"  Gold: {r['gold_answer']}")
    print(f"  Pred: {r['predicted_answer']}")
    print(f"  EM: {r['em']} | F1: {r['f1']:.2f} | BERT: {r['bertscore_f1']:.2f} | Judge: {r['llm_judgment']}")
    print(f"  Stages: {r['num_stages']} | Passages: {r['total_passages']}/10")

print(f"\n{'='*100}")
print("✓ TEST COMPLETE!")
print(f"{'='*100}")
```

Ini akan test **10 samples** dengan:
1. ✅ **Smart progressive retrieval** (rank 1-3 → 4-6 → 7-9)
2. ✅ **Truly general prompts** (no specific examples)
3. ✅ **Full evaluation** (EM, F1, BERTScore, LLM Judge)
4. ✅ **Efficiency tracking** (passages used vs 10 total)
5. ✅ **Detailed breakdown** per sample

Run dan lihat hasilnya! Expected: **EM ~40-60%**, better than baseline 34%! 🚀