Ah iya! **Pipeline salah** - LLM tetap jawab "Tidak ada informasi" padahal sudah ada context "Peggy Seeger" dari Stage 1. 

**Root problem:** Prompt masih **kurang jelas** bahwa harus cari info tentang **Peggy Seeger** (hasil Stage 1), bukan James Henry Miller.

**Fix: Reformulate Stage 2 question dengan jawaban Stage 1:**

```python
# ==================== FINAL FIX: REFORMULATE QUESTION WITH STAGE 1 ANSWER ====================
print("="*100)
print("FINAL FIX: REFORMULATE STAGE QUESTIONS WITH PREVIOUS ANSWERS")
print("="*100)

def reformulate_question_with_context(stage_question, previous_answers):
    """
    Reformulate stage question by replacing placeholders AND making it clearer
    
    Example:
    - Original: "Apa kewarganegaraan [ANSWER_STAGE_1]?"
    - Stage 1 answer: "Peggy Seeger"
    - Reformulated: "Apa kewarganegaraan Peggy Seeger?"
    """
    reformulated = stage_question
    
    # Replace all placeholders
    for stage_num, answer in previous_answers.items():
        placeholder = f"[ANSWER_STAGE_{stage_num}]"
        if placeholder in reformulated:
            reformulated = reformulated.replace(placeholder, answer)
    
    return reformulated

def generate_answer_final(stage_question, contexts, dataset_name, 
                          main_question=None, previous_stage_results=None):
    """
    Generate answer with CLEAR context about what we're looking for
    """
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        title = get_context_title(ctx, dataset_name)
        text = get_context_text(ctx, dataset_name)
        context_parts.append(f"Passage {i} ({title}):\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    # Build prompt
    prompt_parts = []
    
    if main_question:
        prompt_parts.append(f"MAIN QUESTION: {main_question}")
    
    if previous_stage_results:
        prompt_parts.append("\nPREVIOUS STAGE RESULTS:")
        for prev in previous_stage_results:
            prompt_parts.append(f"  Stage {prev['stage']}: {prev['answer']}")
    
    prompt_parts.append(f"\nCURRENT QUESTION: {stage_question}")
    
    prompt_parts.append(f"\nPASSAGES:")
    prompt_parts.append(context_str)
    
    prompt_parts.append("""
INSTRUCTIONS:
1. Answer the CURRENT QUESTION based on the passages
2. If previous stage results mention a person/entity, look for information about that person/entity in the passages
3. Use logical inference when clearly implied
4. Short answer (max 10 words)
5. If truly no relevant info: "Tidak ada informasi"

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
                {"role": "system", "content": "Answer questions from passages. Connect information across stages."},
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
        return "", 0.0, str(e), ""

# ==================== TEST SAMPLE 6 WITH FIXED PIPELINE ====================
print("\n" + "="*100)
print("TEST: SAMPLE 6 WITH FIXED PIPELINE")
print("="*100)

sample = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[5]

question = get_question(sample, 'hotpotqa')
gold_answer = get_answer(sample, 'hotpotqa')
all_passages = get_contexts(sample, 'hotpotqa')

print(f"Question: {question}")
print(f"Gold: {gold_answer}")

# Decompose
sub_questions = decompose_question(question, 'hotpotqa')

print(f"\nDecomposition:")
for sq in sub_questions:
    print(f"  Stage {sq['stage']}: {sq['question']}")

# Process stages
stage_results = []
previous_answers = {}

for stage_idx, sq in enumerate(sub_questions):
    stage_num = sq['stage']
    stage_question = sq['question']
    
    # Reformulate with previous answers
    stage_question = reformulate_question_with_context(stage_question, previous_answers)
    
    print(f"\n{'='*80}")
    print(f"STAGE {stage_num}")
    print(f"{'='*80}")
    print(f"Question (reformulated): {stage_question}")
    
    if stage_idx == 0:
        # Stage 1
        print("\nMethod: Smart Progressive")
        
        all_ranked = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=len(all_passages))
        
        windows = [(0, 3, "1-3"), (3, 6, "4-6"), (6, 9, "7-9")]
        attempts = []
        accumulated = []
        
        for start, end, label in windows:
            window_passages = all_ranked[start:end]
            
            print(f"\n  Window {label}:")
            for p in window_passages:
                title = get_context_title(p, 'hotpotqa')[:40]
                print(f"    {title}")
            
            answer, conf, reasoning, prompt = generate_answer_final(
                stage_question, window_passages, 'hotpotqa', 
                main_question=question, previous_stage_results=None
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
        # Stage 2+
        print(f"\nMethod: Q2P with context")
        print(f"Previous answers: {previous_answers}")
        
        # IMPORTANT: Retrieve based on REFORMULATED question (e.g., "Apa kewarganegaraan Peggy Seeger?")
        retrieved = retrieve_passages_dense(stage_question, all_passages, 'hotpotqa', k=5)  # Use K=5 for better coverage
        
        print(f"\nRetrieved (based on reformulated question):")
        for p in retrieved:
            title = get_context_title(p, 'hotpotqa')[:45]
            score = p.get('retrieval_score', 0)
            marker = "✓" if is_gold_passage(p, 'hotpotqa') else "✗"
            print(f"  {marker} {title} ({score:.4f})")
        
        answer, confidence, reasoning, prompt = generate_answer_final(
            stage_question, retrieved, 'hotpotqa',
            main_question=question, 
            previous_stage_results=stage_results
        )
        
        print(f"\n  → {answer} (conf: {confidence:.2f})")
        print(f"  Reasoning: {reasoning}")
        
        # Show prompt preview
        print(f"\n[PROMPT PREVIEW]")
        print(f"{'-'*60}")
        prompt_preview = prompt[:500]
        print(prompt_preview + "...")
        print(f"{'-'*60}")
        
        used_passages = retrieved
    
    stage_results.append({
        'stage': stage_num,
        'question': stage_question,
        'answer': answer,
        'confidence': confidence,
        'passages': used_passages
    })
    
    previous_answers[stage_num] = answer
    
    print(f"\nStage {stage_num} result: {answer}")

# Synthesis
print(f"\n{'='*80}")
print("SYNTHESIS")
print(f"{'='*80}")

synthesis_prompt = f"Q: {question}\n\nStages:\n"
for s in stage_results:
    synthesis_prompt += f"Stage {s['stage']}: {s['answer']}\n"
synthesis_prompt += "\nFinal answer (max 5 words):"

print(synthesis_prompt)

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

print(f"\nFinal: {final_answer}")

# Evaluate
em = exact_match(final_answer, gold_answer)
f1 = f1_score(final_answer, gold_answer)

print(f"\n{'='*80}")
print("RESULT")
print(f"{'='*80}")
print(f"Predicted: {final_answer}")
print(f"Gold: {gold_answer}")
print(f"EM: {em} | F1: {f1:.2f}")

status = "✅" if em == 1 else "❌"
print(f"\n{status} {'CORRECT!' if em == 1 else 'INCORRECT'}")

print(f"\n{'='*100}")
print("KEY IMPROVEMENTS IN THIS VERSION:")
print(f"{'='*100}")
print("1. ✅ Reformulate stage questions with previous answers")
print("   - Stage 2 now: 'Apa kewarganegaraan Peggy Seeger?'")
print("   - NOT: 'Apa kewarganegaraan [ANSWER_STAGE_1]?'")
print("2. ✅ Retrieve based on reformulated question (includes 'Peggy Seeger')")
print("3. ✅ Use K=5 for Stage 2+ to get better coverage")
print("4. ✅ Clear prompt: 'look for information about that person/entity'")
```

**Key fixes:**
1. ✅ **Reformulate question**: Replace `[ANSWER_STAGE_1]` → actual answer BEFORE retrieval
2. ✅ **Retrieve on reformulated**: Search "Apa kewarganegaraan Peggy Seeger?" not "[ANSWER_STAGE_1]"
3. ✅ **Increase K for Stage 2+**: Use K=5 instead of K=3 for better coverage
4. ✅ **Clearer prompt**: Tell LLM to look for info about person mentioned in previous stages

Run ini - seharusnya **Stage 2 berhasil** dapat "American"! 🚀