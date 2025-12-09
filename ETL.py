Oke! **Debug sample 10 super detail** + tampilkan semua prompts:

```python
# ==================== DEBUG SAMPLE 10 - SUPER DETAILED ====================
print("="*100)
print("DEBUG: SAMPLE 10 HOTPOTQA - FULL DETAILED BREAKDOWN")
print("="*100)

# Get sample 10
sample = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[9]  # Index 9 = Sample 10

question = get_question(sample, 'hotpotqa')
gold_answer = get_answer(sample, 'hotpotqa')
all_passages = get_contexts(sample, 'hotpotqa')

print(f"\n{'='*100}")
print("SAMPLE INFO")
print(f"{'='*100}")
print(f"Main Question: {question}")
print(f"Gold Answer: {gold_answer}")
print(f"Total passages: {len(all_passages)}")

# Show all passages
print(f"\n{'='*100}")
print("ALL AVAILABLE PASSAGES")
print(f"{'='*100}")

for i, p in enumerate(all_passages, 1):
    title = get_context_title(p, 'hotpotqa')
    text = get_context_text(p, 'hotpotqa')
    print(f"\n[{i}] {title}")
    print(f"    Text: {text[:200]}...")
    print(f"    Full length: {len(text)} chars")

# Decompose
print(f"\n{'='*100}")
print("STEP 1: QUESTION DECOMPOSITION")
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
print("─"*80)
print(decomp_prompt)
print("─"*80)

try:
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
    
    print("\n[DECOMPOSITION RESULT]")
    print(f"✓ Decomposed into {len(sub_questions)} stages:")
    for sq in sub_questions:
        print(f"  Stage {sq['stage']}: {sq['question']}")
        print(f"    Purpose: {sq.get('purpose', 'N/A')}")
except Exception as e:
    print(f"\n❌ Decomposition error: {e}")
    sub_questions = [{"stage": 1, "question": question}]

# Process each stage with FULL detail
stage_results = []
previous_answers = {}
all_prompts = []

for stage_idx, sq in enumerate(sub_questions):
    stage_num = sq['stage']
    stage_question = sq['question']
    
    # Replace placeholders
    original_stage_question = stage_question
    for prev_stage, prev_answer in previous_answers.items():
        stage_question = stage_question.replace(f"[ANSWER_STAGE_{prev_stage}]", prev_answer)
    
    print(f"\n{'='*100}")
    print(f"STAGE {stage_num}")
    print(f"{'='*100}")
    print(f"Original question: {original_stage_question}")
    if original_stage_question != stage_question:
        print(f"After substitution: {stage_question}")
    
    if stage_idx == 0:
        # Stage 1: Smart progressive with FULL detail
        print(f"\n{'─'*80}")
        print("SMART PROGRESSIVE RETRIEVAL")
        print(f"{'─'*80}")
        
        # Get full ranking
        all_ranked = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=len(all_passages))
        
        print(f"\n[FULL RANKING - Top 10]")
        for i, p in enumerate(all_ranked, 1):
            title = get_context_title(p, 'hotpotqa')
            score = p.get('retrieval_score', 0)
            marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
            print(f"  [{i}] {marker} {title[:50]:50s} (score: {score:.4f})")
        
        # Try windows
        windows = [(0, 3, "Rank 1-3"), (3, 6, "Rank 4-6"), (6, 9, "Rank 7-9")]
        
        attempts = []
        accumulated = []
        
        for window_idx, (start, end, label) in enumerate(windows, 1):
            print(f"\n{'─'*60}")
            print(f"WINDOW {window_idx}: {label}")
            print(f"{'─'*60}")
            
            window_passages = all_ranked[start:end]
            
            print(f"\nPassages in window:")
            for p in window_passages:
                title = get_context_title(p, 'hotpotqa')
                score = p.get('retrieval_score', 0)
                rank = p.get('retrieval_rank', 0)
                marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
                print(f"  [{rank}] {marker} {title[:50]:50s} ({score:.4f})")
            
            # Build prompt
            context_parts = []
            for i, ctx in enumerate(window_passages, 1):
                title = get_context_title(ctx, 'hotpotqa')
                text = get_context_text(ctx, 'hotpotqa')
                context_parts.append(f"Passage {i} ({title}):\n{text}")
            
            context_str = "\n\n".join(context_parts)
            
            gen_prompt = f"""Answer the question based on the passages.

PASSAGES:
{context_str}

QUESTION: {stage_question}

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
            
            print(f"\n[GENERATION PROMPT - Window {window_idx}]")
            print("─"*80)
            print(gen_prompt[:500] + "..." if len(gen_prompt) > 500 else gen_prompt)
            print("─"*80)
            
            all_prompts.append({
                'stage': stage_num,
                'window': label,
                'type': 'generation',
                'prompt': gen_prompt
            })
            
            # Generate
            try:
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
                
                print(f"\n[GENERATION RESULT - Window {window_idx}]")
                print(f"Answer: {answer}")
                print(f"Confidence: {confidence:.2f}")
                print(f"Reasoning: {reasoning}")
                
                attempts.append({
                    'window': label,
                    'answer': answer,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'passages': window_passages
                })
                
                accumulated.extend(window_passages)
                
                if confidence >= 0.7:
                    print(f"\n✅ SUFFICIENT confidence! Stopping.")
                    break
                else:
                    print(f"\n⚠ Low confidence ({confidence:.2f} < 0.7), trying next window...")
                
            except Exception as e:
                print(f"\n❌ Generation error: {e}")
                attempts.append({
                    'window': label,
                    'answer': '',
                    'confidence': 0,
                    'reasoning': str(e),
                    'passages': window_passages
                })
        
        # Pick best
        best = max(attempts, key=lambda x: x['confidence'])
        answer = best['answer']
        confidence = best['confidence']
        reasoning = best['reasoning']
        used_passages = accumulated
        
        print(f"\n{'─'*60}")
        print(f"STAGE {stage_num} FINAL RESULT")
        print(f"{'─'*60}")
        print(f"Best answer: {answer}")
        print(f"Best confidence: {confidence:.2f}")
        print(f"From window: {best['window']}")
        print(f"Total passages tried: {len(accumulated)}")
        
    else:
        # Stage 2+: Q2P
        print(f"\n{'─'*80}")
        print("RETRIEVAL: Question-to-Passage (Q2P)")
        print(f"{'─'*80}")
        
        retrieved = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=3)
        
        print(f"\nTop-3 passages:")
        for p in retrieved:
            title = get_context_title(p, 'hotpotqa')
            score = p.get('retrieval_score', 0)
            rank = p.get('retrieval_rank', 0)
            marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
            print(f"  [{rank}] {marker} {title[:50]:50s} ({score:.4f})")
        
        # Build prompt
        context_parts = []
        for i, ctx in enumerate(retrieved, 1):
            title = get_context_title(ctx, 'hotpotqa')
            text = get_context_text(ctx, 'hotpotqa')
            context_parts.append(f"Passage {i} ({title}):\n{text}")
        
        context_str = "\n\n".join(context_parts)
        
        gen_prompt = f"""Answer the question based on the passages.

PASSAGES:
{context_str}

QUESTION: {stage_question}

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
        print("─"*80)
        print(gen_prompt[:500] + "..." if len(gen_prompt) > 500 else gen_prompt)
        print("─"*80)
        
        all_prompts.append({
            'stage': stage_num,
            'type': 'generation',
            'prompt': gen_prompt
        })
        
        try:
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
            
            used_passages = retrieved
            
        except Exception as e:
            print(f"\n❌ Generation error: {e}")
            answer = ""
            confidence = 0
            reasoning = str(e)
            used_passages = retrieved
    
    stage_results.append({
        'stage': stage_num,
        'question': stage_question,
        'answer': answer,
        'confidence': confidence,
        'reasoning': reasoning,
        'passages': used_passages
    })
    
    previous_answers[stage_num] = answer

# Final synthesis
print(f"\n{'='*100}")
print("FINAL SYNTHESIS")
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

print("\n[SYNTHESIS PROMPT]")
print("─"*80)
print(synthesis_prompt)
print("─"*80)

all_prompts.append({
    'stage': 'synthesis',
    'type': 'synthesis',
    'prompt': synthesis_prompt
})

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
    
    print(f"\n[SYNTHESIS RESULT]")
    print(f"Final answer: {final_answer}")
    
except Exception as e:
    print(f"\n❌ Synthesis error: {e}")
    final_answer = stage_results[-1]['answer']

# Evaluation
print(f"\n{'='*100}")
print("EVALUATION")
print(f"{'='*100}")

em = exact_match(final_answer, gold_answer)
f1 = f1_score(final_answer, gold_answer)

print(f"\nPredicted: {final_answer}")
print(f"Gold: {gold_answer}")
print(f"\nEM: {em}")
print(f"F1: {f1:.3f}")

# Check if correct
is_correct = em == 1

print(f"\n{'✅' if is_correct else '❌'} Result: {'CORRECT' if is_correct else 'INCORRECT'}")

# Total passages used
total_passages = len(set(
    get_context_title(p, 'hotpotqa')
    for s in stage_results
    for p in s['passages']
))

print(f"\nTotal unique passages used: {total_passages}/{len(all_passages)}")
print(f"Number of stages: {len(stage_results)}")

# Summary of all prompts
print(f"\n{'='*100}")
print("PROMPT SUMMARY")
print(f"{'='*100}")

print(f"\nTotal prompts generated: {len(all_prompts)}")
for i, p in enumerate(all_prompts, 1):
    stage = p.get('stage', 'N/A')
    ptype = p.get('type', 'N/A')
    window = p.get('window', '')
    prompt_len = len(p['prompt'])
    
    label = f"Stage {stage}"
    if window:
        label += f" - {window}"
    label += f" ({ptype})"
    
    print(f"\nPrompt {i}: {label}")
    print(f"  Length: {prompt_len} chars")

# Detailed stage breakdown
print(f"\n{'='*100}")
print("STAGE-BY-STAGE BREAKDOWN")
print(f"{'='*100}")

for s in stage_results:
    print(f"\nStage {s['stage']}:")
    print(f"  Question: {s['question']}")
    print(f"  Answer: {s['answer']}")
    print(f"  Confidence: {s['confidence']:.2f}")
    print(f"  Reasoning: {s['reasoning'][:100]}...")
    print(f"  Passages used: {len(s['passages'])}")
    
    gold_count = sum(1 for p in s['passages'] if is_gold_passage(p, 'hotpotqa'))
    print(f"  Gold passages retrieved: {gold_count}")

# Final diagnostic
print(f"\n{'='*100}")
print("DIAGNOSTIC")
print(f"{'='*100}")

if not is_correct:
    print("\n❌ FAILED - Analyzing why...")
    
    print(f"\n1. Question decomposition:")
    print(f"   Stages: {len(sub_questions)}")
    for sq in sub_questions:
        print(f"   - Stage {sq['stage']}: {sq['question']}")
    
    print(f"\n2. Stage answers:")
    for s in stage_results:
        print(f"   Stage {s['stage']}: {s['answer']} (conf: {s['confidence']:.2f})")
    
    print(f"\n3. Final synthesis:")
    print(f"   Predicted: {final_answer}")
    print(f"   Gold: {gold_answer}")
    print(f"   Issue: {'Extra words' if len(final_answer.split()) > len(gold_answer.split()) else 'Wrong entity or format'}")
    
    print(f"\n4. Gold passage coverage:")
    total_gold = sum(1 for s in stage_results for p in s['passages'] if is_gold_passage(p, 'hotpotqa'))
    print(f"   Total gold passages retrieved: {total_gold}/{len([p for p in all_passages if is_gold_passage(p, 'hotpotqa')])}")

else:
    print("\n✅ SUCCESS!")
    print(f"\nKey factors:")
    print(f"  - Correct decomposition: {len(sub_questions)} stages")
    print(f"  - All stages answered correctly")
    print(f"  - Synthesis produced exact match")

print(f"\n{'='*100}")
print("✓ DEBUG COMPLETE")
print(f"{'='*100}")
```

Run ini untuk **super detailed debug** sample 10 dengan semua prompts!