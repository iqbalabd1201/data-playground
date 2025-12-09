Oke! Debug **sample 6 only** dengan output **semua prompts dalam JSON**:

```python
# ==================== DEBUG SAMPLE 6: EXPORT ALL PROMPTS TO JSON ====================
print("="*100)
print("DEBUG: SAMPLE 6 - EXPORT ALL PROMPTS")
print("="*100)

import json

# Get sample 6
sample = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[5]  # Index 5 = Sample 6
sample_id = 6

question = get_question(sample, 'hotpotqa')
gold_answer = get_answer(sample, 'hotpotqa')
all_passages = get_contexts(sample, 'hotpotqa')

print(f"\n{'='*100}")
print("SAMPLE INFO")
print(f"{'='*100}")
print(f"Sample ID: {sample_id}")
print(f"Question: {question}")
print(f"Gold Answer: {gold_answer}")
print(f"Total passages: {len(all_passages)}")

# Show all passages
print(f"\n{'─'*80}")
print("ALL PASSAGES")
print(f"{'─'*80}")
for i, p in enumerate(all_passages, 1):
    title = get_context_title(p, 'hotpotqa')
    text = get_context_text(p, 'hotpotqa')
    print(f"[{i}] {title}")
    print(f"    {text[:150]}...")

# Store all prompts
all_prompts = []
debug_log = {
    'sample_id': sample_id,
    'question': question,
    'gold_answer': gold_answer,
    'total_passages': len(all_passages),
    'passages': [
        {
            'id': i,
            'title': get_context_title(p, 'hotpotqa'),
            'text': get_context_text(p, 'hotpotqa'),
            'is_gold': is_gold_passage(p, 'hotpotqa')
        }
        for i, p in enumerate(all_passages, 1)
    ]
}

try:
    # STEP 1: Decomposition
    print(f"\n{'='*100}")
    print("STEP 1: DECOMPOSITION")
    print(f"{'='*100}")
    
    decomp_prompt = f"""Decompose this multi-hop question into sub-questions.

Question: {question}

For comparison questions (e.g., "which was founded earlier"), include stages to find comparable attributes.

Return JSON:
{{
  "sub_questions": [
    {{"stage": 1, "question": "...", "purpose": "..."}},
    {{"stage": 2, "question": "...", "purpose": "..."}}
  ]
}}

JSON:"""
    
    print("\n[DECOMPOSITION PROMPT]")
    print(decomp_prompt)
    
    all_prompts.append({
        'prompt_id': 1,
        'type': 'decomposition',
        'stage': 0,
        'prompt': decomp_prompt
    })
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Decompose questions into necessary sub-questions."},
            {"role": "user", "content": decomp_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    decomp_result = json.loads(response.choices[0].message.content)
    sub_questions = decomp_result.get('sub_questions', [])
    
    print(f"\n[DECOMPOSITION RESULT]")
    print(json.dumps(decomp_result, indent=2))
    
    all_prompts[-1]['response'] = decomp_result
    
    debug_log['decomposition'] = {
        'sub_questions': sub_questions,
        'prompt': decomp_prompt,
        'response': decomp_result
    }
    
    # STEP 2: Process stages
    stage_results = []
    previous_answers = {}
    prompt_counter = 2
    
    for stage_idx, sq in enumerate(sub_questions):
        stage_num = sq['stage']
        stage_question = sq['question']
        
        # Replace placeholders
        original_question = stage_question
        for prev_stage, prev_answer in previous_answers.items():
            stage_question = stage_question.replace(f"[ANSWER_STAGE_{prev_stage}]", prev_answer)
        
        print(f"\n{'='*100}")
        print(f"STAGE {stage_num}")
        print(f"{'='*100}")
        print(f"Original: {original_question}")
        if original_question != stage_question:
            print(f"Substituted: {stage_question}")
        
        stage_log = {
            'stage': stage_num,
            'original_question': original_question,
            'substituted_question': stage_question,
            'prompts': []
        }
        
        if stage_idx == 0:
            # Stage 1: Smart progressive
            print(f"\n{'─'*80}")
            print("METHOD: SMART PROGRESSIVE")
            print(f"{'─'*80}")
            
            all_ranked = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=len(all_passages))
            
            print(f"\nFull ranking:")
            for i, p in enumerate(all_ranked[:5], 1):
                title = get_context_title(p, 'hotpotqa')
                score = p.get('retrieval_score', 0)
                marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
                print(f"  [{i}] {marker} {title[:45]:45s} ({score:.4f})")
            
            windows = [(0, 3, "Rank 1-3"), (3, 6, "Rank 4-6"), (6, 9, "Rank 7-9")]
            attempts = []
            accumulated = []
            
            for window_idx, (start, end, label) in enumerate(windows, 1):
                print(f"\n{'─'*60}")
                print(f"WINDOW: {label}")
                print(f"{'─'*60}")
                
                window_passages = all_ranked[start:end]
                
                print(f"Passages:")
                for p in window_passages:
                    title = get_context_title(p, 'hotpotqa')
                    rank = p.get('retrieval_rank', 0)
                    marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
                    print(f"  [{rank}] {marker} {title[:45]}")
                
                # Build prompt
                context_parts = []
                for i, ctx in enumerate(window_passages, 1):
                    title = get_context_title(ctx, 'hotpotqa')
                    text = get_context_text(ctx, 'hotpotqa')
                    context_parts.append(f"Passage {i} ({title}):\n{text}")
                
                context_str = "\n\n".join(context_parts)
                
                gen_prompt = f"""Answer the question based on the passages.

QUESTION: {stage_question}

PASSAGES:
{context_str}

RULES:
1. Answer from passages only
2. Use logical inference when clearly implied
3. Short answer (max 10 words)
4. If no info: "Tidak ada informasi"

JSON:
{{
  "answer": "...",
  "confidence": 0-100,
  "reasoning": "..."
}}"""
                
                print(f"\n[GENERATION PROMPT]")
                print(gen_prompt)
                
                all_prompts.append({
                    'prompt_id': prompt_counter,
                    'type': 'generation',
                    'stage': stage_num,
                    'window': label,
                    'prompt': gen_prompt
                })
                
                stage_log['prompts'].append({
                    'window': label,
                    'passages_used': [get_context_title(p, 'hotpotqa') for p in window_passages],
                    'prompt': gen_prompt
                })
                
                prompt_counter += 1
                
                # Generate
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Extract answers from passages."},
                        {"role": "user", "content": gen_prompt}
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
                
                print(f"\n[GENERATION RESULT]")
                print(f"Answer: {answer}")
                print(f"Confidence: {confidence:.2f}")
                print(f"Reasoning: {reasoning}")
                
                all_prompts[-1]['response'] = result
                stage_log['prompts'][-1]['response'] = result
                
                attempts.append({
                    'window': label,
                    'answer': answer,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'passages': window_passages
                })
                
                accumulated.extend(window_passages)
                
                if confidence >= 0.7:
                    print(f"\n✅ SUFFICIENT!")
                    break
                else:
                    print(f"\n⚠ Low confidence")
            
            best = max(attempts, key=lambda x: x['confidence'])
            answer = best['answer']
            confidence = best['confidence']
            used_passages = accumulated
            
            stage_log['best_answer'] = answer
            stage_log['best_confidence'] = confidence
            stage_log['attempts'] = [
                {
                    'window': a['window'],
                    'answer': a['answer'],
                    'confidence': a['confidence']
                }
                for a in attempts
            ]
            
        else:
            # Stage 2+: Q2P with context
            print(f"\n{'─'*80}")
            print("METHOD: Q2P (with previous context)")
            print(f"{'─'*80}")
            
            retrieved = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=3)
            
            print(f"\nRetrieved:")
            for p in retrieved:
                title = get_context_title(p, 'hotpotqa')
                rank = p.get('retrieval_rank', 0)
                marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
                print(f"  [{rank}] {marker} {title[:45]}")
            
            # Build prompt with context
            context_parts = []
            for i, ctx in enumerate(retrieved, 1):
                title = get_context_title(ctx, 'hotpotqa')
                text = get_context_text(ctx, 'hotpotqa')
                context_parts.append(f"Passage {i} ({title}):\n{text}")
            
            context_str = "\n\n".join(context_parts)
            
            # Include previous stage results
            prev_context = ""
            if previous_answers:
                prev_context = "\nPREVIOUS STAGE RESULTS:\n"
                for s in stage_results:
                    prev_context += f"  Stage {s['stage']}: {s['answer']}\n"
            
            gen_prompt = f"""Answer the question based on the passages.

MAIN QUESTION: {question}
{prev_context}
CURRENT STAGE QUESTION: {stage_question}

PASSAGES:
{context_str}

RULES:
1. Answer from passages only
2. Use logical inference when clearly implied
3. Use previous stage answers if relevant
4. Short answer (max 10 words)
5. If no info: "Tidak ada informasi"

JSON:
{{
  "answer": "...",
  "confidence": 0-100,
  "reasoning": "..."
}}"""
            
            print(f"\n[GENERATION PROMPT]")
            print(gen_prompt)
            
            all_prompts.append({
                'prompt_id': prompt_counter,
                'type': 'generation',
                'stage': stage_num,
                'prompt': gen_prompt
            })
            
            stage_log['prompts'].append({
                'passages_used': [get_context_title(p, 'hotpotqa') for p in retrieved],
                'prompt': gen_prompt
            })
            
            prompt_counter += 1
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Extract answers from passages. Use previous context."},
                    {"role": "user", "content": gen_prompt}
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
            
            print(f"\n[GENERATION RESULT]")
            print(f"Answer: {answer}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Reasoning: {reasoning}")
            
            all_prompts[-1]['response'] = result
            stage_log['prompts'][-1]['response'] = result
            
            used_passages = retrieved
            
            stage_log['answer'] = answer
            stage_log['confidence'] = confidence
        
        stage_results.append({
            'stage': stage_num,
            'question': stage_question,
            'answer': answer,
            'confidence': confidence,
            'passages': used_passages
        })
        
        previous_answers[stage_num] = answer
        debug_log.setdefault('stages', []).append(stage_log)
    
    # STEP 3: Synthesis
    print(f"\n{'='*100}")
    print("SYNTHESIS")
    print(f"{'='*100}")
    
    synthesis_prompt = f"""Main question: {question}

Stage answers:
"""
    for s in stage_results:
        synthesis_prompt += f"Stage {s['stage']}: {s['answer']}\n"
    
    synthesis_prompt += """
Based on the stage answers, provide the final answer to the main question.
Keep it SHORT (max 5 words).

Answer:"""
    
    print(f"\n[SYNTHESIS PROMPT]")
    print(synthesis_prompt)
    
    all_prompts.append({
        'prompt_id': prompt_counter,
        'type': 'synthesis',
        'prompt': synthesis_prompt
    })
    
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
    
    print(f"\n[SYNTHESIS RESULT]")
    print(f"Final answer: {final_answer}")
    
    all_prompts[-1]['response'] = {'final_answer': final_answer}
    
    debug_log['synthesis'] = {
        'prompt': synthesis_prompt,
        'final_answer': final_answer
    }
    
    # Evaluation
    print(f"\n{'='*100}")
    print("EVALUATION")
    print(f"{'='*100}")
    
    em = exact_match(final_answer, gold_answer)
    f1 = f1_score(final_answer, gold_answer)
    
    print(f"\nPredicted: {final_answer}")
    print(f"Gold: {gold_answer}")
    print(f"EM: {em}")
    print(f"F1: {f1:.3f}")
    
    status = "✅" if em == 1 else "❌"
    print(f"\n{status} Result: {'CORRECT' if em == 1 else 'INCORRECT'}")
    
    debug_log['evaluation'] = {
        'predicted_answer': final_answer,
        'gold_answer': gold_answer,
        'em': em,
        'f1': f1,
        'correct': em == 1
    }
    
    debug_log['all_prompts'] = all_prompts

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    debug_log['error'] = str(e)

# Save to JSON
print(f"\n{'='*100}")
print("SAVING TO JSON")
print(f"{'='*100}")

output_dir = os.path.join(LOG_DIR, 'debug_sample6')
os.makedirs(output_dir, exist_ok=True)

# Save full debug log
debug_path = os.path.join(output_dir, 'sample6_full_debug.json')
with open(debug_path, 'w', encoding='utf-8') as f:
    json.dump(debug_log, f, indent=2, ensure_ascii=False)
print(f"✓ Full debug log: {debug_path}")

# Save prompts only
prompts_path = os.path.join(output_dir, 'sample6_prompts_only.json')
with open(prompts_path, 'w', encoding='utf-8') as f:
    json.dump({'prompts': all_prompts}, f, indent=2, ensure_ascii=False)
print(f"✓ Prompts only: {prompts_path}")

print(f"\n{'='*100}")
print("✓ DEBUG COMPLETE - SAMPLE 6")
print(f"{'='*100}")
print(f"\nTotal prompts generated: {len(all_prompts)}")
print(f"Files saved to: {output_dir}")
```

Run ini untuk debug **sample 6** dengan:
- ✅ **All prompts** (decomposition, generation per window, synthesis)
- ✅ **All responses** per prompt
- ✅ **Full passages** content
- ✅ **Stage-by-stage breakdown**
- ✅ **Export to JSON** for inspection

🔍