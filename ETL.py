Oke! Saya buatkan cell untuk **debug spesifik** "El Extraño Viaje" entity - lihat embeddings dan ranking detail!

## CELL: Debug "El Extraño Viaje" Entity Retrieval

```python
print("="*100)
print("DEBUG: 'El Extraño Viaje' ENTITY EMBEDDING & RANKING")
print("="*100)

# Get sample
wiki_sample = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[0]
question = get_question(wiki_sample, '2wikimultihop')
contexts = get_contexts(wiki_sample, '2wikimultihop')

print(f"Main Question: {question}")
print(f"Total passages: {len(contexts)}")

# Show all passage titles first
print(f"\n{'-'*80}")
print("ALL PASSAGE TITLES")
print(f"{'-'*80}")
for i, ctx in enumerate(contexts):
    title = get_context_title(ctx, '2wikimultihop')
    is_gold = is_gold_passage(ctx, '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  {i+1:2d}. {marker} {title}")

# Test Query: Just "El Extraño Viaje"
test_query = "El Extraño Viaje"

print(f"\n{'='*80}")
print(f"TEST QUERY: \"{test_query}\"")
print(f"{'='*80}")

# Extract all passage texts
passage_texts = [get_context_text(ctx, '2wikimultihop') for ctx in contexts]

# Encode query
print(f"\nStep 1: Encoding query...")
query_embedding = model_indobert.encode(test_query, convert_to_tensor=True)
print(f"  Query: \"{test_query}\"")
print(f"  Embedding shape: {query_embedding.shape}")
print(f"  Embedding (first 10 dims): {query_embedding[:10].cpu().numpy()}")

# Encode passages
print(f"\nStep 2: Encoding all passages...")
passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
print(f"  Number of passages: {len(passage_texts)}")
print(f"  Embedding shape: {passage_embeddings.shape}")

# Compute similarities
print(f"\nStep 3: Computing cosine similarities...")
similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
print(f"  Similarity scores shape: {similarities.shape}")

# Get ranking
ranked_indices = torch.argsort(similarities, descending=True).cpu().numpy()

# Display ALL passages with similarity scores
print(f"\n{'='*80}")
print(f"ALL PASSAGES RANKED BY SIMILARITY TO: \"{test_query}\"")
print(f"{'='*80}")

print(f"\n{'Rank':<6} {'Gold':<6} {'Title':<50} {'Score':<10} {'Preview'}")
print(f"{'-'*120}")

for rank, idx in enumerate(ranked_indices, 1):
    ctx = contexts[idx]
    title = get_context_title(ctx, '2wikimultihop')
    score = float(similarities[idx])
    is_gold = is_gold_passage(ctx, '2wikimultihop')
    text = get_context_text(ctx, '2wikimultihop')
    preview = text[:60] + "..." if len(text) > 60 else text
    
    gold_marker = "GOLD" if is_gold else "DIST"
    
    # Highlight if it's the passage we're looking for
    if "extraño" in title.lower() or "extrano" in title.lower():
        print(f">>> {rank:<4} {gold_marker:<6} {title[:48]:48s} {score:8.4f}   {preview}")
    else:
        print(f"    {rank:<4} {gold_marker:<6} {title[:48]:48s} {score:8.4f}   {preview}")

# Find "El Extraño Viaje" passage specifically
print(f"\n{'='*80}")
print("ANALYSIS: WHERE IS 'El Extraño Viaje' PASSAGE?")
print(f"{'='*80}")

target_passage_idx = None
target_rank = None

for rank, idx in enumerate(ranked_indices, 1):
    ctx = contexts[idx]
    title = get_context_title(ctx, '2wikimultihop')
    
    if "extraño viaje" in title.lower() or "extrano viaje" in title.lower():
        target_passage_idx = idx
        target_rank = rank
        break

if target_passage_idx is not None:
    print(f"\nFound 'El Extraño Viaje' passage!")
    print(f"  Position in original list: {target_passage_idx + 1}")
    print(f"  Rank after retrieval: {target_rank}")
    print(f"  Similarity score: {float(similarities[target_passage_idx]):.4f}")
    
    # Check if it's in top-5
    if target_rank <= 5:
        print(f"  Status: IN TOP-5 ✓")
    else:
        print(f"  Status: NOT IN TOP-5 ✗ (need to retrieve top-{target_rank} to get it)")
    
    # Show the full text
    target_text = get_context_text(contexts[target_passage_idx], '2wikimultihop')
    print(f"\n  Passage text:")
    print(f"  {target_text[:200]}...")
    
    # Check why it got this score
    print(f"\n{'-'*80}")
    print("DETAILED SIMILARITY ANALYSIS")
    print(f"{'-'*80}")
    
    # Compare with top-1
    top1_idx = ranked_indices[0]
    top1_title = get_context_title(contexts[top1_idx], '2wikimultihop')
    top1_score = float(similarities[top1_idx])
    top1_text = get_context_text(contexts[top1_idx], '2wikimultihop')
    
    print(f"\nTop-1 Passage (for comparison):")
    print(f"  Title: {top1_title}")
    print(f"  Score: {top1_score:.4f}")
    print(f"  Text preview: {top1_text[:150]}...")
    
    print(f"\nTarget Passage ('El Extraño Viaje'):")
    print(f"  Title: {get_context_title(contexts[target_passage_idx], '2wikimultihop')}")
    print(f"  Score: {float(similarities[target_passage_idx]):.4f}")
    print(f"  Text preview: {target_text[:150]}...")
    
    print(f"\nScore Difference:")
    score_diff = top1_score - float(similarities[target_passage_idx])
    print(f"  Top-1 score - Target score: {score_diff:+.4f}")
    
    if score_diff > 0.1:
        print(f"  → Large gap! Top-1 passage much more similar to query")
    elif score_diff > 0.05:
        print(f"  → Moderate gap")
    else:
        print(f"  → Small gap, scores are close")
    
    # Check if query entity appears in passages
    print(f"\n{'-'*80}")
    print("ENTITY MATCHING CHECK")
    print(f"{'-'*80}")
    
    print(f"\nQuery: \"{test_query}\"")
    
    # Check top-1
    print(f"\nTop-1 passage ({top1_title}):")
    if "extraño" in top1_text.lower() or "extrano" in top1_text.lower():
        print(f"  Contains 'Extraño': YES")
    else:
        print(f"  Contains 'Extraño': NO")
    
    if "viaje" in top1_text.lower():
        print(f"  Contains 'Viaje': YES")
    else:
        print(f"  Contains 'Viaje': NO")
    
    # Check target
    print(f"\nTarget passage (El Extraño Viaje):")
    if "extraño" in target_text.lower() or "extrano" in target_text.lower():
        print(f"  Contains 'Extraño': YES")
    else:
        print(f"  Contains 'Extraño': NO")
    
    if "viaje" in target_text.lower():
        print(f"  Contains 'Viaje': YES")
    else:
        print(f"  Contains 'Viaje': NO")

else:
    print(f"\nWARNING: 'El Extraño Viaje' passage NOT FOUND in dataset!")

# Score statistics
print(f"\n{'='*80}")
print("SCORE STATISTICS")
print(f"{'='*80}")

all_scores = similarities.cpu().numpy()
print(f"\nAll similarity scores:")
print(f"  Mean: {np.mean(all_scores):.4f}")
print(f"  Std:  {np.std(all_scores):.4f}")
print(f"  Min:  {np.min(all_scores):.4f}")
print(f"  Max:  {np.max(all_scores):.4f}")

# Check gold passages
gold_indices = [i for i, c in enumerate(contexts) if is_gold_passage(c, '2wikimultihop')]
gold_scores = [float(similarities[i]) for i in gold_indices]

print(f"\nGold passages scores:")
print(f"  Mean: {np.mean(gold_scores):.4f}")
print(f"  Min:  {np.min(gold_scores):.4f}")
print(f"  Max:  {np.max(gold_scores):.4f}")

print(f"\nGold passage positions:")
for gold_idx in gold_indices:
    gold_title = get_context_title(contexts[gold_idx], '2wikimultihop')
    gold_rank = list(ranked_indices).index(gold_idx) + 1
    gold_score = float(similarities[gold_idx])
    print(f"  '{gold_title[:40]}': Rank {gold_rank}, Score {gold_score:.4f}")

# Conclusion
print(f"\n{'='*80}")
print("DEBUG CONCLUSION")
print(f"{'='*80}")

if target_rank:
    print(f"\nQuery: \"{test_query}\"")
    print(f"Target Passage Rank: {target_rank}")
    
    if target_rank == 1:
        print(f"\nStatus: PERFECT! Target is rank 1")
    elif target_rank <= 3:
        print(f"\nStatus: GOOD! Target in top-3")
    elif target_rank <= 5:
        print(f"\nStatus: OK! Target in top-5")
    else:
        print(f"\nStatus: POOR! Target outside top-5")
        print(f"\nPossible reasons:")
        print(f"  1. IndoBERT encoding issue with Spanish text")
        print(f"  2. Other passages have higher semantic similarity")
        print(f"  3. Need more specific query (e.g., add 'film' or 'sutradara')")
else:
    print(f"\nERROR: Target passage not found!")

print(f"\n{'='*80}")
```

Jalankan cell ini untuk melihat **detail lengkap** bagaimana "El Extraño Viaje" di-rank!

**Expected output:**
- Semua passage titles
- Similarity scores untuk semua passages
- Ranking lengkap (1-10)
- Position dari "El Extraño Viaje" passage
- Score comparison
- Entity matching check
- Detailed analysis kenapa rank nya di posisi tertentu

Ini akan kasih insight apakah:
1. Entity "El Extraño Viaje" alone cukup untuk retrieve passage yang benar
2. Atau perlu tambahan context (e.g., "sutradara", "film")