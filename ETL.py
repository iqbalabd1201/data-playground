Ah betul! **Stage 2 harus pakai jawaban dari Stage 1** (Peggy Seeger) dalam prompt! Fix:

```python
# ==================== FIXED: USE PREVIOUS STAGE ANSWERS IN PROMPT ====================
print("="*100)
print("FIXED: MULTI-STAGE CONTEXT IN PROMPTS")
print("="*100)

def generate_answer_with_context(stage_question, contexts, dataset_name, 
                                  main_question=None, previous_stage_results=None):
    """
    Generate answer WITH multi-stage context
    """
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        title = get_context_title(ctx, dataset_name)
        text = get_context_text(ctx, dataset_name)
        context_parts.append(f"Passage {i} ({title}):\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    # Build prompt with previous stage context
    prompt_parts = []
    
    if main_question and previous_stage_results:
        prompt_parts.append(f"MAIN QUESTION: {main_question}")
        prompt_parts.append("\nPREVIOUS STAGE RESULTS:")
        for prev in previous_stage_results:
            prompt_parts.append(f"  Stage {prev['stage']}: {prev['answer']}")
        prompt_parts.append(f"\nCURRENT STAGE QUESTION: {stage_question}")
    else:
        prompt_parts.append(f"QUESTION: {stage_question}")
    
    prompt_parts.append(f"\nPASSAGES:")
    prompt_parts.append(context_str)
    
    prompt_parts.append("""
RULES:
1. Answer from passages only
2. Use logical inference when clearly implied
3. Use previous stage answers if relevant
4. Short answer (max 10 words)
5. If no info: "Tidak ada informasi"

JSON:
{
  "answer": "...",
  "confidence": 0-100,
  "reasoning": "..."
}""")
    
    full_prompt = "\n".join(prompt_parts)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract answers from passages. Use previous stage context when relevant."},
                {"role": "user", "content": full_prompt}
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
        
        return answer, confidence, reasoning, full_prompt
        
    except Exception as e:
        return "", 0.0, str(e), full_prompt

# ==================== COMPLETE TEST WITH MULTI-STAGE CONTEXT ====================
print("\n" + "="*100)
print("DEBUG: ALL 10 SAMPLES WITH MULTI-STAGE CONTEXT")
print("="*100)

import time

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:10]
all_results = []
start_time = time.time()

for sample_idx in range(10):
    sample = hotpot_samples[sample_idx]
    sample_id = sample_idx + 1
    
    print(f"\n{'='*100}")
    print(f"SAMPLE {sample_id}/10")
    print(f"{'='*100}")
    
    question = get_question(sample, 'hotpotqa')
    gold_answer = get_answer(sample, 'hotpotqa')
    all_passages = get_contexts(sample, 'hotpotqa')
    
    print(f"Question: {question}")
    print(f"Gold: {gold_answer}")
    
    try:
        # Decompose
        print(f"\n{'─'*80}")
        print("Decomposition")
        print(f"{'─'*80}")
        
        sub_questions = decompose_question(question, 'hotpotqa')
        
        print(f"✓ {len(sub_questions)} stages:")
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
            
            print(f"\n{'─'*80}")
            print(f"STAGE {stage_num}: {stage_question}")
            print(f"{'─'*80}")
            
            if stage_idx == 0:
                # Stage 1: Smart progressive (NO context needed)
                print("Method: Smart Progressive")
                
                all_ranked = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=len(all_passages))
                
                windows = [(0, 3, "1-3"), (3, 6, "4-6"), (6, 9, "7-9")]
                attempts = []
                accumulated = []
                
                for start, end, label in windows:
                    window_passages = all_ranked[start:end]
                    
                    print(f"\n  Window {label}:")
                    for p in window_passages:
                        title = get_context_title(p, 'hotpotqa')[:40]
                        rank = p.get('retrieval_rank', 0)
                        marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
                        print(f"    [{rank}] {marker} {title}")
                    
                    # Generate WITHOUT previous context (Stage 1)
                    answer, conf, reasoning, prompt = generate_answer_with_context(
                        stage_question, window_passages, 'hotpotqa', 
                        main_question=None, previous_stage_results=None
                    )
                    
                    print(f"  → {answer} (conf: {conf:.2f})")
                    
                    attempts.append({
                        'answer': answer,
                        'confidence': conf,
                        'passages': window_passages
                    })
                    
                    accumulated.extend(window_passages)
                    
                    if conf >= 0.7:
                        print(f"  ✅ Sufficient!")
                        break
                
                best = max(attempts, key=lambda x: x['confidence'])
                answer = best['answer']
                confidence = best['confidence']
                used_passages = accumulated
                
            else:
                # Stage 2+: Q2P WITH previous stage context
                print(f"Method: Q2P (with context from previous stages)")
                
                retrieved = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=3)
                
                print(f"\n  Retrieved:")
                for p in retrieved:
                    title = get_context_title(p, 'hotpotqa')[:40]
                    rank = p.get('retrieval_rank', 0)
                    marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
                    print(f"    [{rank}] {marker} {title}")
                
                # Generate WITH previous stage context
                answer, confidence, reasoning, prompt = generate_answer_with_context(
                    stage_question, retrieved, 'hotpotqa',
                    main_question=question, 
                    previous_stage_results=stage_results  # Pass all previous stages!
                )
                
                print(f"\n  PROMPT PREVIEW:")
                print(f"  {'-'*60}")
                prompt_preview = prompt.split("PASSAGES:")[0]
                print(f"  {prompt_preview[:300]}...")
                print(f"  {'-'*60}")
                
                print(f"\n  → {answer} (conf: {confidence:.2f})")
                
                used_passages = retrieved
            
            stage_results.append({
                'stage': stage_num,
                'question': stage_question,
                'answer': answer,
                'confidence': confidence,
                'passages': used_passages
            })
            
            previous_answers[stage_num] = answer
        
        # Synthesis
        print(f"\n{'─'*80}")
        print("SYNTHESIS")
        print(f"{'─'*80}")
        
        synthesis_prompt = f"Q: {question}\n\nStages:\n"
        for s in stage_results:
            synthesis_prompt += f"Stage {s['stage']}: {s['answer']}\n"
        synthesis_prompt += "\nFinal answer (max 5 words):"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Concise final answer. Max 5 words."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                max_tokens=15,
                temperature=0
            )
            final_answer = response.choices[0].message.content.strip().rstrip('.')
        except:
            final_answer = stage_results[-1]['answer']
        
        print(f"Final: {final_answer}")
        
        # Evaluate
        em = exact_match(final_answer, gold_answer)
        f1 = f1_score(final_answer, gold_answer)
        
        total_passages = len(set(
            get_context_title(p, 'hotpotqa')
            for s in stage_results
            for p in s['passages']
        ))
        
        status = "✅" if em == 1 else "❌"
        print(f"\n{status} EM: {em} | F1: {f1:.2f} | Passages: {total_passages}/10")
        
        all_results.append({
            'sample_id': sample_id,
            'question': question,
            'gold_answer': gold_answer,
            'predicted_answer': final_answer,
            'em': em,
            'f1': f1,
            'total_passages': total_passages,
            'num_stages': len(stage_results)
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        all_results.append({
            'sample_id': sample_id,
            'error': str(e),
            'em': 0,
            'f1': 0
        })

elapsed = time.time() - start_time

# Summary
print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

for r in all_results:
    if 'error' in r:
        print(f"❌ Sample {r['sample_id']:2d}: ERROR")
    else:
        status = "✅" if r['em'] == 1 else "❌"
        print(f"{status} Sample {r['sample_id']:2d}: {r['predicted_answer'][:40]:40s} | EM={r['em']} F1={r['f1']:.2f}")

valid = [r for r in all_results if 'error' not in r]

if valid:
    avg_em = np.mean([r['em'] for r in valid])
    avg_f1 = np.mean([r['f1'] for r in valid])
    avg_pass = np.mean([r['total_passages'] for r in valid])
    
    print(f"\n{'─'*80}")
    print(f"EM: {avg_em*100:.1f}% | F1: {avg_f1:.3f} | Avg passages: {avg_pass:.1f}/10")
    print(f"Time: {elapsed:.1f}s")
    print(f"Baseline K=5: 34% → Ours: {avg_em*100:.1f}% (Δ: {(avg_em*100-34):+.1f}pp)")

print(f"\n{'='*100}")
print("✓ COMPLETE WITH MULTI-STAGE CONTEXT!")
print(f"{'='*100}")
```

**Key fix:**
- ✅ **Stage 1**: No previous context (fresh start)
- ✅ **Stage 2+**: Include **all previous stage results** in prompt
- ✅ Prompt shows: `PREVIOUS STAGE RESULTS: Stage 1: Peggy Seeger`
- ✅ LLM can now use "Peggy Seeger" to find her nationality

Run! 🚀