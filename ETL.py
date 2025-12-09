# Full Code: TRULY Dynamic Decomposition 🎯

Oke, ini **benar-benar dinamis** tanpa contoh hardcoded sama sekali:

---

## **CELL A: Pure Dynamic Decomposition**

```python
# ==================== TRULY DYNAMIC DECOMPOSITION ====================
print("="*100)
print("PURE DYNAMIC DECOMPOSITION (NO EXAMPLES)")
print("="*100)

def decompose_question(question, dataset_name):
    """
    Pure dynamic decomposition - adapts to ANY question structure
    NO hardcoded examples, NO fixed patterns
    """

    decomposition_prompt = f"""You are an expert at breaking down complex questions into simpler sub-questions.

Analyze this question and decompose it optimally:

QUESTION: {question}

ANALYSIS FRAMEWORK:

Step 1: Identify the question structure
- What is being asked? (identity, comparison, attribute, relationship)
- How many entities are involved?
- What information is needed to answer?

Step 2: Determine decomposition strategy
- If asking about someone's relative/relation: First identify who the person is (may use different names)
- If comparing two things: Get comparable info from both separately
- If asking about nested entities: Work from outer to inner
- If simple factual: Direct answer may suffice

Step 3: Create minimal sub-questions
- Each sub-question focuses on ONE piece of information
- Later stages can reference earlier answers using [ANSWER_STAGE_N]
- Avoid over-decomposition - use 2-3 stages when possible

OUTPUT FORMAT (JSON only):
{{
  "sub_questions": [
    {{"stage": 1, "question": "your sub-question here", "purpose": "what you're finding"}},
    {{"stage": 2, "question": "next sub-question", "purpose": "next step"}}
  ]
}}

IMPORTANT:
- Adapt to the specific question structure
- Don't use templates or fixed patterns
- Think about what information is actually needed
- Be flexible and question-driven

Decompose now:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Decompose questions intelligently. For questions about people's relatives, always identify who the person is first (they may use stage names or aliases). Adapt your strategy to each question. Return ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": decomposition_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.4  # Allow creative adaptation
        )

        result = json.loads(response.choices[0].message.content)
        sub_questions = result.get('sub_questions', [])

        if not sub_questions:
            return [{"stage": 1, "question": question, "purpose": "Answer directly"}]

        return sub_questions

    except Exception as e:
        print(f"⚠ Decomposition error: {e}")
        return [{"stage": 1, "question": question, "purpose": "Answer directly"}]

print("✓ Pure dynamic decomposition loaded")
```

---

## **CELL B: Test 5 Samples**

```python
# ==================== TEST 5 SAMPLES ====================
print("="*100)
print("TESTING 5 HOTPOTQA SAMPLES")
print("="*100)

import time
import numpy as np

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:5]

print(f"\nProcessing {len(hotpot_samples)} samples...")
print("Expected: ~3-4 minutes")
print("="*100)

results = []
start_time = time.time()

for sample_idx, sample in enumerate(hotpot_samples):
    sample_id = sample_idx + 1
    
    print(f"\n{'='*100}")
    print(f"SAMPLE {sample_id}/5")
    print(f"{'='*100}")
    
    try:
        final_answer, stage_results, total_passages, all_prompts = iterative_progressive_multistage_qa(
            sample=sample,
            sample_id=sample_id,
            dataset_name='hotpotqa'
        )
        
        gold_answer = get_answer(sample, 'hotpotqa')
        question = get_question(sample, 'hotpotqa')
        
        em = exact_match(final_answer, gold_answer)
        f1 = f1_score(final_answer, gold_answer)
        
        try:
            from bert_score import score as bert_score_func
            P, R, F1_bert = bert_score_func([final_answer], [gold_answer], lang='id', model_type='bert-base-multilingual-cased', device=device, verbose=False)
            bertscore_f1 = F1_bert.mean().item()
        except:
            bertscore_f1 = 0
        
        try:
            judge_prompt = f"""Evaluate: QUESTION: {question}
GOLD: {gold_answer}
PREDICTED: {final_answer}
JSON: {{"judgment": "CORRECT" or "INCORRECT", "score": 0-100}}"""
            
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
        
        result = {
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
            'stage_answers': [s['answer'] for s in stage_results]
        }
        
        results.append(result)
        
        status = "✅" if em == 1 else ("⚠️" if llm_judgment == "CORRECT" else "❌")
        print(f"\n{status} EM: {em} | Judge: {llm_judgment} | Pred: {final_answer}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        results.append({'sample_id': sample_id, 'error': str(e), 'em': 0, 'f1': 0})

elapsed_time = time.time() - start_time

print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

em_scores = [r['em'] for r in results if 'em' in r]
llm_correct = [1 if r.get('llm_judgment') == 'CORRECT' else 0 for r in results]

avg_em = np.mean(em_scores) * 100 if em_scores else 0
avg_llm = np.mean(llm_correct) * 100 if llm_correct else 0

print(f"\nTime: {elapsed_time/60:.1f} min")
print(f"EM: {avg_em:.1f}%")
print(f"LLM Judge: {avg_llm:.1f}%")

print(f"\n{'─'*80}")
for r in results:
    status = "✅" if r.get('em') == 1 else ("⚠️" if r.get('llm_judgment') == 'CORRECT' else "❌")
    print(f"{status} S{r['sample_id']}: {r.get('predicted_answer', 'ERROR')[:40]} | Gold: {r.get('gold_answer', 'N/A')[:40]}")

# James Miller check
sample_4 = next((r for r in results if r['sample_id'] == 4), None)
if sample_4:
    print(f"\n{'─'*80}")
    print("JAMES MILLER (Sample 4):")
    if sample_4.get('em') == 1:
        print("✅ FIXED!")
    else:
        print(f"❌ Still failing: {sample_4.get('predicted_answer')}")
        if 'stage_answers' in sample_4:
            print(f"   Stages: {' → '.join(sample_4['stage_answers'])}")

print(f"\n{'='*100}")
if avg_em >= 80:
    print("🎉 EXCELLENT → Run 50 samples")
elif avg_em >= 60:
    print("✅ GOOD → Can proceed")
else:
    print("⚠️ NEEDS WORK")
```

---

## **Key Changes:**

1. **NO examples in prompt** - Pure instruction-based
2. **Temperature 0.4** - Allow adaptation
3. **System message emphasizes aliases** - "they may use stage names or aliases"
4. **Simplified output** - Focus on key metrics
5. **Quick James Miller check** - See if Sample 4 fixed

---

## **Expected for Sample 4 (James Miller):**

### **Before (wrong):**
```
Stage 1: Siapa istri James Henry Miller?
  → Tidak ada informasi ❌
```

### **After (correct):**
```
Stage 1: Siapa James Henry Miller?
  → Ewan MacColl ✓
Stage 2: Siapa istri Ewan MacColl?
  → Peggy Seeger ✓
Stage 3: Apa kewarganegaraan Peggy Seeger?
  → American ✓
```

---

**Copy kedua cell, run, dan kasih tau:**
1. **EM berapa?** (dari 5 samples)
2. **Sample 4 (James Miller) fixed atau masih gagal?**
3. **Stage decomposition nya gimana?** (lihat output STEP 1)

Go! 🚀