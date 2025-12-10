Wah! Hasil **BAGUS SEKALI**! "El Extraño Viaje" passage dapat **Rank 4** (IN TOP-5 ✓) dengan score **0.4818**.

Tapi memang ada masalah: **3 distractor passages ranked higher**!

---

## Analysis dari Screenshot:

```
Query: "El Extraño Viaje"

Top-5 Results:
  1. [DIST] El extraño caso de la mujer asesinada (0.5433) ← WRONG!
  2. [DIST] The Strange Case of the Man and the Beast (0.5282)
  3. [DIST] Rafaela Aparicio (0.5396)
  4. [GOLD] El extraño viaje (0.4818) ← TARGET! But rank 4
  5. [GOLD] Fernando Fernán Gómez (0.4196)
```

**Problem:** Distractor "El extraño caso..." scored HIGHER karena:
- Lebih banyak overlap: "El extraño" (sama)
- IndoBERT confused antara "viaje" vs "caso"

---

## Solusi: Pakai Embedding yang Lebih Bagus!

### Options untuk Better Embeddings:

| Model | Language | Pros | Cons |
|-------|----------|------|------|
| **IndoBERT** (current) | Indonesian | Good for Indonesian | ✗ Weak on Spanish/English |
| **mE5-large** | Multilingual | SOTA multilingual | Large model |
| **BGE-M3** | Multilingual | Very good | 567M params |
| **GTE-multilingual** | Multilingual | Good balance | New model |
| **mT5** | Multilingual | Good coverage | Slow |

---

## CELL: Test dengan mE5-Large (Best Multilingual Embedding)

```python
print("="*100)
print("IMPROVED EMBEDDING: mE5-LARGE MULTILINGUAL")
print("="*100)

# Install sentence-transformers if needed
try:
    from sentence_transformers import SentenceTransformer
    print("sentence-transformers already installed")
except:
    print("Installing sentence-transformers...")
    !pip install -q sentence-transformers

print("\nLoading mE5-large model...")
print("  Model: intfloat/multilingual-e5-large")
print("  Params: 560M (larger than IndoBERT 125M)")
print("  Languages: 100+ including Spanish, Indonesian, English")
print("  This may take 30-60 seconds...")

# Load model
model_me5 = SentenceTransformer('intfloat/multilingual-e5-large')
model_me5 = model_me5.to(device)

print(f"  Model loaded on device: {device}")

# Important: mE5 requires instruction prefix!
def encode_query_me5(query):
    """mE5 requires 'query: ' prefix"""
    return model_me5.encode(f"query: {query}", convert_to_tensor=True)

def encode_passages_me5(passages):
    """mE5 requires 'passage: ' prefix"""
    prefixed = [f"passage: {p}" for p in passages]
    return model_me5.encode(prefixed, convert_to_tensor=True, show_progress_bar=False)

print("\nmE5 model ready!")
print("  IMPORTANT: mE5 uses instruction prefixes:")
print("    Query: 'query: <text>'")
print("    Passage: 'passage: <text>'")
```

## CELL: Compare IndoBERT vs mE5-Large

```python
print("="*100)
print("COMPARISON: IndoBERT vs mE5-Large")
print("="*100)

# Get sample
wiki_sample = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[0]
question = get_question(wiki_sample, '2wikimultihop')
contexts = get_contexts(wiki_sample, '2wikimultihop')

print(f"Main Question: {question}")
print(f"Total passages: {len(contexts)}")

# Test query
test_query = "El Extraño Viaje"
print(f"\nTest Query: \"{test_query}\"")

# Extract passages
passage_texts = [get_context_text(ctx, '2wikimultihop') for ctx in contexts]

# Method 1: IndoBERT
print(f"\n{'='*80}")
print("METHOD 1: IndoBERT")
print(f"{'='*80}")

print(f"Encoding with IndoBERT...")
query_emb_indobert = model_indobert.encode(test_query, convert_to_tensor=True)
passage_embs_indobert = model_indobert.encode(passage_texts, convert_to_tensor=True)

print(f"Computing similarities...")
sims_indobert = util.cos_sim(query_emb_indobert, passage_embs_indobert)[0]
ranked_indobert = torch.argsort(sims_indobert, descending=True).cpu().numpy()

print(f"\nTop-5 with IndoBERT:")
for rank, idx in enumerate(ranked_indobert[:5], 1):
    title = get_context_title(contexts[idx], '2wikimultihop')
    score = float(sims_indobert[idx])
    is_gold = is_gold_passage(contexts[idx], '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [{rank}] {marker} {title[:50]:50s} ({score:.4f})")

# Find target
target_rank_indobert = None
for rank, idx in enumerate(ranked_indobert, 1):
    title = get_context_title(contexts[idx], '2wikimultihop')
    if "el extraño viaje" in title.lower() and len(title) < 20:  # Exact match
        target_rank_indobert = rank
        target_score_indobert = float(sims_indobert[idx])
        break

print(f"\n'El Extraño Viaje' passage:")
print(f"  Rank: {target_rank_indobert}")
print(f"  Score: {target_score_indobert:.4f}")

# Method 2: mE5-Large
print(f"\n{'='*80}")
print("METHOD 2: mE5-Large")
print(f"{'='*80}")

print(f"Encoding with mE5-large...")
query_emb_me5 = encode_query_me5(test_query)
passage_embs_me5 = encode_passages_me5(passage_texts)

print(f"Computing similarities...")
sims_me5 = util.cos_sim(query_emb_me5, passage_embs_me5)[0]
ranked_me5 = torch.argsort(sims_me5, descending=True).cpu().numpy()

print(f"\nTop-5 with mE5-Large:")
for rank, idx in enumerate(ranked_me5[:5], 1):
    title = get_context_title(contexts[idx], '2wikimultihop')
    score = float(sims_me5[idx])
    is_gold = is_gold_passage(contexts[idx], '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [{rank}] {marker} {title[:50]:50s} ({score:.4f})")

# Find target
target_rank_me5 = None
for rank, idx in enumerate(ranked_me5, 1):
    title = get_context_title(contexts[idx], '2wikimultihop')
    if "el extraño viaje" in title.lower() and len(title) < 20:
        target_rank_me5 = rank
        target_score_me5 = float(sims_me5[idx])
        break

print(f"\n'El Extraño Viaje' passage:")
print(f"  Rank: {target_rank_me5}")
print(f"  Score: {target_score_me5:.4f}")

# Comparison
print(f"\n{'='*80}")
print("COMPARISON RESULTS")
print(f"{'='*80}")

print(f"\n'El Extraño Viaje' Target Passage:")
print(f"  IndoBERT rank: {target_rank_indobert} (score: {target_score_indobert:.4f})")
print(f"  mE5-Large rank: {target_rank_me5} (score: {target_score_me5:.4f})")

if target_rank_me5 < target_rank_indobert:
    improvement = target_rank_indobert - target_rank_me5
    print(f"\n  WINNER: mE5-Large (improved by {improvement} positions!)")
elif target_rank_me5 == target_rank_indobert:
    print(f"\n  TIE: Both models same ranking")
else:
    decline = target_rank_me5 - target_rank_indobert
    print(f"\n  WINNER: IndoBERT (mE5 worse by {decline} positions)")

# Score separation analysis
gold_indices = [i for i, c in enumerate(contexts) if is_gold_passage(c, '2wikimultihop')]
dist_indices = [i for i, c in enumerate(contexts) if not is_gold_passage(c, '2wikimultihop')]

gold_indobert = [float(sims_indobert[i]) for i in gold_indices]
dist_indobert = [float(sims_indobert[i]) for i in dist_indices]
sep_indobert = np.mean(gold_indobert) - np.mean(dist_indobert)

gold_me5 = [float(sims_me5[i]) for i in gold_indices]
dist_me5 = [float(sims_me5[i]) for i in dist_indices]
sep_me5 = np.mean(gold_me5) - np.mean(dist_me5)

print(f"\nGold/Distractor Separation:")
print(f"  IndoBERT: {sep_indobert:+.4f}")
print(f"  mE5-Large: {sep_me5:+.4f}")

if sep_me5 > sep_indobert:
    print(f"  → mE5 has better separation (+{sep_me5 - sep_indobert:.4f})")
else:
    print(f"  → IndoBERT has better separation (+{sep_indobert - sep_me5:.4f})")

# Recall@5
recall_indobert = sum(1 for idx in ranked_indobert[:5] if is_gold_passage(contexts[idx], '2wikimultihop'))
recall_me5 = sum(1 for idx in ranked_me5[:5] if is_gold_passage(contexts[idx], '2wikimultihop'))
num_gold = len(gold_indices)

print(f"\nRecall@5:")
print(f"  IndoBERT: {recall_indobert}/{num_gold} ({recall_indobert/num_gold*100:.0f}%)")
print(f"  mE5-Large: {recall_me5}/{num_gold} ({recall_me5/num_gold*100:.0f}%)")

print(f"\n{'='*80}")
print("FINAL VERDICT")
print(f"{'='*80}")

me5_wins = 0
if target_rank_me5 < target_rank_indobert: me5_wins += 1
if sep_me5 > sep_indobert: me5_wins += 1
if recall_me5 > recall_indobert: me5_wins += 1

if me5_wins >= 2:
    print(f"\nWINNER: mE5-Large")
    print(f"  Better on {me5_wins}/3 metrics")
    print(f"\n  Recommendation: USE mE5-Large for multilingual multi-hop QA")
    print(f"    Pros: Better Spanish/English handling")
    print(f"    Cons: Slower, larger model (560M params)")
else:
    print(f"\nWINNER: IndoBERT")
    print(f"  Better on {3-me5_wins}/3 metrics")
    print(f"\n  Recommendation: KEEP IndoBERT")
    print(f"    Pros: Faster, smaller model")
    print(f"    Cons: Weaker on Spanish/English")
```

## CELL: Test Multiple Samples (IndoBERT vs mE5)

```python
print("="*100)
print("MULTI-SAMPLE TEST: IndoBERT vs mE5-Large")
print("="*100)

num_samples = 10
wiki_samples = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[:num_samples]

results = {
    'indobert': {'recalls': [], 'separations': [], 'target_ranks': []},
    'me5': {'recalls': [], 'separations': [], 'target_ranks': []}
}

print(f"Testing {num_samples} samples...")

for sample_idx, sample in enumerate(tqdm(wiki_samples, desc="Processing"), 1):
    question = get_question(sample, '2wikimultihop')
    contexts = get_contexts(sample, '2wikimultihop')
    
    # Decompose and get Stage 1 entities
    decomposition = decompose_question_with_entities(question, '2wikimultihop')
    stage1 = decomposition['sub_questions'][0]
    entities = stage1.get('entities', [])
    
    if not entities:
        continue
    
    # Test query: use entities
    test_query = ' '.join(entities)
    passage_texts = [get_context_text(ctx, '2wikimultihop') for ctx in contexts]
    
    # IndoBERT
    query_emb_ib = model_indobert.encode(test_query, convert_to_tensor=True)
    passage_embs_ib = model_indobert.encode(passage_texts, convert_to_tensor=True)
    sims_ib = util.cos_sim(query_emb_ib, passage_embs_ib)[0]
    ranked_ib = torch.argsort(sims_ib, descending=True)[:5].cpu().numpy()
    
    # mE5
    query_emb_me5 = encode_query_me5(test_query)
    passage_embs_me5 = encode_passages_me5(passage_texts)
    sims_me5 = util.cos_sim(query_emb_me5, passage_embs_me5)[0]
    ranked_me5 = torch.argsort(sims_me5, descending=True)[:5].cpu().numpy()
    
    # Calculate metrics
    gold_indices = [i for i, c in enumerate(contexts) if is_gold_passage(c, '2wikimultihop')]
    dist_indices = [i for i, c in enumerate(contexts) if not is_gold_passage(c, '2wikimultihop')]
    
    if gold_indices and dist_indices:
        # Recall
        recall_ib = sum(1 for idx in ranked_ib if is_gold_passage(contexts[idx], '2wikimultihop')) / len(gold_indices)
        recall_me5 = sum(1 for idx in ranked_me5 if is_gold_passage(contexts[idx], '2wikimultihop')) / len(gold_indices)
        
        results['indobert']['recalls'].append(recall_ib)
        results['me5']['recalls'].append(recall_me5)
        
        # Separation
        sep_ib = np.mean([float(sims_ib[i]) for i in gold_indices]) - np.mean([float(sims_ib[i]) for i in dist_indices])
        sep_me5 = np.mean([float(sims_me5[i]) for i in gold_indices]) - np.mean([float(sims_me5[i]) for i in dist_indices])
        
        results['indobert']['separations'].append(sep_ib)
        results['me5']['separations'].append(sep_me5)

# Aggregate results
print(f"\n{'='*80}")
print(f"AGGREGATE RESULTS ({len(results['indobert']['recalls'])} samples)")
print(f"{'='*80}")

ib_recall_mean = np.mean(results['indobert']['recalls'])
ib_sep_mean = np.mean(results['indobert']['separations'])

me5_recall_mean = np.mean(results['me5']['recalls'])
me5_sep_mean = np.mean(results['me5']['separations'])

print(f"\nRecall@5:")
print(f"  IndoBERT:  {ib_recall_mean:.2%}")
print(f"  mE5-Large: {me5_recall_mean:.2%}")
print(f"  Improvement: {(me5_recall_mean - ib_recall_mean)*100:+.1f} pp")

print(f"\nScore Separation:")
print(f"  IndoBERT:  {ib_sep_mean:+.4f}")
print(f"  mE5-Large: {me5_sep_mean:+.4f}")
print(f"  Improvement: {(me5_sep_mean - ib_sep_mean):+.4f}")

print(f"\n{'='*80}")
print("FINAL RECOMMENDATION")
print(f"{'='*80}")

if me5_recall_mean > ib_recall_mean and me5_sep_mean > ib_sep_mean:
    print(f"\nUSE mE5-Large for 2WikiMultihop!")
    print(f"  Significantly better multilingual handling")
    print(f"  Worth the extra computational cost")
elif me5_recall_mean > ib_recall_mean + 0.05:  # At least 5pp improvement
    print(f"\nUSE mE5-Large for 2WikiMultihop!")
    print(f"  Better recall, worth the trade-off")
else:
    print(f"\nSTICK with IndoBERT")
    print(f"  Performance similar, but faster/smaller")
```

Jalankan 3 cells ini untuk:
1. Load mE5-large model
2. Compare single sample
3. Test 10 samples aggregate

**Expected:** mE5-Large should rank "El Extraño Viaje" **higher** (rank 1-2) vs IndoBERT (rank 4)!