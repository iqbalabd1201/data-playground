Oke! Saya buatkan **FULL CODE** dari decomposition dengan entity extraction sampai retrieval comparison!

## CELL 1: Improved Decomposition WITH Entity Extraction

```python
print("="*100)
print("IMPROVED DECOMPOSITION: WITH ENTITY EXTRACTION BUILT-IN")
print("="*100)

import re

def extract_entities_simple(text):
    """
    Simple but effective entity extraction
    No external dependencies needed
    """
    entities = []
    
    # 1. Capitalized sequences (Names, Titles)
    # "El Extraño Viaje", "Arthur's Magazine", "Love In Pawn"
    cap_pattern = r'\b[A-Z][a-zA-Z\'\-]+(?:\s+[A-Z][a-zA-Z\'\-]+)*\b'
    capitalized = re.findall(cap_pattern, text)
    entities.extend(capitalized)
    
    # 2. Key concepts - Indonesian
    concepts_id = ['sutradara', 'direktur', 'aktor', 'aktris', 'penulis',
                   'film', 'majalah', 'negara', 'kota', 'lahir', 'didirikan',
                   'tempat', 'tanggal', 'waktu']
    for concept in concepts_id:
        if concept in text.lower():
            entities.append(concept)
    
    # 3. Key concepts - English  
    concepts_en = ['director', 'actor', 'actress', 'writer', 'film', 'movie',
                   'magazine', 'country', 'city', 'born', 'founded', 'place',
                   'date', 'time', 'when', 'where', 'who']
    for concept in concepts_en:
        if concept in text.lower():
            entities.append(concept)
    
    # 4. Quoted text
    quoted = re.findall(r'["\']([^"\']+)["\']', text)
    entities.extend(quoted)
    
    # 5. Years (important for temporal questions)
    years = re.findall(r'\b(18|19|20)\d{2}\b', text)
    entities.extend(years)
    
    # Remove stopwords
    stopwords = {'the', 'a', 'an', 'is', 'was', 'are', 'yang', 'di', 'ke', 'dan', 'atau', 'or', 'and'}
    entities = [e for e in entities if e.lower() not in stopwords]
    
    # Remove duplicates (case-insensitive)
    seen = set()
    unique = []
    for ent in entities:
        ent_clean = ent.strip()
        if ent_clean and ent_clean.lower() not in seen and len(ent_clean) > 1:
            seen.add(ent_clean.lower())
            unique.append(ent_clean)
    
    return unique

def decompose_question_with_entities(question, dataset_name):
    """
    Decompose question AND extract entities from each sub-question
    All in one step - more efficient!
    """
    
    decomposition_prompt = f"""Analyze this multi-hop question and decompose it into sequential sub-questions.

QUESTION: {question}

QUESTION TYPES:
1. COMPARISON: Compare two entities
2. BRIDGE: Find intermediate entity first
3. SIMPLE: Direct question

Return JSON with: question_type, reasoning, num_stages, sub_questions

JSON:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Decompose multi-hop questions into sub-questions. Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": decomposition_prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)
        
        # Extract entities from ORIGINAL question
        main_entities = extract_entities_simple(question)
        
        # Extract entities from EACH sub-question
        if 'sub_questions' in result:
            for sq in result['sub_questions']:
                sq_text = sq['question']
                sq_entities = extract_entities_simple(sq_text)
                
                # Add entities to sub_question structure
                sq['entities'] = sq_entities
                sq['entity_count'] = len(sq_entities)
                sq['entity_query'] = ' '.join(sq_entities)  # Ready for encoding
        
        # Add main question entities
        result['main_question_entities'] = main_entities
        
        return result

    except Exception as e:
        print(f"Error: {e}")
        # Fallback
        entities = extract_entities_simple(question)
        return {
            'question_type': 'simple',
            'reasoning': 'Decomposition failed',
            'num_stages': 1,
            'sub_questions': [{
                'stage': 1,
                'question': question,
                'purpose': 'Answer directly',
                'depends_on': [],
                'entities': entities,
                'entity_count': len(entities),
                'entity_query': ' '.join(entities)
            }],
            'main_question_entities': entities
        }

print("Improved decomposition function loaded")
print("  - Extracts entities during decomposition")
print("  - Stores entities with each sub-question")
print("  - Ready for entity-based retrieval")
```

## CELL 2: Retrieval Functions (Full Text vs Entity-Based)

```python
print("="*100)
print("RETRIEVAL FUNCTIONS: FULL TEXT vs ENTITY-BASED")
print("="*100)

def retrieve_passages_fulltext(question_text, contexts, dataset_name, k=5):
    """
    Traditional: Full text query encoding
    """
    # Encode full question text
    query_embedding = model_indobert.encode(question_text, convert_to_tensor=True)
    
    # Encode passages (full text)
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
    
    # Compute similarity
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    
    # Rank
    top_k_indices = torch.argsort(similarities, descending=True)[:k].cpu().numpy()
    
    # Return
    retrieved = []
    for rank, idx in enumerate(top_k_indices):
        ctx = contexts[idx].copy()
        ctx['retrieval_score'] = float(similarities[idx])
        ctx['retrieval_rank'] = rank + 1
        ctx['method'] = 'fulltext'
        retrieved.append(ctx)
    
    return retrieved

def retrieve_passages_entity_based(entities, question_text, contexts, dataset_name, k=5):
    """
    New: Entity-only query encoding
    """
    if not entities:
        # Fallback to full text if no entities
        print("    Warning: No entities, falling back to full text")
        return retrieve_passages_fulltext(question_text, contexts, dataset_name, k)
    
    # Encode entities only
    entity_query = ' '.join(entities)
    query_embedding = model_indobert.encode(entity_query, convert_to_tensor=True)
    
    # Encode passages (full text)
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
    
    # Compute similarity
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    
    # Rank
    top_k_indices = torch.argsort(similarities, descending=True)[:k].cpu().numpy()
    
    # Return
    retrieved = []
    for rank, idx in enumerate(top_k_indices):
        ctx = contexts[idx].copy()
        ctx['retrieval_score'] = float(similarities[idx])
        ctx['retrieval_rank'] = rank + 1
        ctx['method'] = 'entity'
        ctx['query_entities'] = entities
        retrieved.append(ctx)
    
    return retrieved

def retrieve_with_stage_decomposition(stage_obj, contexts, dataset_name, method='entity', k=5):
    """
    Retrieve using stage decomposition object
    Automatically uses pre-extracted entities
    """
    question_text = stage_obj['question']
    entities = stage_obj.get('entities', [])
    
    if method == 'entity':
        return retrieve_passages_entity_based(entities, question_text, contexts, dataset_name, k)
    else:
        return retrieve_passages_fulltext(question_text, contexts, dataset_name, k)

print("Retrieval functions loaded")
print("  - retrieve_passages_fulltext: Traditional approach")
print("  - retrieve_passages_entity_based: Entity-only query")
print("  - retrieve_with_stage_decomposition: Uses pre-extracted entities")
```

## CELL 3: Complete Test & Comparison

```python
print("="*100)
print("COMPLETE TEST: FULL TEXT vs ENTITY-BASED RETRIEVAL")
print("="*100)

# Get sample
wiki_sample = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[0]
question = get_question(wiki_sample, '2wikimultihop')
gold_answer = get_answer(wiki_sample, '2wikimultihop')
contexts = get_contexts(wiki_sample, '2wikimultihop')

print(f"Main Question: {question}")
print(f"Gold Answer: {gold_answer}")
print(f"Total passages: {len(contexts)}")

# Count gold passages
num_gold = sum(1 for c in contexts if is_gold_passage(c, '2wikimultihop'))
print(f"Gold passages: {num_gold}")

# Step 1: Decompose with entity extraction
print(f"\n{'='*80}")
print("STEP 1: DECOMPOSE WITH ENTITY EXTRACTION")
print(f"{'='*80}")

decomposition = decompose_question_with_entities(question, '2wikimultihop')

print(f"\nQuestion Type: {decomposition.get('question_type', 'unknown')}")
print(f"Number of Stages: {decomposition.get('num_stages', 0)}")
print(f"Main Question Entities: {decomposition.get('main_question_entities', [])}")

print(f"\nSub-questions:")
for sq in decomposition.get('sub_questions', []):
    print(f"\n  Stage {sq['stage']}:")
    print(f"    Question: {sq['question']}")
    print(f"    Entities ({sq.get('entity_count', 0)}): {sq.get('entities', [])}")

# Step 2: Test Stage 1 - Both Methods
stage1 = decomposition['sub_questions'][0]
stage1_question = stage1['question']
stage1_entities = stage1.get('entities', [])

print(f"\n{'='*80}")
print("STEP 2: STAGE 1 RETRIEVAL COMPARISON")
print(f"{'='*80}")

print(f"\nStage 1 Question: {stage1_question}")
print(f"Stage 1 Entities: {stage1_entities}")

# Method 1: Full Text Query
print(f"\n{'-'*80}")
print("METHOD 1: FULL TEXT QUERY")
print(f"{'-'*80}")
print(f"Query: \"{stage1_question}\"")

retrieved_fulltext = retrieve_passages_fulltext(stage1_question, contexts, '2wikimultihop', k=5)

print(f"\nTop-5 Results (Full Text):")
for p in retrieved_fulltext:
    title = get_context_title(p, '2wikimultihop')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [{p['retrieval_rank']}] {marker} {title[:50]:50s} ({score:.4f})")

recall_fulltext, gold_fulltext, _ = compute_recall_at_k(
    retrieved_fulltext, contexts, '2wikimultihop', k=5
)
print(f"\nRecall@5: {recall_fulltext:.2%} ({gold_fulltext}/{num_gold})")

# Method 2: Entity-Based Query
print(f"\n{'-'*80}")
print("METHOD 2: ENTITY-BASED QUERY")
print(f"{'-'*80}")
print(f"Query Entities: {stage1_entities}")
print(f"Entity Query String: \"{' '.join(stage1_entities)}\"")

retrieved_entity = retrieve_passages_entity_based(
    stage1_entities, stage1_question, contexts, '2wikimultihop', k=5
)

print(f"\nTop-5 Results (Entity-Based):")
for p in retrieved_entity:
    title = get_context_title(p, '2wikimultihop')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    entities_used = ', '.join(p.get('query_entities', []))
    print(f"  [{p['retrieval_rank']}] {marker} {title[:50]:50s} ({score:.4f})")
    if p['retrieval_rank'] == 1:
        print(f"       Using entities: [{entities_used}]")

recall_entity, gold_entity, _ = compute_recall_at_k(
    retrieved_entity, contexts, '2wikimultihop', k=5
)
print(f"\nRecall@5: {recall_entity:.2%} ({gold_entity}/{num_gold})")

# Comparison
print(f"\n{'='*80}")
print("COMPARISON RESULTS")
print(f"{'='*80}")

print(f"\nRecall@5:")
print(f"  Full Text:    {recall_fulltext:.2%} ({gold_fulltext}/{num_gold})")
print(f"  Entity-Based: {recall_entity:.2%} ({gold_entity}/{num_gold})")
print(f"  Difference:   {(recall_entity - recall_fulltext)*100:+.1f} percentage points")

# Score analysis
passage_texts = [get_context_text(ctx, '2wikimultihop') for ctx in contexts]
passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)

# Full text similarities
fulltext_emb = model_indobert.encode(stage1_question, convert_to_tensor=True)
fulltext_sims = util.cos_sim(fulltext_emb, passage_embeddings)[0].cpu().numpy()

# Entity similarities
entity_query = ' '.join(stage1_entities)
entity_emb = model_indobert.encode(entity_query, convert_to_tensor=True)
entity_sims = util.cos_sim(entity_emb, passage_embeddings)[0].cpu().numpy()

# Gold vs Distractor scores
gold_indices = [i for i, c in enumerate(contexts) if is_gold_passage(c, '2wikimultihop')]
dist_indices = [i for i, c in enumerate(contexts) if not is_gold_passage(c, '2wikimultihop')]

gold_fulltext_scores = [fulltext_sims[i] for i in gold_indices]
dist_fulltext_scores = [fulltext_sims[i] for i in dist_indices]

gold_entity_scores = [entity_sims[i] for i in gold_indices]
dist_entity_scores = [entity_sims[i] for i in dist_indices]

print(f"\n{'-'*80}")
print("SCORE DISTRIBUTION ANALYSIS")
print(f"{'-'*80}")

print(f"\nFull Text Query:")
print(f"  Gold mean:       {np.mean(gold_fulltext_scores):.4f}")
print(f"  Distractor mean: {np.mean(dist_fulltext_scores):.4f}")
print(f"  Separation:      {np.mean(gold_fulltext_scores) - np.mean(dist_fulltext_scores):+.4f}")

print(f"\nEntity-Based Query:")
print(f"  Gold mean:       {np.mean(gold_entity_scores):.4f}")
print(f"  Distractor mean: {np.mean(dist_entity_scores):.4f}")
print(f"  Separation:      {np.mean(gold_entity_scores) - np.mean(dist_entity_scores):+.4f}")

# Determine winner
sep_fulltext = np.mean(gold_fulltext_scores) - np.mean(dist_fulltext_scores)
sep_entity = np.mean(gold_entity_scores) - np.mean(dist_entity_scores)

print(f"\n{'='*80}")
print("FINAL VERDICT")
print(f"{'='*80}")

if recall_entity > recall_fulltext:
    winner = "ENTITY-BASED"
    improvement = (recall_entity - recall_fulltext) * 100
    print(f"\nWINNER: {winner} (+{improvement:.1f} pp)")
elif recall_entity < recall_fulltext:
    winner = "FULL TEXT"
    improvement = (recall_fulltext - recall_entity) * 100
    print(f"\nWINNER: {winner} (+{improvement:.1f} pp)")
else:
    winner = "TIE"
    print(f"\nRESULT: {winner}")

if sep_entity > sep_fulltext:
    print(f"\nEntity-based has BETTER separation:")
    print(f"  Entity separation: {sep_entity:+.4f}")
    print(f"  Full text separation: {sep_fulltext:+.4f}")
    print(f"  -> Gold passages rank higher with entity queries")
else:
    print(f"\nFull text has BETTER separation:")
    print(f"  Full text separation: {sep_fulltext:+.4f}")
    print(f"  Entity separation: {sep_entity:+.4f}")
    print(f"  -> Semantic context helps distinguish gold passages")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")

print(f"\nFull Text Approach:")
print(f"  Pros: Captures semantic context")
print(f"  Cons: Diluted by function words")
print(f"  Recall@5: {recall_fulltext:.2%}")
print(f"  Separation: {sep_fulltext:+.4f}")

print(f"\nEntity-Based Approach:")
print(f"  Pros: Focused on key entities, less noise")
print(f"  Cons: May miss semantic relationships")
print(f"  Recall@5: {recall_entity:.2%}")
print(f"  Separation: {sep_entity:+.4f}")

print(f"\nRecommendation:")
if recall_entity > recall_fulltext and sep_entity > sep_fulltext:
    print(f"  Use ENTITY-BASED for this dataset")
elif recall_fulltext > recall_entity and sep_fulltext > sep_entity:
    print(f"  Use FULL TEXT for this dataset")
else:
    print(f"  Consider HYBRID approach (combine both)")
```

## CELL 4: Test Multiple Samples

```python
print("="*100)
print("MULTI-SAMPLE TEST: FULL TEXT vs ENTITY-BASED")
print("="*100)

num_test_samples = 10

# Storage
results = {
    'fulltext': {'recalls': [], 'separations': []},
    'entity': {'recalls': [], 'separations': []}
}

# Get samples
wiki_samples = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[:num_test_samples]

print(f"Testing {num_test_samples} samples...")

for sample_idx, sample in enumerate(tqdm(wiki_samples, desc="Testing"), 1):
    question = get_question(sample, '2wikimultihop')
    contexts = get_contexts(sample, '2wikimultihop')
    
    # Decompose with entities
    decomposition = decompose_question_with_entities(question, '2wikimultihop')
    stage1 = decomposition['sub_questions'][0]
    stage1_question = stage1['question']
    stage1_entities = stage1.get('entities', [])
    
    # Test Full Text
    retrieved_ft = retrieve_passages_fulltext(stage1_question, contexts, '2wikimultihop', k=5)
    recall_ft, _, total_gold = compute_recall_at_k(retrieved_ft, contexts, '2wikimultihop', k=5)
    results['fulltext']['recalls'].append(recall_ft)
    
    # Test Entity-Based
    retrieved_ent = retrieve_passages_entity_based(stage1_entities, stage1_question, contexts, '2wikimultihop', k=5)
    recall_ent, _, _ = compute_recall_at_k(retrieved_ent, contexts, '2wikimultihop', k=5)
    results['entity']['recalls'].append(recall_ent)
    
    # Score separation
    passage_texts = [get_context_text(ctx, '2wikimultihop') for ctx in contexts]
    passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
    
    # Full text
    ft_emb = model_indobert.encode(stage1_question, convert_to_tensor=True)
    ft_sims = util.cos_sim(ft_emb, passage_embeddings)[0].cpu().numpy()
    
    # Entity
    if stage1_entities:
        ent_query = ' '.join(stage1_entities)
        ent_emb = model_indobert.encode(ent_query, convert_to_tensor=True)
        ent_sims = util.cos_sim(ent_emb, passage_embeddings)[0].cpu().numpy()
    else:
        ent_sims = ft_sims  # Fallback
    
    # Calculate separations
    gold_indices = [i for i, c in enumerate(contexts) if is_gold_passage(c, '2wikimultihop')]
    dist_indices = [i for i, c in enumerate(contexts) if not is_gold_passage(c, '2wikimultihop')]
    
    if gold_indices and dist_indices:
        sep_ft = np.mean([ft_sims[i] for i in gold_indices]) - np.mean([ft_sims[i] for i in dist_indices])
        sep_ent = np.mean([ent_sims[i] for i in gold_indices]) - np.mean([ent_sims[i] for i in dist_indices])
        
        results['fulltext']['separations'].append(sep_ft)
        results['entity']['separations'].append(sep_ent)

# Calculate statistics
print(f"\n{'='*80}")
print(f"AGGREGATE RESULTS ({num_test_samples} samples)")
print(f"{'='*80}")

ft_recall_mean = np.mean(results['fulltext']['recalls'])
ft_recall_std = np.std(results['fulltext']['recalls'])
ft_sep_mean = np.mean(results['fulltext']['separations'])

ent_recall_mean = np.mean(results['entity']['recalls'])
ent_recall_std = np.std(results['entity']['recalls'])
ent_sep_mean = np.mean(results['entity']['separations'])

print(f"\nRecall@5:")
print(f"  Full Text:    {ft_recall_mean:.2%} ± {ft_recall_std:.2%}")
print(f"  Entity-Based: {ent_recall_mean:.2%} ± {ent_recall_std:.2%}")
print(f"  Improvement:  {(ent_recall_mean - ft_recall_mean)*100:+.1f} pp")

print(f"\nGold/Distractor Separation:")
print(f"  Full Text:    {ft_sep_mean:+.4f}")
print(f"  Entity-Based: {ent_sep_mean:+.4f}")
print(f"  Improvement:  {(ent_sep_mean - ft_sep_mean):+.4f}")

print(f"\n{'='*80}")
print("FINAL CONCLUSION")
print(f"{'='*80}")

if ent_recall_mean > ft_recall_mean and ent_sep_mean > ft_sep_mean:
    print(f"\nEntity-Based is BETTER on both metrics!")
    print(f"  Recommendation: Use entity-based retrieval for Stage 1")
elif ft_recall_mean > ent_recall_mean and ft_sep_mean > ent_sep_mean:
    print(f"\nFull Text is BETTER on both metrics!")
    print(f"  Recommendation: Stick with full text retrieval")
else:
    print(f"\nMixed results - each method has advantages")
    print(f"  Recommendation: Use hybrid approach or tune per dataset")
```

Jalankan semua 4 cells ini secara berurutan untuk test lengkap!

**Expected Output:** Comparison lengkap antara Full Text vs Entity-Based retrieval dengan metrics: Recall@5, Score Separation, dan aggregate statistics dari 10 samples!