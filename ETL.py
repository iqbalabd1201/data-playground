# Error: `model` Not Defined! 🔴

Ah, code error karena variable `model` tidak didefinisikan di dalam function/scope yang sama.

---

## **Quick Fix:**

Code test perlu akses ke `model` yang sudah di-load sebelumnya. Update jadi standalone:

```python
# ==================== TEST: RETRIEVAL WITHOUT TITLE (FIXED) ====================
print("="*100)
print("TEST: RETRIEVAL WITHOUT TITLE (TEXT ONLY)")
print("="*100)

import torch
from sentence_transformers import util

# Ensure model is available
if 'model' not in globals():
    print("Loading IndoBERT model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('firqaaa/indo-sentence-bert-base')
    model = model.to(device)

# Get sample 4
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')
sample_4 = hotpot_samples[3]

question = get_question(sample_4, 'hotpotqa')
all_passages = get_contexts(sample_4, 'hotpotqa')

print(f"Question: {question}")
print(f"Total passages: {len(all_passages)}")

# Encode question once
question_embedding = model.encode(question, convert_to_tensor=True)

# Test 4 strategies
print(f"\n{'='*100}")
print("STRATEGY COMPARISON")
print(f"{'='*100}")

results_summary = []

# Strategy 1: TITLE + TEXT[:200] (current method)
print(f"\n{'─'*80}")
print("STRATEGY 1: TITLE + TEXT[:200] (CURRENT)")
print(f"{'─'*80}")

passage_texts_1 = [
    f"{get_context_title(ctx, 'hotpotqa')} {get_context_text(ctx, 'hotpotqa')[:200]}"
    for ctx in all_passages
]

passage_embeddings_1 = model.encode(passage_texts_1, convert_to_tensor=True, show_progress_bar=False)
scores_1 = util.cos_sim(question_embedding, passage_embeddings_1)[0]
top_5_1 = torch.topk(scores_1, 5)

print("\nTop-5 results:")
ewan_rank_1 = None
for rank, (score, idx) in enumerate(zip(top_5_1.values, top_5_1.indices), 1):
    title = get_context_title(all_passages[idx], 'hotpotqa')
    is_gold = is_gold_passage(all_passages[idx], 'hotpotqa')
    marker = "✓" if is_gold else "✗"
    
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        ewan_rank_1 = rank
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f}) ← EWAN!")
    else:
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f})")

if ewan_rank_1:
    print(f"\n✓ Ewan MacColl at RANK {ewan_rank_1}")
else:
    print(f"\n✗ Ewan MacColl NOT in top-5")

results_summary.append(("TITLE + TEXT[:200]", ewan_rank_1))

# Strategy 2: TEXT ONLY [:500]
print(f"\n{'─'*80}")
print("STRATEGY 2: TEXT ONLY [:500]")
print(f"{'─'*80}")

passage_texts_2 = [
    get_context_text(ctx, 'hotpotqa')[:500]
    for ctx in all_passages
]

passage_embeddings_2 = model.encode(passage_texts_2, convert_to_tensor=True, show_progress_bar=False)
scores_2 = util.cos_sim(question_embedding, passage_embeddings_2)[0]
top_5_2 = torch.topk(scores_2, 5)

print("\nTop-5 results:")
ewan_rank_2 = None
for rank, (score, idx) in enumerate(zip(top_5_2.values, top_5_2.indices), 1):
    title = get_context_title(all_passages[idx], 'hotpotqa')
    is_gold = is_gold_passage(all_passages[idx], 'hotpotqa')
    marker = "✓" if is_gold else "✗"
    
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        ewan_rank_2 = rank
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f}) ← EWAN!")
    else:
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f})")

if ewan_rank_2:
    print(f"\n✓ Ewan MacColl at RANK {ewan_rank_2}")
else:
    print(f"\n✗ Ewan MacColl NOT in top-5")

results_summary.append(("TEXT ONLY [:500]", ewan_rank_2))

# Strategy 3: TEXT ONLY [:1000]
print(f"\n{'─'*80}")
print("STRATEGY 3: TEXT ONLY [:1000]")
print(f"{'─'*80}")

passage_texts_3 = [
    get_context_text(ctx, 'hotpotqa')[:1000]
    for ctx in all_passages
]

passage_embeddings_3 = model.encode(passage_texts_3, convert_to_tensor=True, show_progress_bar=False)
scores_3 = util.cos_sim(question_embedding, passage_embeddings_3)[0]
top_5_3 = torch.topk(scores_3, 5)

print("\nTop-5 results:")
ewan_rank_3 = None
for rank, (score, idx) in enumerate(zip(top_5_3.values, top_5_3.indices), 1):
    title = get_context_title(all_passages[idx], 'hotpotqa')
    is_gold = is_gold_passage(all_passages[idx], 'hotpotqa')
    marker = "✓" if is_gold else "✗"
    
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        ewan_rank_3 = rank
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f}) ← EWAN!")
    else:
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f})")

if ewan_rank_3:
    print(f"\n✓ Ewan MacColl at RANK {ewan_rank_3}")
else:
    print(f"\n✗ Ewan MacColl NOT in top-5")

results_summary.append(("TEXT ONLY [:1000]", ewan_rank_3))

# Strategy 4: TEXT ONLY [FULL]
print(f"\n{'─'*80}")
print("STRATEGY 4: TEXT ONLY [FULL]")
print(f"{'─'*80}")

passage_texts_4 = [
    get_context_text(ctx, 'hotpotqa')
    for ctx in all_passages
]

passage_embeddings_4 = model.encode(passage_texts_4, convert_to_tensor=True, show_progress_bar=False)
scores_4 = util.cos_sim(question_embedding, passage_embeddings_4)[0]
top_5_4 = torch.topk(scores_4, 5)

print("\nTop-5 results:")
ewan_rank_4 = None
for rank, (score, idx) in enumerate(zip(top_5_4.values, top_5_4.indices), 1):
    title = get_context_title(all_passages[idx], 'hotpotqa')
    is_gold = is_gold_passage(all_passages[idx], 'hotpotqa')
    marker = "✓" if is_gold else "✗"
    
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        ewan_rank_4 = rank
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f}) ← EWAN!")
    else:
        print(f"  [{rank}] {marker} {title:45s} ({score:.4f})")

if ewan_rank_4:
    print(f"\n✓ Ewan MacColl at RANK {ewan_rank_4}")
else:
    print(f"\n✗ Ewan MacColl NOT in top-5")

results_summary.append(("TEXT ONLY [FULL]", ewan_rank_4))

# Summary table
print(f"\n{'='*100}")
print("SUMMARY: EWAN MACCOLL RANKING")
print(f"{'='*100}")

print(f"\n{'Strategy':<25s} {'Rank':<10s} {'Status'}")
print(f"{'─'*60}")

for strategy_name, rank in results_summary:
    if rank == 1:
        status = "🎉 BEST!"
    elif rank and rank <= 3:
        status = "✅ Good"
    elif rank and rank <= 5:
        status = "⚠️ OK"
    else:
        status = "❌ Failed"
    
    rank_str = str(rank) if rank else "Not in top-5"
    print(f"{strategy_name:<25s} {rank_str:<10s} {status}")

# Find where "James Henry Miller" appears in Ewan MacColl passage
print(f"\n{'='*100}")
print("TEXT POSITION ANALYSIS")
print(f"{'='*100}")

for idx, ctx in enumerate(all_passages):
    title = get_context_title(ctx, 'hotpotqa')
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        text = get_context_text(ctx, 'hotpotqa')
        print(f"\nEwan MacColl passage:")
        print(f"  Title: {title}")
        print(f"  Text length: {len(text)} chars")
        
        if 'james henry miller' in text.lower():
            pos = text.lower().index('james henry miller')
            print(f"  'James Henry Miller' at position: {pos}")
            
            # Show context
            start = max(0, pos - 30)
            end = min(len(text), pos + 100)
            print(f"  Context: ...{text[start:end]}...")
            
            if pos <= 200:
                print(f"  ✓ Within [:200] - should work with title+text[:200]")
            elif pos <= 500:
                print(f"  ⚠️ Within [:500] - needs text[:500]")
            elif pos <= 1000:
                print(f"  ⚠️ Within [:1000] - needs text[:1000]")
            else:
                print(f"  ❌ After 1000 - needs full text")
        else:
            print(f"  ⚠️ 'James Henry Miller' NOT found!")
            print(f"  First 200 chars: {text[:200]}")

# Recommendation
print(f"\n{'='*100}")
print("RECOMMENDATION")
print(f"{'='*100}")

best_strategy = min(results_summary, key=lambda x: x[1] if x[1] else 999)
print(f"\nBest strategy: {best_strategy[0]} (Rank {best_strategy[1]})")

if best_strategy[1] == 1:
    print(f"✅ This strategy puts Ewan MacColl at RANK 1!")
    print(f"   → Recommended to use this in retrieve_passages_dense()")
elif best_strategy[1] and best_strategy[1] <= 3:
    print(f"⚠️ This strategy gets Rank {best_strategy[1]} - acceptable but not optimal")
else:
    print(f"❌ Even best strategy doesn't get Rank 1")
    print(f"   → May need hybrid retrieval (BM25 + Dense)")

print(f"\n{'='*100}")
print("✓ Test complete")
print(f"{'='*100}")
```

---

## **What This Shows:**

1. **4 ranking comparisons** side-by-side
2. **Position of "James Henry Miller"** in text
3. **Best strategy recommendation**

---

**Run ini, kasih tau:**
- **Which strategy gives RANK 1?**
- **Position of "James Henry Miller" in text?**

Ini akan kasih answer pasti apakah title yang bikin rank turun! 🎯