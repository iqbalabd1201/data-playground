# Test: Dense Retrieval WITHOUT Title 🔍

Oke, coba **tanpa title**, hanya **full text** saja:

```python
# ==================== TEST: DENSE RETRIEVAL WITHOUT TITLE ====================
print("="*100)
print("TEST: RETRIEVAL WITHOUT TITLE (TEXT ONLY)")
print("="*100)

import torch
from sentence_transformers import util

# Get sample 4
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')
sample_4 = hotpot_samples[3]

question = get_question(sample_4, 'hotpotqa')
all_passages = get_contexts(sample_4, 'hotpotqa')

print(f"Question: {question}")
print(f"Total passages: {len(all_passages)}")

# Test different strategies
strategies = [
    ("TITLE + TEXT[:200]", lambda ctx: f"{get_context_title(ctx, 'hotpotqa')} {get_context_text(ctx, 'hotpotqa')[:200]}"),
    ("TEXT ONLY [:500]", lambda ctx: get_context_text(ctx, 'hotpotqa')[:500]),
    ("TEXT ONLY [:1000]", lambda ctx: get_context_text(ctx, 'hotpotqa')[:1000]),
    ("TEXT ONLY [FULL]", lambda ctx: get_context_text(ctx, 'hotpotqa')),
]

# Encode question once
question_embedding = model.encode(question, convert_to_tensor=True)

print(f"\n{'='*100}")
print("COMPARISON OF RETRIEVAL STRATEGIES")
print(f"{'='*100}")

for strategy_name, text_func in strategies:
    print(f"\n{'─'*80}")
    print(f"STRATEGY: {strategy_name}")
    print(f"{'─'*80}")
    
    # Encode passages with this strategy
    passage_texts = [text_func(ctx) for ctx in all_passages]
    
    # Show sample encoding for Ewan MacColl
    ewan_idx = None
    for idx, ctx in enumerate(all_passages):
        if 'ewan' in get_context_title(ctx, 'hotpotqa').lower():
            ewan_idx = idx
            print(f"\nEwan MacColl passage encoding (first 200 chars):")
            print(f"  '{passage_texts[idx][:200]}...'")
            break
    
    # Encode all passages
    passage_embeddings = model.encode(passage_texts, convert_to_tensor=True, show_progress_bar=False)
    
    # Compute similarities
    scores = util.cos_sim(question_embedding, passage_embeddings)[0]
    
    # Get rankings
    top_k = min(5, len(all_passages))
    top_results = torch.topk(scores, top_k)
    
    print(f"\nTop-{top_k} results:")
    ewan_rank = None
    
    for rank, (score, idx) in enumerate(zip(top_results.values, top_results.indices), 1):
        title = get_context_title(all_passages[idx], 'hotpotqa')
        is_gold = is_gold_passage(all_passages[idx], 'hotpotqa')
        marker = "✓" if is_gold else "✗"
        
        if 'ewan' in title.lower() or 'maccoll' in title.lower():
            ewan_rank = rank
            print(f"  [{rank}] {marker} {title:45s} (score: {score:.4f}) ← EWAN MACCOLL!")
        else:
            print(f"  [{rank}] {marker} {title:45s} (score: {score:.4f})")
    
    if ewan_rank:
        print(f"\n  ✅ Ewan MacColl found at RANK {ewan_rank}")
    else:
        print(f"\n  ❌ Ewan MacColl NOT in top-{top_k}")
    
    # If found, check if it moved up
    if ewan_rank == 1:
        print(f"  🎉 RANK 1 - PERFECT!")
    elif ewan_rank and ewan_rank <= 3:
        print(f"  ✅ RANK {ewan_rank} - Good (top-3)")
    elif ewan_rank and ewan_rank <= 5:
        print(f"  ⚠️ RANK {ewan_rank} - Acceptable (top-5)")

# Summary comparison
print(f"\n{'='*100}")
print("SUMMARY: EWAN MACCOLL RANKING BY STRATEGY")
print(f"{'='*100}")

print(f"\n{'Strategy':<30s} {'Ewan MacColl Rank':<20s} {'Status'}")
print(f"{'─'*70}")

for strategy_name, text_func in strategies:
    passage_texts = [text_func(ctx) for ctx in all_passages]
    passage_embeddings = model.encode(passage_texts, convert_to_tensor=True, show_progress_bar=False)
    scores = util.cos_sim(question_embedding, passage_embeddings)[0]
    
    # Find Ewan MacColl rank
    sorted_indices = torch.argsort(scores, descending=True)
    ewan_rank = None
    
    for rank, idx in enumerate(sorted_indices, 1):
        title = get_context_title(all_passages[idx], 'hotpotqa')
        if 'ewan' in title.lower() or 'maccoll' in title.lower():
            ewan_rank = rank
            break
    
    if ewan_rank == 1:
        status = "🎉 RANK 1"
    elif ewan_rank and ewan_rank <= 3:
        status = f"✅ RANK {ewan_rank}"
    elif ewan_rank and ewan_rank <= 5:
        status = f"⚠️ RANK {ewan_rank}"
    else:
        status = "❌ NOT IN TOP-5"
    
    print(f"{strategy_name:<30s} {str(ewan_rank) if ewan_rank else 'N/A':<20s} {status}")

# Additional analysis: Check text content
print(f"\n{'='*100}")
print("TEXT CONTENT ANALYSIS")
print(f"{'='*100}")

for idx, ctx in enumerate(all_passages):
    title = get_context_title(ctx, 'hotpotqa')
    text = get_context_text(ctx, 'hotpotqa')
    
    if 'ewan' in title.lower() or 'maccoll' in title.lower():
        print(f"\nEwan MacColl passage:")
        print(f"  Title: {title}")
        print(f"  Text length: {len(text)} characters")
        
        # Find where "James Henry Miller" appears
        if 'james henry miller' in text.lower():
            pos = text.lower().index('james henry miller')
            print(f"  'James Henry Miller' appears at position: {pos}")
            print(f"  Context around it:")
            start = max(0, pos - 50)
            end = min(len(text), pos + 150)
            print(f"    ...{text[start:end]}...")
            
            if pos <= 200:
                print(f"  ✓ Within first 200 chars - SHOULD BE CAUGHT with title+text[:200]")
            elif pos <= 500:
                print(f"  ⚠️ Position 200-500 - NEEDS text[:500]")
            elif pos <= 1000:
                print(f"  ⚠️ Position 500-1000 - NEEDS text[:1000]")
            else:
                print(f"  ❌ After position 1000 - NEEDS full text")
        else:
            print(f"  ⚠️ 'James Henry Miller' NOT FOUND in text!")
            print(f"  First 300 chars: {text[:300]}...")

print(f"\n{'='*100}")
print("✓ Test complete")
print(f"{'='*100}")
```

---

## **What This Will Show:**

1. **Ranking comparison** across 4 strategies:
   - Title + Text[:200] (current)
   - Text only [:500]
   - Text only [:1000]  
   - Text only [FULL]

2. **Where "James Henry Miller" appears** in Ewan MacColl passage

3. **Which strategy gives best rank** for Ewan MacColl

---

## **Expected Results:**

### **Hypothesis A: Title hurts!**
```
TITLE + TEXT[:200]:  Rank 4 ❌
TEXT ONLY [:500]:    Rank 1 ✅
TEXT ONLY [:1000]:   Rank 1 ✅
TEXT ONLY [FULL]:    Rank 1 ✅

→ Title "Ewan MacColl" dilutes the "James Henry Miller" signal!
```

### **Hypothesis B: Text position matters!**
```
'James Henry Miller' appears at position: 15
✓ Within first 200 chars

But title dilutes:
"Ewan MacColl James Henry Miller..." ← "Ewan MacColl" weakens match
vs
"James Henry Miller..." ← Direct match!

→ Remove title = better ranking
```

### **Hypothesis C: Text length matters!**
```
TEXT ONLY [:200]:  Rank 2
TEXT ONLY [:500]:  Rank 1 ✅
TEXT ONLY [:1000]: Rank 1 ✅

'James Henry Miller' appears at position: 320

→ Need at least 500 chars to catch it
```

---

**Run code dan kasih tau:**

1. **Ranking untuk setiap strategy?**
2. **Position of "James Henry Miller" in text?**
3. **Which strategy gives RANK 1?**

This will tell us **exactly** how to fix retrieval! 🎯