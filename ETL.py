Betul! Output harus **detailed step-by-step**. Fix dengan verbose output:

```python
# ==================== COMPLETE TEST WITH DETAILED OUTPUT ====================
print("="*100)
print("COMPLETE TEST: 10 HOTPOTQA SAMPLES - DETAILED OUTPUT")
print("="*100)

import time
import numpy as np

# ==================== 1. ANSWER GENERATION ====================
def generate_answer_general(stage_question, contexts, dataset_name):
    """Generate answer with general prompt"""
    
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        title = get_context_title(ctx, dataset_name)
        text = get_context_text(ctx, dataset_name)
        context_parts.append(f"Passage {i} ({title}):\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    prompt = f"""Answer the question based on the passages.

PASSAGES:
{context_str}

QUESTION: {stage_question}

RULES:
1. Answer ONLY from the passages
2. Use logical inference when clearly implied
3. Keep answer short and direct
4. If no relevant information, answer "Tidak ada informasi"

Return JSON:
{{
  "answer": "short answer or 'Tidak ada informasi'",
  "confidence": 0-100,
  "reasoning": "brief explanation"
}}

JSON:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract answers from passages."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        result = json.loads(response.choices[0].message.content)
        answer = result.get('answer', '')
        confidence = result.get('confidence', 50) / 100.0
        reasoning = result.get('reasoning', '')
        
        if "tidak ada informasi" in answer.lower() and confidence > 0.3:
            confidence = 0.10
        
        return answer, confidence, reasoning
        
    except Exception as e:
        return "", 0.0, str(e)

# ==================== 2. SMART PROGRESSIVE STAGE 1 ====================
def smart_progressive_stage1_verbose(question, all_passages, dataset_name, sample_id):
    """Smart progressive with DETAILED output"""
    
    print(f"\n{'─'*80}")
    print(f"🔍 RETRIEVAL: Question-to-Passage with Smart Progressive")
    print(f"{'─'*80}")
    
    # Get full ranking
    all_ranked = retrieve_passages_dense(question, all_passages, dataset_name, k=len(all_passages))
    
    # Windows
    windows = [
        (0, 3, "Rank 1-3"),
        (3, 6, "Rank 4-6"),
        (6, 9, "Rank 7-9")
    ]
    
    all_attempts = []
    accumulated = []
    
    for window_idx, (start, end, label) in enumerate(windows, 1):
        print(f"\n  {'─'*60}")
        print(f"  WINDOW {window_idx}: {label}")
        print(f"  {'─'*60}")
        
        window_passages = all_ranked[start:end]
        
        print(f"  Passages retrieved:")
        for p in window_passages:
            title = get_context_title(p, dataset_name)
            score = p.get('retrieval_score', 0)
            rank = p.get('retrieval_rank', 0)
            is_gold = is_gold_passage(p, dataset_name)
            marker = "✓" if is_gold else "✗"
            print(f"    [{rank}] {marker} {title[:45]:45s} (score: {score:.4f})")
        
        print(f"\n  Generating answer with {len(window_passages)} passages...")
        answer, conf, reasoning = generate_answer_general(
            question, window_passages, dataset_name
        )
        
        print(f"  Answer: {answer}")
        print(f"  Confidence: {conf:.2f}")
        print(f"  Reasoning: {reasoning[:100]}...")
        
        all_attempts.append({
            'window': label,
            'answer': answer,
            'confidence': conf,
            'passages': window_passages
        })
        
        accumulated.extend(window_passages)
        
        if conf >= 0.7:
            print(f"  ✅ SUFFICIENT confidence!")
            break
        else:
            print(f"  ⚠ Low confidence, trying next window...")
    
    # Get best answer
    best = max(all_attempts, key=lambda x: x['confidence'])
    return best['answer'], best['confidence'], best.get('reasoning', ''), accumulated, all_attempts

# ==================== 3. TEST SINGLE SAMPLE WITH DETAIL ====================
def test_sample_verbose(sample, sample_id, dataset_name):
    """Test single sample with FULL detailed output"""
    
    print(f"\n{'='*100}")
    print(f"SAMPLE {sample_id}")
    print(f"{'='*100}")
    
    question = get_question(sample, dataset_name)
    gold_answer = get_answer(sample, dataset_name)
    all_passages = get_contexts(sample, dataset_name)
    
    print(f"Main Question: {question}")
    print(f"Gold Answer: {gold_answer}")
    print(f"Total passages available: {len(all_passages)}")
    
    # Decompose
    print(f"\n{'─'*80}")
    print(f"STEP 1: Question Decomposition")
    print(f"{'─'*80}")
    
    sub_questions = decompose_question(question, dataset_name)
    
    print(f"✓ Decomposed into {len(sub_questions)} stages:")
    for sq in sub_questions:
        print(f"  Stage {sq['stage']}: {sq['question']}")
    
    # Process stages
    stage_results = []
    previous_answers = {}
    
    for stage_idx, sq in enumerate(sub_questions):
        stage_num = sq['stage']
        stage_question = sq['question']
        
        # Replace placeholders
        for prev_stage, prev_answer in previous_answers.items():
            stage_question = stage_question.replace(f"[ANSWER_STAGE_{prev_stage}]", prev_answer)
        
        print(f"\n{'='*80}")
        print(f"STAGE {stage_num}")
        print(f"{'='*80}")
        print(f"Current Question: {stage_question}")
        
        if stage_idx == 0:
            # Stage 1: Smart progressive with verbose
            answer, conf, reasoning, used_passages, attempts = smart_progressive_stage1_verbose(
                stage_question, all_passages, dataset_name, sample_id
            )
            
            print(f"\n  {'─'*60}")
            print(f"  STAGE {stage_num} SUMMARY")
            print(f"  {'─'*60}")
            print(f"  Final Answer: {answer}")
            print(f"  Confidence: {conf:.2f}")
            print(f"  Windows tried: {len(attempts)}")
            print(f"  Total passages used: {len(used_passages)}")
            
        else:
            # Stage 2+: Simple Q2P
            print(f"\n{'─'*80}")
            print(f"🔍 RETRIEVAL: Question-to-Passage (Q2P)")
            print(f"{'─'*80}")
            
            retrieved = retrieve_passages_dense(stage_question, all_passages, dataset_name, k=3)
            
            print(f"  Retrieving top-3 passages...")
            for p in retrieved:
                title = get_context_title(p, dataset_name)
                score = p.get('retrieval_score', 0)
                rank = p.get('retrieval_rank', 0)
                is_gold = is_gold_passage(p, dataset_name)
                marker = "✓" if is_gold else "✗"
                print(f"    [{rank}] {marker} {title[:45]:45s} (score: {score:.4f})")
            
            print(f"\n  Generating answer with K=3...")
            answer, conf, reasoning = generate_answer_general(stage_question, retrieved, dataset_name)
            
            print(f"  Answer: {answer}")
            print(f"  Confidence: {conf:.2f}")
            print(f"  Reasoning: {reasoning[:100]}...")
            
            used_passages = retrieved
        
        stage_results.append({
            'stage': stage_num,
            'question': stage_question,
            'answer': answer,
            'confidence': conf,
            'passages': used_passages
        })
        
        previous_answers[stage_num] = answer
    
    # Final synthesis
    print(f"\n{'='*80}")
    print(f"FINAL ANSWER SYNTHESIS")
    print(f"{'='*80}")
    
    synthesis_prompt = f"Main question: {question}\n\nStage answers:\n"
    for s in stage_results:
        synthesis_prompt += f"Stage {s['stage']}: {s['answer']}\n"
    synthesis_prompt += "\nProvide final answer (max 5 words):"
    
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
    
    print(f"Synthesized final answer: {final_answer}")
    
    # Evaluate
    print(f"\n{'='*80}")
    print(f"FINAL RESULT")
    print(f"{'='*80}")
    
    em = exact_match(final_answer, gold_answer)
    f1 = f1_score(final_answer, gold_answer)
    
    print(f"Final Answer: {final_answer}")
    print(f"Gold Answer: {gold_answer}")
    
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
        judge_prompt = f"Q: {question}\nGold: {gold_answer}\nPred: {final_answer}\n\nCorrect? JSON: {{\"judgment\": \"CORRECT/INCORRECT\"}}"
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
    
    total_passages = len(set(
        get_context_title(p, dataset_name)
        for s in stage_results
        for p in s['passages']
    ))
    
    print(f"\nMetrics:")
    print(f"  EM: {em}")
    print(f"  F1: {f1:.3f}")
    print(f"  BERTScore F1: {bertscore_f1:.3f}")
    print(f"  LLM Judge: {llm_judgment}")
    print(f"  Total unique passages used: {total_passages}/{len(all_passages)}")
    print(f"  Number of stages: {len(stage_results)}")
    
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
        'num_stages': len(stage_results)
    }

# ==================== 4. RUN 10 SAMPLES ====================
start_time = time.time()

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:10]
all_results = []

for i, sample in enumerate(hotpot_samples, 1):
    try:
        result = test_sample_verbose(sample, i, 'hotpotqa')
        all_results.append(result)
    except Exception as e:
        print(f"\n⚠ Error on sample {i}: {e}")
        all_results.append({'sample_id': i, 'error': str(e), 'em': 0, 'f1': 0})

elapsed_time = time.time() - start_time

# ==================== 5. SUMMARY ====================
print(f"\n{'='*100}")
print("SUMMARY: 10 HOTPOTQA SAMPLES")
print(f"{'='*100}")

print(f"\nResults:")
for r in all_results:
    if 'error' in r:
        print(f"❌ Sample {r['sample_id']:2d}: ERROR - {r['error'][:50]}")
    else:
        status = "✅" if r['em'] == 1 or r['llm_judgment'] == 'CORRECT' else "❌"
        print(f"{status} Sample {r['sample_id']:2d}:")
        print(f"   Q: {r['question'][:60]}")
        print(f"   Gold: {r['gold_answer']}")
        print(f"   Pred: {r['predicted_answer']}")
        print(f"   Metrics: EM={r['em']} F1={r['f1']:.2f} BERT={r['bertscore_f1']:.2f} Judge={r['llm_judgment']}")
        print()

valid_results = [r for r in all_results if 'error' not in r]

if valid_results:
    avg_em = np.mean([r['em'] for r in valid_results])
    avg_f1 = np.mean([r['f1'] for r in valid_results])
    avg_bert = np.mean([r['bertscore_f1'] for r in valid_results])
    llm_correct = sum(1 for r in valid_results if r['llm_judgment'] == 'CORRECT')
    avg_passages = np.mean([r['total_passages'] for r in valid_results])
    
    print(f"{'─'*80}")
    print("AGGREGATE METRICS")
    print(f"{'─'*80}")
    print(f"Samples: {len(valid_results)}/10")
    print(f"EM: {avg_em*100:.1f}%")
    print(f"F1: {avg_f1:.3f}")
    print(f"BERTScore: {avg_bert:.3f}")
    print(f"LLM Judge: {llm_correct/len(valid_results)*100:.1f}%")
    print(f"Avg passages: {avg_passages:.1f}/10")
    print(f"Time: {elapsed_time:.1f}s")
    
    print(f"\n{'─'*80}")
    print("vs BASELINE")
    print(f"{'─'*80}")
    print(f"K=5 baseline: 34% | Ours: {avg_em*100:.1f}% | Δ: {(avg_em*100-34):+.1f}pp")
    print(f"K=10 baseline: 36% | Ours: {avg_em*100:.1f}% | Δ: {(avg_em*100-36):+.1f}pp")

print(f"\n{'='*100}")
print("✓ TEST COMPLETE!")
print(f"{'='*100}")
```

Sekarang output akan **super detailed** per sample:
- ✅ Stage-by-stage breakdown
- ✅ Window-by-window retrieval attempts
- ✅ Passage titles + scores + gold markers
- ✅ Answer + confidence + reasoning per stage
- ✅ Full metrics at the end

Run! 🚀