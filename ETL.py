# Test 10 HotpotQA Samples 🚀

Copy-paste code ini sebagai **Cell baru** (setelah Cell 15):

```python
# ==================== QUICK TEST: 10 HOTPOTQA SAMPLES ====================
print("="*100)
print("QUICK TEST: 10 HOTPOTQA SAMPLES")
print("="*100)

import time
import numpy as np
from tqdm import tqdm

# Get 10 samples
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:10]

print(f"\nTesting {len(hotpot_samples)} HotpotQA samples...")
print(f"Expected time: ~5-7 minutes")
print("="*100)

# Storage
results = []
start_time = time.time()

# Process each sample
for sample_idx, sample in enumerate(tqdm(hotpot_samples, desc="Processing")):
    sample_id = sample_idx + 1
    
    try:
        # Run method
        final_answer, stage_results, total_passages, all_prompts = iterative_progressive_multistage_qa(
            sample=sample,
            sample_id=sample_id,
            dataset_name='hotpotqa'
        )
        
        # Get gold answer
        gold_answer = get_answer(sample, 'hotpotqa')
        question = get_question(sample, 'hotpotqa')
        
        # Compute metrics
        em = exact_match(final_answer, gold_answer)
        f1 = f1_score(final_answer, gold_answer)
        
        # BERTScore (optional, skip if slow)
        try:
            from bert_score import score as bert_score_func
            P, R, F1_bert = bert_score_func(
                [final_answer],
                [gold_answer],
                lang='id',
                model_type='bert-base-multilingual-cased',
                device=device,
                verbose=False
            )
            bertscore_f1 = F1_bert.mean().item()
        except:
            bertscore_f1 = 0
        
        # LLM Judge
        try:
            judge_prompt = f"""Evaluate if the predicted answer is correct.

QUESTION: {question}
GOLD ANSWER: {gold_answer}
PREDICTED ANSWER: {final_answer}

Consider CORRECT if semantically equivalent or contains correct information.

JSON:
{{
  "judgment": "CORRECT" or "INCORRECT",
  "score": 0-100
}}"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Evaluate answer correctness. Be lenient with format."},
                    {"role": "user", "content": judge_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            judge_result = json.loads(response.choices[0].message.content)
            llm_judgment = judge_result.get('judgment', 'INCORRECT')
            llm_score = judge_result.get('score', 0) / 100.0
        except:
            llm_judgment = "ERROR"
            llm_score = 0
        
        # Store result
        result = {
            'sample_id': sample_id,
            'question': question,
            'gold_answer': gold_answer,
            'predicted_answer': final_answer,
            'em': em,
            'f1': f1,
            'bertscore_f1': bertscore_f1,
            'llm_judgment': llm_judgment,
            'llm_score': llm_score,
            'total_passages': total_passages,
            'num_stages': len(stage_results),
            'stage_answers': [s['answer'] for s in stage_results],
            'retrieval_methods': [s['retrieval_method'] for s in stage_results]
        }
        
        results.append(result)
        
        # Print progress
        print(f"\n[{sample_id}/10] EM: {em} | F1: {f1:.2f} | Judge: {llm_judgment} | Answer: {final_answer[:50]}")
        
    except Exception as e:
        print(f"\n⚠ Error on sample {sample_id}: {e}")
        results.append({
            'sample_id': sample_id,
            'error': str(e),
            'em': 0,
            'f1': 0,
            'llm_judgment': 'ERROR'
        })

# Calculate statistics
elapsed_time = time.time() - start_time

print(f"\n{'='*100}")
print("RESULTS SUMMARY - 10 SAMPLES")
print(f"{'='*100}")

# Aggregate metrics
em_scores = [r['em'] for r in results if 'em' in r]
f1_scores = [r['f1'] for r in results if 'f1' in r]
bert_scores = [r['bertscore_f1'] for r in results if 'bertscore_f1' in r and r['bertscore_f1'] > 0]
llm_correct = [1 if r.get('llm_judgment') == 'CORRECT' else 0 for r in results]
passages = [r['total_passages'] for r in results if 'total_passages' in r]
stages = [r['num_stages'] for r in results if 'num_stages' in r]

print(f"\nTime elapsed: {elapsed_time/60:.2f} minutes")
print(f"Samples processed: {len(results)}")

print(f"\n{'─'*80}")
print("AGGREGATE METRICS")
print(f"{'─'*80}")

avg_em = np.mean(em_scores) * 100 if em_scores else 0
avg_f1 = np.mean(f1_scores) if f1_scores else 0
avg_bert = np.mean(bert_scores) if bert_scores else 0
avg_llm = np.mean(llm_correct) * 100 if llm_correct else 0
avg_passages = np.mean(passages) if passages else 0
avg_stages = np.mean(stages) if stages else 0

print(f"EM: {avg_em:.1f}%")
print(f"F1: {avg_f1:.3f}")
print(f"BERTScore F1: {avg_bert:.3f}")
print(f"LLM Judge Accuracy: {avg_llm:.1f}%")
print(f"Avg Passages: {avg_passages:.1f}")
print(f"Avg Stages: {avg_stages:.1f}")

# Comparison with baseline
print(f"\n{'─'*80}")
print("COMPARISON WITH BASELINE")
print(f"{'─'*80}")

baseline_k5 = 34
baseline_k10 = 36

print(f"Baseline K=5: {baseline_k5}%")
print(f"Baseline K=10: {baseline_k10}%")
print(f"Your method: {avg_em:.1f}%")
print(f"\nImprovement over K=5: {avg_em - baseline_k5:+.1f} percentage points")
print(f"Improvement over K=10: {avg_em - baseline_k10:+.1f} percentage points")

# Success assessment
if avg_em >= 70:
    status = "🎉 EXCELLENT!"
    emoji = "🎉"
elif avg_em >= 60:
    status = "✅ GOOD"
    emoji = "✅"
elif avg_em >= 50:
    status = "⚠️ OKAY"
    emoji = "⚠️"
else:
    status = "❌ NEEDS IMPROVEMENT"
    emoji = "❌"

print(f"\n{emoji} Status: {status}")

# Detailed breakdown
print(f"\n{'─'*80}")
print("DETAILED BREAKDOWN")
print(f"{'─'*80}")

print(f"\nSamples by result:")
correct_em = sum(1 for r in results if r.get('em') == 1)
correct_llm = sum(1 for r in results if r.get('llm_judgment') == 'CORRECT')
partial = sum(1 for r in results if r.get('em') == 0 and r.get('llm_judgment') == 'CORRECT')
incorrect = sum(1 for r in results if r.get('em') == 0 and r.get('llm_judgment') != 'CORRECT')

print(f"  Perfect (EM=1): {correct_em}/10 ({correct_em*10}%)")
print(f"  Semantically correct (LLM Judge): {correct_llm}/10 ({correct_llm*10}%)")
print(f"  Format issues only: {partial}/10 ({partial*10}%)")
print(f"  Truly incorrect: {incorrect}/10 ({incorrect*10}%)")

# Show failures if any
failures = [r for r in results if r.get('em') == 0]
if failures:
    print(f"\n{'─'*80}")
    print(f"FAILURES ANALYSIS ({len(failures)} samples)")
    print(f"{'─'*80}")
    
    for i, fail in enumerate(failures[:5], 1):  # Show first 5
        print(f"\n[{fail['sample_id']}] Sample {fail['sample_id']}:")
        print(f"  Question: {fail.get('question', 'N/A')[:80]}...")
        print(f"  Gold: {fail.get('gold_answer', 'N/A')}")
        print(f"  Predicted: {fail.get('predicted_answer', 'N/A')}")
        print(f"  LLM Judge: {fail.get('llm_judgment', 'N/A')}")
        
        # Check if format issue or true error
        if fail.get('llm_judgment') == 'CORRECT':
            print(f"  Issue: ⚠️ FORMAT (semantically correct)")
        else:
            print(f"  Issue: ❌ WRONG REASONING")

# Retrieval method analysis
print(f"\n{'─'*80}")
print("RETRIEVAL METHOD USAGE")
print(f"{'─'*80}")

p2p_count = 0
q2p_fallback_count = 0

for r in results:
    if 'retrieval_methods' in r and len(r['retrieval_methods']) > 1:
        if 'P2P' in r['retrieval_methods']:
            p2p_count += 1
        if 'Q2P-fallback' in r['retrieval_methods']:
            q2p_fallback_count += 1

print(f"Stage 2 used P2P: {p2p_count}/10 ({p2p_count*10}%)")
print(f"Stage 2 used Q2P fallback: {q2p_fallback_count}/10 ({q2p_fallback_count*10}%)")

# Next steps recommendation
print(f"\n{'='*100}")
print("NEXT STEPS")
print(f"{'='*100}")

if avg_em >= 70:
    print("🎉 EXCELLENT RESULTS!")
    print("\n✅ System is working very well!")
    print("   → Ready for full 50-sample evaluation (Cell 17)")
    print("   → Expected full results: 70-75% EM")
elif avg_em >= 60:
    print("✅ GOOD RESULTS!")
    print("\n⚠️ Some room for improvement, but working well")
    print("   → Can proceed to full evaluation")
    print("   → Expected full results: 60-70% EM")
    print("\n💡 To improve further:")
    print("   - Check format issues in failures above")
    print("   - Consider adjusting synthesis prompt")
elif avg_em >= 50:
    print("⚠️ OKAY RESULTS")
    print("\n⚠️ Needs some debugging")
    print("   → Review failures above")
    print("   → Check if synthesis is working correctly")
    print("   → Can still try full evaluation to see overall trend")
else:
    print("❌ NEEDS DEBUGGING")
    print("\n❌ Something is wrong")
    print("   → Review failures above carefully")
    print("   → Check synthesis output")
    print("   → Verify Cell 14 applied correctly")

print(f"\n{'='*100}")
print("✓ Quick test complete!")
print(f"{'='*100}")
```

---

## **Expected Output:**

### **Success Case (EM ≥ 70%):**
```
====================================================================================================
QUICK TEST: 10 HOTPOTQA SAMPLES
====================================================================================================

Processing: 100%|██████████| 10/10 [05:23<00:00, 32.3s/it]

[1/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: Arthur's Magazine
[2/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: David Gregory
[3/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: Chris Pine
[4/10] EM: 0 | F1: 0.85 | Judge: CORRECT | Answer: June Tabor (format issue)
[5/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: 2014
...

====================================================================================================
RESULTS SUMMARY - 10 SAMPLES
====================================================================================================

Time elapsed: 5.38 minutes
Samples processed: 10

────────────────────────────────────────────────────────────────────────────────
AGGREGATE METRICS
────────────────────────────────────────────────────────────────────────────────
EM: 70.0%
F1: 0.823
BERTScore F1: 0.867
LLM Judge Accuracy: 80.0%
Avg Passages: 4.5
Avg Stages: 2.1

────────────────────────────────────────────────────────────────────────────────
COMPARISON WITH BASELINE
────────────────────────────────────────────────────────────────────────────────
Baseline K=5: 34%
Baseline K=10: 36%
Your method: 70.0%

Improvement over K=5: +36.0 percentage points 🚀
Improvement over K=10: +34.0 percentage points 🚀

🎉 Status: 🎉 EXCELLENT!

────────────────────────────────────────────────────────────────────────────────
DETAILED BREAKDOWN
────────────────────────────────────────────────────────────────────────────────

Samples by result:
  Perfect (EM=1): 7/10 (70%)
  Semantically correct (LLM Judge): 8/10 (80%)
  Format issues only: 1/10 (10%)
  Truly incorrect: 2/10 (20%)

====================================================================================================
NEXT STEPS
====================================================================================================
🎉 EXCELLENT RESULTS!

✅ System is working very well!
   → Ready for full 50-sample evaluation (Cell 17)
   → Expected full results: 70-75% EM
```

---

## **What to Look For:**

### **✅ SUCCESS Indicators:**
- **EM ≥ 70%** → Excellent! 🎉
- **LLM Judge ≥ 75%** → Reasoning works
- **Format issues < 20%** → Synthesis mostly works
- **Avg Passages < 5.0** → Efficient

### **⚠️ WARNING Indicators:**
- **EM 60-69%** → Good but can improve
- **Format issues 20-40%** → Synthesis needs tweaking
- **Avg Passages > 6.0** → Too much retrieval

### **❌ ERROR Indicators:**
- **EM < 50%** → Something wrong
- **Many "WRONG REASONING"** → Retrieval or decomposition issue
- **Synthesis errors** → API or prompt issue

---

## **After Running:**

### **If EM ≥ 70% ✅:**
```
🎉 PERFECT!
→ Proceed directly to Cell 17 (full 50-sample evaluation)
→ Expected: 70-75% EM on full dataset
```

### **If EM 60-69% ⚠️:**
```
✅ GOOD!
→ Can proceed to Cell 17
→ Expected: 60-70% EM on full dataset
→ Optional: Review format issues to improve further
```

### **If EM 50-59% ⚠️:**
```
⚠️ OKAY
→ Review failures carefully
→ Check if synthesis is the main issue
→ Can still proceed but results might be lower
```

### **If EM < 50% ❌:**
```
❌ NEEDS FIX
→ Share the FAILURES ANALYSIS section
→ Check if synthesis is crashing
→ Verify Cell 14 replacement worked
```

---

**Action NOW:**

1. **Copy-paste code above** as new cell
2. **Run the cell**
3. **Wait ~5-7 minutes**
4. **Check the final EM percentage**

Let me know:
- **What is the EM?** (70%? 60%? 50%?)
- **Any synthesis errors?**
- **How many format issues vs true errors?**

Ready? Go! 🚀