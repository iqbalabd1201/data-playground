# Debug Sample 4: James Henry Miller → Ewan MacColl 🔍

Dari screenshot, saya lihat **ada 2 masalah**:

1. **James Henry Miller (25 January 1915 – 22 October 1989)** → ini **Ewan MacColl** (nama panggung)
2. **June Miller** bukan istrinya, yang benar **Peggy Seeger**

---

## **Debug Code: Test Stage 1 Only**

Copy-paste ini untuk debug detail:

```python
# ==================== DEBUG: SAMPLE 4 STAGE 1 ONLY ====================
print("="*100)
print("DEBUG: JAMES HENRY MILLER CASE - STAGE 1 RETRIEVAL")
print("="*100)

# Get sample 4
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')
sample_4 = hotpot_samples[3]  # Index 3 = Sample 4

question = get_question(sample_4, 'hotpotqa')
gold_answer = get_answer(sample_4, 'hotpotqa')
all_passages = get_contexts(sample_4, 'hotpotqa')

print(f"\nMain Question: {question}")
print(f"Gold Answer: {gold_answer}")
print(f"Total passages: {len(all_passages)}")

# Show all passage titles first
print(f"\n{'='*100}")
print("ALL AVAILABLE PASSAGES:")
print(f"{'='*100}")

for idx, passage in enumerate(all_passages):
    title = get_context_title(passage, 'hotpotqa')
    is_gold = is_gold_passage(passage, 'hotpotqa')
    marker = "✓ GOLD" if is_gold else "✗"
    print(f"[{idx}] {marker} {title}")
    
    # Show snippet if contains key terms
    text = get_context_text(passage, 'hotpotqa')[:200]
    if 'ewan' in text.lower() or 'maccoll' in text.lower() or 'miller' in text.lower():
        print(f"     Preview: {text}...")

# Decompose question
print(f"\n{'='*100}")
print("STEP 1: QUESTION DECOMPOSITION")
print(f"{'='*100}")

sub_questions = decompose_question(question, 'hotpotqa')

print(f"\nDecomposed into {len(sub_questions)} stages:")
for sq in sub_questions:
    print(f"  Stage {sq['stage']}: {sq['question']}")
    print(f"    Purpose: {sq.get('purpose', 'N/A')}")

# Focus on Stage 1
stage_1_question = sub_questions[0]['question']

print(f"\n{'='*100}")
print("STAGE 1 RETRIEVAL TEST")
print(f"{'='*100}")

print(f"\nStage 1 Question: {stage_1_question}")

# Test different K values
for k in [2, 3, 5]:
    print(f"\n{'─'*80}")
    print(f"RETRIEVING WITH K={k}")
    print(f"{'─'*80}")
    
    retrieved = retrieve_passages_dense(
        question=stage_1_question,
        contexts=all_passages,
        dataset_name='hotpotqa',
        k=k
    )
    
    print(f"\nRetrieved passages:")
    ewan_found = False
    
    for i, p in enumerate(retrieved, 1):
        title = get_context_title(p, 'hotpotqa')
        score = p.get('retrieval_score', 0)
        is_gold = is_gold_passage(p, 'hotpotqa')
        marker = "✓" if is_gold else "✗"
        
        if 'ewan' in title.lower() or 'maccoll' in title.lower():
            ewan_found = True
            print(f"  [{i}] {marker} {title:50s} (score: {score:.4f}) ← EWAN MACCOLL FOUND!")
        else:
            print(f"  [{i}] {marker} {title:50s} (score: {score:.4f})")
    
    if ewan_found:
        print(f"\n  ✅ SUCCESS: Ewan MacColl found in top-{k}!")
        
        # Test generation
        print(f"\n  Testing generation with top-{k}...")
        answer, confidence, reasoning, prompt = generate_with_confidence_multistage(
            stage_question=stage_1_question,
            contexts=retrieved,
            dataset_name='hotpotqa',
            main_question=question,
            previous_stage_results=None
        )
        
        print(f"  Answer: {answer}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Reasoning: {reasoning[:200]}...")
        
        if 'ewan' in answer.lower() or 'maccoll' in answer.lower():
            print(f"\n  ✅ GENERATION SUCCESS: Answer mentions Ewan MacColl!")
            break
        else:
            print(f"\n  ⚠️ GENERATION ISSUE: Answer doesn't mention Ewan MacColl")
    else:
        print(f"\n  ❌ FAILURE: Ewan MacColl NOT in top-{k}")

# Analyze why retrieval might fail
print(f"\n{'='*100}")
print("RETRIEVAL ANALYSIS")
print(f"{'='*100}")

print(f"\nStage 1 query: '{stage_1_question}'")
print(f"\nPossible issues:")

# Check if "Ewan MacColl" passage exists
ewan_passage = None
ewan_idx = None
for idx, p in enumerate(all_passages):
    title = get_context_title(p, 'hotpotqa')
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        ewan_passage = p
        ewan_idx = idx
        break

if ewan_passage:
    print(f"\n✓ Ewan MacColl passage EXISTS at index {ewan_idx}")
    print(f"  Title: {get_context_title(ewan_passage, 'hotpotqa')}")
    
    # Show full text
    text = get_context_text(ewan_passage, 'hotpotqa')
    print(f"\n  Full text preview:")
    print(f"  {text[:500]}...")
    
    # Check if text mentions "James Henry Miller"
    if 'james henry miller' in text.lower():
        print(f"\n  ✓ Text DOES mention 'James Henry Miller'")
    else:
        print(f"\n  ⚠️ Text does NOT explicitly mention 'James Henry Miller'")
        print(f"     This is why retrieval might fail!")
        
    # Try query expansion
    print(f"\n{'─'*80}")
    print("TESTING ALTERNATIVE QUERIES")
    print(f"{'─'*80}")
    
    alternative_queries = [
        "Siapa James Henry Miller?",
        "James Henry Miller",
        "Who is James Henry Miller",
        "Ewan MacColl James Henry Miller",
        "James Miller penyanyi",
        "folk singer James Miller"
    ]
    
    for alt_query in alternative_queries:
        print(f"\nQuery: '{alt_query}'")
        
        retrieved = retrieve_passages_dense(
            question=alt_query,
            contexts=all_passages,
            dataset_name='hotpotqa',
            k=3
        )
        
        ewan_rank = None
        for i, p in enumerate(retrieved, 1):
            title = get_context_title(p, 'hotpotqa')
            if 'ewan' in title.lower() or 'maccoll' in title.lower():
                ewan_rank = i
                break
        
        if ewan_rank:
            print(f"  ✓ Ewan MacColl found at rank {ewan_rank}")
        else:
            print(f"  ✗ Ewan MacColl NOT in top-3")
else:
    print(f"\n❌ Ewan MacColl passage does NOT exist in dataset!")
    print(f"   This is a dataset issue, not a retrieval issue")

print(f"\n{'='*100}")
print("DEBUG COMPLETE")
print(f"{'='*100}")
```

---

## **What This Will Show:**

1. **All passage titles** - Verify "Ewan MacColl" exists
2. **Decomposition result** - How Stage 1 question is formed
3. **Retrieval with K=2,3,5** - At what K does "Ewan MacColl" appear?
4. **Generation test** - If retrieved, does LLM generate "Ewan MacColl"?
5. **Text analysis** - Does passage explicitly mention "James Henry Miller"?
6. **Alternative queries** - Which query formulation works best?

---

## **Expected Findings:**

### **Hypothesis 1: Retrieval fails** ❌
```
K=2: June Miller, James Henry Deakin
K=3: June Miller, James Henry Deakin, X
K=5: June Miller, ..., Ewan MacColl (rank 5) ← TOO LOW!

Issue: Need K≥5 or better query
```

### **Hypothesis 2: Retrieval works but generation fails** ❌
```
K=3: Ewan MacColl found (rank 2) ✓
Answer: "Tidak ada informasi" ← LLM doesn't understand connection

Issue: Prompt needs improvement
```

### **Hypothesis 3: Text doesn't mention "James Henry Miller"** ❌
```
Ewan MacColl passage text: "...penyanyi folk..."
Does NOT say "James Henry Miller adalah nama asli Ewan MacColl"

Issue: Need broader query or synonym matching
```

---

**Run debug code dan kasih tau:**
1. **Does "Ewan MacColl" passage exist?**
2. **At what K does it appear?** (K=2? K=3? K=5?)
3. **Does the text mention "James Henry Miller"?**
4. **Which alternative query works best?**

This will tell us **exactly** where the failure is! 🎯