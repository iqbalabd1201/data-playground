Oke! Saya buatkan cell untuk **test Stage 1 retrieval** - lihat similarity score dan ranking passage untuk sub-question Stage 1!

## CELL: Test Stage 1 Retrieval dengan Similarity Scores

```python
print("="*100)
print("TEST STAGE 1 RETRIEVAL - QUESTION-TO-PASSAGE SIMILARITY")
print("="*100)

def test_stage1_retrieval(sample, dataset_name, use_decomposition=True):
    """
    Test retrieval untuk Stage 1 question
    Show similarity scores dan ranking
    """
    
    # Get data
    main_question = get_question(sample, dataset_name)
    gold_answer = get_answer(sample, dataset_name)
    all_contexts = get_contexts(sample, dataset_name)
    
    print(f"\nMain Question: {main_question}")
    print(f"Gold Answer: {gold_answer}")
    print(f"Total passages: {len(all_contexts)}")
    
    # Count gold passages
    num_gold = sum(1 for c in all_contexts if is_gold_passage(c, dataset_name))
    print(f"Gold passages: {num_gold}")
    
    # Decompose question
    if use_decomposition:
        print(f"\n{'-'*80}")
        print("DECOMPOSING QUESTION")
        print(f"{'-'*80}")
        
        decomposition = decompose_question_visualized(main_question, dataset_name)
        
        if not decomposition or not decomposition.get('sub_questions'):
            print("Decomposition failed, using main question")
            stage1_question = main_question
        else:
            sub_questions = decomposition['sub_questions']
            
            print(f"\nQuestion Type: {decomposition.get('question_type', 'unknown')}")
            print(f"Total Stages: {len(sub_questions)}")
            
            # Get Stage 1 question
            stage1_sq = sub_questions[0]
            stage1_question = stage1_sq['question']
            
            print(f"\n{'-'*80}")
            print("STAGE 1 SUB-QUESTION")
            print(f"{'-'*80}")
            print(f"Question: {stage1_question}")
            print(f"Purpose: {stage1_sq.get('purpose', 'N/A')}")
            print(f"Depends on: {stage1_sq.get('depends_on', []) or 'None (independent)'}")
    else:
        stage1_question = main_question
    
    # Retrieval dengan IndoBERT
    print(f"\n{'='*80}")
    print("STAGE 1 RETRIEVAL - QUESTION TO PASSAGE SIMILARITY")
    print(f"{'='*80}")
    
    print(f"\nQuery: {stage1_question}")
    
    # Extract passage texts
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in all_contexts]
    
    print(f"\n{'-'*80}")
    print("ENCODING")
    print(f"{'-'*80}")
    
    # Encode query
    print(f"Encoding query...")
    query_embedding = model_indobert.encode(stage1_question, convert_to_tensor=True)
    print(f"  Query embedding shape: {query_embedding.shape}")
    print(f"  → 1 vector of {query_embedding.shape[0]} dimensions")
    
    # Encode passages
    print(f"\nEncoding {len(passage_texts)} passages...")
    passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
    print(f"  Passage embeddings shape: {passage_embeddings.shape}")
    print(f"  → {passage_embeddings.shape[0]} vectors, each {passage_embeddings.shape[1]} dimensions")
    
    # Compute similarity
    print(f"\n{'-'*80}")
    print("COMPUTING COSINE SIMILARITY")
    print(f"{'-'*80}")
    
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    print(f"Similarity scores shape: {similarities.shape}")
    print(f"  → {similarities.shape[0]} scores, one for each passage")
    
    # Get ranking
    ranked_indices = torch.argsort(similarities, descending=True).cpu().numpy()
    
    # Display all passages with scores
    print(f"\n{'='*80}")
    print("ALL PASSAGES RANKED BY SIMILARITY")
    print(f"{'='*80}")
    
    print(f"\n{'Rank':<6} {'Type':<6} {'Title':<50} {'Score':<10} {'Gold'}")
    print(f"{'-'*100}")
    
    for rank, idx in enumerate(ranked_indices, 1):
        ctx = all_contexts[idx]
        title = get_context_title(ctx, dataset_name)
        score = float(similarities[idx])
        is_gold = is_gold_passage(ctx, dataset_name)
        
        type_marker = "[GOLD]" if is_gold else "[DIST]"
        gold_marker = "✓" if is_gold else "✗"
        
        # Highlight top-5
        if rank <= 5:
            prefix = ">>>" if is_gold else "   "
        else:
            prefix = "   "
        
        print(f"{prefix} {rank:<4} {type_marker:<6} {title[:48]:48s} {score:8.4f}   {gold_marker}")
    
    # Top-K analysis
    print(f"\n{'='*80}")
    print("TOP-K RETRIEVAL ANALYSIS")
    print(f"{'='*80}")
    
    for k in [1, 3, 5, 10]:
        top_k_indices = ranked_indices[:k]
        
        # Count gold in top-k
        gold_in_topk = sum(1 for idx in top_k_indices if is_gold_passage(all_contexts[idx], dataset_name))
        
        # Calculate recall
        recall = gold_in_topk / num_gold if num_gold > 0 else 0
        
        print(f"\nTop-{k}:")
        print(f"  Gold passages retrieved: {gold_in_topk}/{num_gold}")
        print(f"  Recall@{k}: {recall:.2%}")
        
        if k == 5:
            print(f"\n  Passages in Top-5:")
            for i, idx in enumerate(top_k_indices[:5], 1):
                ctx = all_contexts[idx]
                title = get_context_title(ctx, dataset_name)
                score = float(similarities[idx])
                is_gold = is_gold_passage(ctx, dataset_name)
                marker = "✓ [GOLD]" if is_gold else "✗ [DIST]"
                print(f"    [{i}] {marker} {title[:45]:45s} (score: {score:.4f})")
    
    # Score distribution analysis
    print(f"\n{'='*80}")
    print("SIMILARITY SCORE DISTRIBUTION")
    print(f"{'='*80}")
    
    all_scores = similarities.cpu().numpy()
    gold_scores = [float(similarities[i]) for i in range(len(all_contexts)) 
                   if is_gold_passage(all_contexts[i], dataset_name)]
    dist_scores = [float(similarities[i]) for i in range(len(all_contexts)) 
                   if not is_gold_passage(all_contexts[i], dataset_name)]
    
    print(f"\nAll passages:")
    print(f"  Mean: {np.mean(all_scores):.4f}")
    print(f"  Std:  {np.std(all_scores):.4f}")
    print(f"  Min:  {np.min(all_scores):.4f}")
    print(f"  Max:  {np.max(all_scores):.4f}")
    
    if gold_scores:
        print(f"\nGold passages:")
        print(f"  Mean: {np.mean(gold_scores):.4f}")
        print(f"  Std:  {np.std(gold_scores):.4f}")
        print(f"  Min:  {np.min(gold_scores):.4f}")
        print(f"  Max:  {np.max(gold_scores):.4f}")
    
    if dist_scores:
        print(f"\nDistractor passages:")
        print(f"  Mean: {np.mean(dist_scores):.4f}")
        print(f"  Std:  {np.std(dist_scores):.4f}")
        print(f"  Min:  {np.min(dist_scores):.4f}")
        print(f"  Max:  {np.max(dist_scores):.4f}")
    
    if gold_scores and dist_scores:
        separation = np.mean(gold_scores) - np.mean(dist_scores)
        print(f"\nSeparation (Gold mean - Distractor mean): {separation:+.4f}")
        
        if separation > 0.1:
            print(f"  → Good separation! Gold passages score significantly higher")
        elif separation > 0:
            print(f"  → Moderate separation, some overlap")
        else:
            print(f"  → Poor separation, distractors score higher!")
    
    # Return results for further analysis
    return {
        'stage1_question': stage1_question,
        'similarities': similarities,
        'ranked_indices': ranked_indices,
        'gold_scores': gold_scores,
        'dist_scores': dist_scores,
        'decomposition': decomposition if use_decomposition else None
    }

print("Function loaded successfully")
```

## CELL: Test dengan HotpotQA Sample

```python
print("="*100)
print("TEST: HOTPOTQA SAMPLE - STAGE 1 RETRIEVAL")
print("="*100)

# Get HotpotQA sample
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')
hotpot_sample = hotpot_samples[0]

# Test Stage 1 retrieval
results_hotpot = test_stage1_retrieval(hotpot_sample, 'hotpotqa', use_decomposition=True)

# Additional analysis
print(f"\n{'='*80}")
print("STAGE 1 RETRIEVAL SUMMARY")
print(f"{'='*80}")

print(f"\nStage 1 Question:")
print(f"  {results_hotpot['stage1_question']}")

print(f"\nRetrieval Performance:")
similarities = results_hotpot['similarities']
ranked_indices = results_hotpot['ranked_indices']

# Find positions of gold passages
gold_positions = []
for rank, idx in enumerate(ranked_indices, 1):
    ctx = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[0]
    contexts = get_contexts(hotpot_sample, 'hotpotqa')
    if is_gold_passage(contexts[idx], 'hotpotqa'):
        title = get_context_title(contexts[idx], 'hotpotqa')
        score = float(similarities[idx])
        gold_positions.append((rank, title, score))

print(f"\nGold passage positions:")
for rank, title, score in gold_positions:
    print(f"  Rank {rank}: {title} (score: {score:.4f})")

if gold_positions:
    best_rank = min(p[0] for p in gold_positions)
    worst_rank = max(p[0] for p in gold_positions)
    print(f"\nBest gold rank: {best_rank}")
    print(f"Worst gold rank: {worst_rank}")
    
    if best_rank <= 5:
        print(f"  ✓ At least one gold passage in Top-5")
    else:
        print(f"  ✗ No gold passages in Top-5")
```

## CELL: Test dengan 2WikiMultihop Sample

```python
print("="*100)
print("TEST: 2WIKIMULTIHOP SAMPLE - STAGE 1 RETRIEVAL")
print("="*100)

# Get 2WikiMultihop sample
wiki_samples = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')
wiki_sample = wiki_samples[0]

# Test Stage 1 retrieval
results_wiki = test_stage1_retrieval(wiki_sample, '2wikimultihop', use_decomposition=True)

# Additional analysis
print(f"\n{'='*80}")
print("STAGE 1 RETRIEVAL SUMMARY")
print(f"{'='*80}")

print(f"\nStage 1 Question:")
print(f"  {results_wiki['stage1_question']}")

print(f"\nRetrieval Performance:")
similarities = results_wiki['similarities']
ranked_indices = results_wiki['ranked_indices']

# Find positions of gold passages
contexts = get_contexts(wiki_sample, '2wikimultihop')
gold_positions = []
for rank, idx in enumerate(ranked_indices, 1):
    if is_gold_passage(contexts[idx], '2wikimultihop'):
        title = get_context_title(contexts[idx], '2wikimultihop')
        score = float(similarities[idx])
        gold_positions.append((rank, title, score))

print(f"\nGold passage positions:")
for rank, title, score in gold_positions:
    print(f"  Rank {rank}: {title} (score: {score:.4f})")

if gold_positions:
    best_rank = min(p[0] for p in gold_positions)
    worst_rank = max(p[0] for p in gold_positions)
    print(f"\nBest gold rank: {best_rank}")
    print(f"Worst gold rank: {worst_rank}")
    
    if best_rank <= 5:
        print(f"  ✓ At least one gold passage in Top-5")
    else:
        print(f"  ✗ No gold passages in Top-5")
```

## CELL: Compare Main Question vs Stage 1 Sub-Question

```python
print("="*100)
print("COMPARISON: MAIN QUESTION vs STAGE 1 SUB-QUESTION RETRIEVAL")
print("="*100)

# Get sample
wiki_sample = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[0]
main_question = get_question(wiki_sample, '2wikimultihop')
contexts = get_contexts(wiki_sample, '2wikimultihop')

# Decompose
decomposition = decompose_question_visualized(main_question, '2wikimultihop')
stage1_question = decomposition['sub_questions'][0]['question'] if decomposition else main_question

print(f"Main Question: {main_question}")
print(f"Stage 1 Question: {stage1_question}")

# Retrieval with main question
print(f"\n{'='*80}")
print("RETRIEVAL 1: USING MAIN QUESTION")
print(f"{'='*80}")

passage_texts = [get_context_text(ctx, '2wikimultihop') for ctx in contexts]
query_emb_main = model_indobert.encode(main_question, convert_to_tensor=True)
passage_embs = model_indobert.encode(passage_texts, convert_to_tensor=True)
sim_main = util.cos_sim(query_emb_main, passage_embs)[0]
ranked_main = torch.argsort(sim_main, descending=True)[:5].cpu().numpy()

print(f"\nTop-5 with MAIN question:")
for rank, idx in enumerate(ranked_main, 1):
    title = get_context_title(contexts[idx], '2wikimultihop')
    score = float(sim_main[idx])
    is_gold = is_gold_passage(contexts[idx], '2wikimultihop')
    marker = "✓" if is_gold else "✗"
    print(f"  [{rank}] {marker} {title[:50]:50s} ({score:.4f})")

# Retrieval with stage 1 question
print(f"\n{'='*80}")
print("RETRIEVAL 2: USING STAGE 1 SUB-QUESTION")
print(f"{'='*80}")

query_emb_stage1 = model_indobert.encode(stage1_question, convert_to_tensor=True)
sim_stage1 = util.cos_sim(query_emb_stage1, passage_embs)[0]
ranked_stage1 = torch.argsort(sim_stage1, descending=True)[:5].cpu().numpy()

print(f"\nTop-5 with STAGE 1 question:")
for rank, idx in enumerate(ranked_stage1, 1):
    title = get_context_title(contexts[idx], '2wikimultihop')
    score = float(sim_stage1[idx])
    is_gold = is_gold_passage(contexts[idx], '2wikimultihop')
    marker = "✓" if is_gold else "✗"
    print(f"  [{rank}] {marker} {title[:50]:50s} ({score:.4f})")

# Compare
print(f"\n{'='*80}")
print("COMPARISON ANALYSIS")
print(f"{'='*80}")

# Recall@5
num_gold = sum(1 for c in contexts if is_gold_passage(c, '2wikimultihop'))
gold_in_main = sum(1 for idx in ranked_main if is_gold_passage(contexts[idx], '2wikimultihop'))
gold_in_stage1 = sum(1 for idx in ranked_stage1 if is_gold_passage(contexts[idx], '2wikimultihop'))

recall_main = gold_in_main / num_gold if num_gold > 0 else 0
recall_stage1 = gold_in_stage1 / num_gold if num_gold > 0 else 0

print(f"\nRecall@5:")
print(f"  Main question:   {recall_main:.2%} ({gold_in_main}/{num_gold})")
print(f"  Stage 1 question: {recall_stage1:.2%} ({gold_in_stage1}/{num_gold})")
print(f"  Difference:      {(recall_stage1 - recall_main)*100:+.1f} percentage points")

if recall_stage1 > recall_main:
    print(f"\n  ✓ Stage 1 decomposition improves retrieval!")
elif recall_stage1 == recall_main:
    print(f"\n  → Stage 1 decomposition has same performance")
else:
    print(f"\n  ✗ Stage 1 decomposition hurts retrieval")

# Score statistics
print(f"\nScore Statistics:")
print(f"  Main question:")
print(f"    Mean: {sim_main.mean():.4f}")
print(f"    Top-5 mean: {sim_main[ranked_main].mean():.4f}")

print(f"  Stage 1 question:")
print(f"    Mean: {sim_stage1.mean():.4f}")
print(f"    Top-5 mean: {sim_stage1[ranked_stage1].mean():.4f}")
```

## Expected Output:

```
================================================================================
ALL PASSAGES RANKED BY SIMILARITY
================================================================================

Rank  Type   Title                                              Score      Gold
----------------------------------------------------------------------------------------------------
>>> 1 [GOLD] Arthur's Magazine                                 0.5949     ✓
>>> 2 [GOLD] First for Women                                   0.5694     ✓
    3 [DIST] Women's colleges in the Southern United States    0.3561     ✗
    4 [DIST] Echosmith                                         0.4150     ✗
    5 [DIST] William Rast                                      0.4282     ✗
    6 [DIST] Radio City (Indian radio station)                 0.3065     ✗
    7 [DIST] History of Albanian football                      0.3310     ✗
    8 [DIST] First Arthur County Courthouse and Jail           0.3669     ✗
    9 [DIST] 2014-15 Ukrainian Hockey Championship             0.2812     ✗
   10 [DIST] Freeway Complex Fire                              0.2970     ✗

================================================================================
TOP-K RETRIEVAL ANALYSIS
================================================================================

Top-5:
  Gold passages retrieved: 2/2
  Recall@5: 100.00%

  Passages in Top-5:
    [1] ✓ [GOLD] Arthur's Magazine                     (score: 0.5949)
    [2] ✓ [GOLD] First for Women                       (score: 0.5694)
    [3] ✗ [DIST] Women's colleges...                   (score: 0.3561)
    [4] ✗ [DIST] Echosmith                             (score: 0.4150)
    [5] ✗ [DIST] William Rast                          (score: 0.4282)

================================================================================
SIMILARITY SCORE DISTRIBUTION
================================================================================

All passages:
  Mean: 0.4145
  Std:  0.1023

Gold passages:
  Mean: 0.5822  ← Higher!
  Std:  0.0180

Distractor passages:
  Mean: 0.3564  ← Lower!
  Std:  0.0578

Separation (Gold mean - Distractor mean): +0.2258
  → Good separation! Gold passages score significantly higher
```

Jalankan cell-cell ini untuk melihat detail similarity score dan ranking untuk Stage 1 retrieval!