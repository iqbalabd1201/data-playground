Ah betul! **Retrieve based on full passage text**, bukan cuma title! Fix:

```python
# ==================== FIX: RETRIEVE BY FULL PASSAGE, NOT TITLE ====================
print("="*100)
print("FIX: Dense Retrieval Using FULL PASSAGE TEXT")
print("="*100)

def retrieve_passages_dense_fixed(question, contexts, dataset_name, k=3):
    """
    Dense retrieval using FULL passage text (not just title)
    """
    # Encode question
    question_emb = embedding_model.encode(question, convert_to_tensor=True, device=device)
    
    # Encode FULL passage texts (not titles!)
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    passage_embs = embedding_model.encode(passage_texts, convert_to_tensor=True, device=device)
    
    # Compute similarities
    similarities = torch.nn.functional.cosine_similarity(
        question_emb.unsqueeze(0), 
        passage_embs
    )
    
    # Get top-k
    top_k_indices = torch.topk(similarities, min(k, len(contexts))).indices.cpu().tolist()
    
    # Build retrieved passages with metadata
    retrieved = []
    for rank, idx in enumerate(top_k_indices, 1):
        ctx = contexts[idx].copy()
        ctx['retrieval_rank'] = rank
        ctx['retrieval_score'] = similarities[idx].item()
        retrieved.append(ctx)
    
    return retrieved

# Override the old function
retrieve_passages_dense = retrieve_passages_dense_fixed

print("✓ Fixed: Dense retrieval now uses FULL passage text")
print("✓ Similarity computed on: passage content, not title")

# Quick test
print("\n" + "="*100)
print("QUICK TEST: Retrieval Quality Check")
print("="*100)

sample = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[0]

question = get_question(sample, 'hotpotqa')
passages = get_contexts(sample, 'hotpotqa')

print(f"Question: {question}")
print(f"\nRetrieving top-5 passages based on FULL TEXT similarity...")

retrieved = retrieve_passages_dense(question, passages, 'hotpotqa', k=5)

for p in retrieved:
    title = get_context_title(p, 'hotpotqa')
    score = p.get('retrieval_score', 0)
    rank = p.get('retrieval_rank', 0)
    text = get_context_text(p, 'hotpotqa')[:150]
    is_gold = is_gold_passage(p, 'hotpotqa')
    marker = "✓" if is_gold else "✗"
    
    print(f"\n[{rank}] {marker} {title} (score: {score:.4f})")
    print(f"    Text preview: {text}...")

print("\n✓ Retrieval now based on full passage content!")
```

Sekarang **cosine similarity** computed on **full passage text**, bukan title! 

Re-run test 10 samples dengan fix ini:

```python
# ==================== RE-RUN: 10 SAMPLES WITH FIXED RETRIEVAL ====================
print("\n" + "="*100)
print("RE-RUN: 10 HOTPOTQA SAMPLES WITH FIXED RETRIEVAL")
print("="*100)

# Copy the complete test code from before, it will use the fixed retrieve_passages_dense

start_time = time.time()

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:10]
all_results = []

for i, sample in enumerate(hotpot_samples, 1):
    try:
        result = test_sample_verbose(sample, i, 'hotpotqa')
        all_results.append(result)
    except Exception as e:
        print(f"\n⚠ Error on sample {i}: {e}")
        all_results.append({'sample_id': i, 'error': str(e), 'em': 0, 'f1': 0})

elapsed_time = time.time() - start_time

# Summary (same as before)
print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

valid_results = [r for r in all_results if 'error' not in r]

if valid_results:
    avg_em = np.mean([r['em'] for r in valid_results])
    avg_f1 = np.mean([r['f1'] for r in valid_results])
    
    print(f"EM: {avg_em*100:.1f}%")
    print(f"F1: {avg_f1:.3f}")
    print(f"Time: {elapsed_time:.1f}s")
```

Atau kalau sudah ada embedding model loaded, retrieval harusnya sudah benar. Cek apakah di **Cell 1** embedding model sudah di-load dengan benar! 🚀