Ya **BENAR**! Ini vector similarity dari **question** ke **passage**.

## Penjelasan Detail:

### Di CELL 6: Retrieval Functions

```python
def retrieve_passages_indobert(question, contexts, dataset_name, k=5):
    # 1. Extract semua passage texts
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    
    # 2. Encode QUESTION menjadi vector
    query_embedding = model_indobert.encode(question, convert_to_tensor=True)
    #                                      ^^^^^^^^
    #                                      INI QUESTION
    
    # 3. Encode semua PASSAGES menjadi vectors
    passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
    #                                          ^^^^^^^^^^^^^^
    #                                          INI PASSAGES
    
    # 4. Hitung COSINE SIMILARITY antara question vector dan passage vectors
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    #                           ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^
    #                           QUESTION (1 vector)  PASSAGES (N vectors)
    
    # 5. Ranking berdasarkan similarity score (highest = most relevant)
    top_k_indices = torch.argsort(similarities, descending=True)[:k]
    
    return retrieved
```

---

## Visual Explanation:

```
INPUT:
  Question: "Majalah mana yang didirikan lebih dulu?"
  Passages: [P1, P2, P3, ..., P10]

STEP 1: Encode Question
  Question → [0.23, 0.45, -0.12, ..., 0.67]  (768-dim vector)
           │
           └─ Query Embedding

STEP 2: Encode All Passages
  P1 → [0.15, 0.38, -0.09, ..., 0.54]
  P2 → [0.28, 0.42, -0.15, ..., 0.71]  ← Arthur's Magazine (relevan!)
  P3 → [0.11, 0.22, -0.03, ..., 0.33]
  ...
  P10 → [0.09, 0.19, -0.06, ..., 0.28]
        │
        └─ Passage Embeddings

STEP 3: Compute Cosine Similarity
  sim(Query, P1)  = 0.62
  sim(Query, P2)  = 0.89  ← HIGHEST! (most similar)
  sim(Query, P3)  = 0.45
  ...
  sim(Query, P10) = 0.38

STEP 4: Ranking
  Rank 1: P2 (0.89) ← Arthur's Magazine
  Rank 2: P1 (0.62)
  Rank 3: P7 (0.58)
  ...
  Rank 10: P10 (0.38)

OUTPUT:
  Top-K passages (K=5) = [P2, P1, P7, P4, P9]
```

---

## Ini BUKAN Passage-to-Passage!

### Question-to-Passage (Q2P) - Yang Digunakan:
```python
similarities = util.cos_sim(query_embedding, passage_embeddings)
#                           ^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^
#                           1 vector         N vectors
#                           (Question)       (All Passages)
# Result: [N similarities] - satu score per passage
```

### Passage-to-Passage (P2P) - Yang Di CELL 10 (improvement):
```python
similarity_matrix = util.cos_sim(passage_embeddings, passage_embeddings)
#                                ^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^
#                                N vectors            N vectors
#                                (All Passages)       (All Passages)
# Result: [N x N matrix] - similarity antara setiap passage pair
```

---

## Kenapa Question-to-Passage?

### 1. **Semantic Matching**
```
Question: "Majalah mana yang didirikan lebih dulu?"
Semantic: [magazine, founding, date, earlier, comparison]

Passage (Arthur's Magazine):
"Arthur's Magazine (1844–1846) was an American literary periodical..."
Semantic: [magazine, 1844, American, periodical, literature]

Similarity: HIGH (0.89) ← Ada overlap semantic!
```

### 2. **Dense Retrieval Advantage**
- **Sparse (BM25)**: Hanya match exact words
  - Query: "didirikan lebih dulu"
  - Passage: "founded in 1844"
  - Match: ❌ (different words)

- **Dense (BERT/mE5)**: Match semantic meaning
  - Query vector: captures "founding date comparison"
  - Passage vector: captures "magazine founded 1844"
  - Match: ✅ (same meaning, different words!)

---

## Cosine Similarity Formula:

```python
cos_sim(A, B) = (A · B) / (||A|| * ||B||)
```

### Example:
```
Query vector:   [0.5, 0.3, 0.8]
Passage vector: [0.6, 0.2, 0.7]

Dot product: (0.5*0.6) + (0.3*0.2) + (0.8*0.7) = 0.30 + 0.06 + 0.56 = 0.92
||Query||:   sqrt(0.5² + 0.3² + 0.8²) = 1.02
||Passage||: sqrt(0.6² + 0.2² + 0.7²) = 0.94

Cosine Similarity = 0.92 / (1.02 * 0.94) = 0.959

Score: 0.959 (very similar!)
```

---

## Comparison: Different Similarity Methods

### Method 1: Cosine Similarity (Current)
```python
similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
# Range: -1 to 1 (biasanya 0 to 1 untuk text)
# Higher = more similar
```

### Method 2: Dot Product
```python
similarities = torch.matmul(query_embedding, passage_embeddings.T)
# Range: unbounded
# Magnitude matters
```

### Method 3: Euclidean Distance
```python
distances = torch.cdist(query_embedding.unsqueeze(0), passage_embeddings)
# Range: 0 to infinity
# Lower = more similar (inverse!)
```

**Cosine Similarity** adalah yang paling umum untuk text retrieval karena:
- Normalized (tidak terpengaruh panjang vector)
- Fokus pada direction (semantic meaning)
- Range 0-1 mudah diinterpret

---

## Test: Apakah Memang Q2P?

Tambahkan cell debug ini untuk verifikasi:

```python
print("="*80)
print("DEBUG: Verifikasi Question-to-Passage Similarity")
print("="*80)

# Get sample
sample = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[0]
question = get_question(sample, 'hotpotqa')
contexts = get_contexts(sample, 'hotpotqa')

print(f"\nQuestion: {question}")
print(f"Number of passages: {len(contexts)}")

# Manual computation untuk verifikasi
passage_texts = [get_context_text(ctx, 'hotpotqa') for ctx in contexts]

# Encode
query_emb = model_indobert.encode(question, convert_to_tensor=True)
passage_embs = model_indobert.encode(passage_texts, convert_to_tensor=True)

print(f"\nQuery embedding shape: {query_emb.shape}")
print(f"  → This is 1 vector for the question")

print(f"\nPassage embeddings shape: {passage_embs.shape}")
print(f"  → This is {len(contexts)} vectors, one for each passage")

# Compute similarity
similarities = util.cos_sim(query_emb, passage_embs)[0]

print(f"\nSimilarity scores shape: {similarities.shape}")
print(f"  → {len(contexts)} scores, one for each passage")

print(f"\nSimilarity scores:")
for i, (ctx, score) in enumerate(zip(contexts, similarities)):
    title = get_context_title(ctx, 'hotpotqa')
    is_gold = is_gold_passage(ctx, 'hotpotqa')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  {i+1:2d}. {marker} {title[:50]:50s} = {score:.4f}")

print(f"\nTop-5 passage indices: {torch.argsort(similarities, descending=True)[:5].tolist()}")
print("\nConclusion: YES, this is Question-to-Passage similarity!")
print("  - 1 query vector compared to N passage vectors")
print("  - Each passage gets 1 similarity score")
print("  - Higher score = passage more relevant to question")
```

Expected output:
```
Query embedding shape: torch.Size([768])
  → This is 1 vector for the question

Passage embeddings shape: torch.Size([10, 768])
  → This is 10 vectors, one for each passage

Similarity scores shape: torch.Size([10])
  → 10 scores, one for each passage

Conclusion: YES, this is Question-to-Passage similarity!
```

---

## Summary:

✅ **Ya, ini Question-to-Passage (Q2P) similarity**

- **Input**: 1 question + N passages
- **Process**: Encode → Compute cosine similarity
- **Output**: N similarity scores
- **Ranking**: Sort by score, return top-K

Ini adalah **standard dense retrieval approach** yang digunakan di semua BERT-based retrieval systems!