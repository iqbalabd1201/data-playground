Ah! Ada **error** di SpaCy multilingual model. Error ini karena `noun_chunks` tidak di-support untuk language `'xx'` (multilingual).

## Fix: Handle Error untuk Multilingual Model

Berikut **fixed version** yang handle error ini:

```python
print("="*100)
print("NER ENTITY EXTRACTION - STAGE 1 QUESTION TEST (FIXED)")
print("="*100)

# Install dan load SpaCy NER
try:
    import spacy
    print("SpaCy already installed")
except:
    print("Installing SpaCy...")
    !pip install -q spacy
    import spacy

# Download models
print("\nDownloading SpaCy models...")
try:
    nlp_en = spacy.load("en_core_web_sm")
    print("English model loaded")
except:
    print("Downloading English model...")
    !python -m spacy download en_core_web_sm
    nlp_en = spacy.load("en_core_web_sm")

try:
    nlp_multi = spacy.load("xx_ent_wiki_sm")
    print("Multilingual model loaded")
except:
    print("Downloading Multilingual model...")
    !python -m spacy download xx_ent_wiki_sm
    nlp_multi = spacy.load("xx_ent_wiki_sm")

print("\nModels ready!")

# Function untuk extract entities (FIXED)
def extract_entities_ner(text, language='en'):
    """
    Extract entities using SpaCy NER
    Fixed: Handle noun_chunks error for multilingual model
    """
    if language == 'en':
        doc = nlp_en(text)
    else:
        doc = nlp_multi(text)
    
    entities = []
    
    # Named entities (works for all languages)
    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })
    
    # Noun chunks (only for English model - not supported in multilingual)
    if language == 'en':
        try:
            for chunk in doc.noun_chunks:
                # Only multi-word chunks
                if len(chunk.text.split()) >= 2:
                    # Check if not already in entities
                    if not any(chunk.text.lower() in e['text'].lower() for e in entities):
                        entities.append({
                            'text': chunk.text,
                            'label': 'NOUN_CHUNK',
                            'start': chunk.start_char,
                            'end': chunk.end_char
                        })
        except NotImplementedError:
            # Silently skip if noun_chunks not supported
            pass
    
    return entities

# Get samples
print("\n" + "="*100)
print("TEST 1: HOTPOTQA SAMPLE")
print("="*100)

hotpot_sample = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[0]
main_q_hotpot = get_question(hotpot_sample, 'hotpotqa')
gold_hotpot = get_answer(hotpot_sample, 'hotpotqa')

print(f"\nMain Question: {main_q_hotpot}")
print(f"Gold Answer: {gold_hotpot}")

# Decompose
print(f"\nDecomposing question...")
decomp_hotpot = decompose_question_visualized(main_q_hotpot, 'hotpotqa')

if decomp_hotpot and decomp_hotpot.get('sub_questions'):
    stage1_q_hotpot = decomp_hotpot['sub_questions'][0]['question']
    print(f"\nStage 1 Question: {stage1_q_hotpot}")
    
    # Extract entities from Stage 1 question
    print(f"\n{'-'*80}")
    print("EXTRACTING ENTITIES FROM STAGE 1 QUESTION")
    print(f"{'-'*80}")
    
    # Detect language (simple heuristic)
    if any(word in stage1_q_hotpot.lower() for word in ['kapan', 'siapa', 'apa', 'yang', 'dimana']):
        lang = 'id'
    else:
        lang = 'en'
    
    print(f"Detected language: {lang.upper()}")
    
    entities_hotpot = extract_entities_ner(stage1_q_hotpot, language=lang)
    
    print(f"\nFound {len(entities_hotpot)} entities:")
    if entities_hotpot:
        for i, ent in enumerate(entities_hotpot, 1):
            print(f"  {i}. \"{ent['text']}\" -> Type: {ent['label']}")
    else:
        print("  (No entities found by NER)")
    
    # Just entity texts for encoding
    entity_texts_hotpot = [e['text'] for e in entities_hotpot]
    print(f"\nEntity texts only: {entity_texts_hotpot}")
else:
    print("ERROR: Decomposition failed")
    entity_texts_hotpot = []

# Test 2: 2WikiMultihop
print("\n" + "="*100)
print("TEST 2: 2WIKIMULTIHOP SAMPLE")
print("="*100)

wiki_sample = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[0]
main_q_wiki = get_question(wiki_sample, '2wikimultihop')
gold_wiki = get_answer(wiki_sample, '2wikimultihop')

print(f"\nMain Question: {main_q_wiki}")
print(f"Gold Answer: {gold_wiki}")

# Decompose
print(f"\nDecomposing question...")
decomp_wiki = decompose_question_visualized(main_q_wiki, '2wikimultihop')

if decomp_wiki and decomp_wiki.get('sub_questions'):
    stage1_q_wiki = decomp_wiki['sub_questions'][0]['question']
    print(f"\nStage 1 Question: {stage1_q_wiki}")
    
    # Extract entities
    print(f"\n{'-'*80}")
    print("EXTRACTING ENTITIES FROM STAGE 1 QUESTION")
    print(f"{'-'*80}")
    
    # Detect language
    if any(word in stage1_q_wiki.lower() for word in ['kapan', 'siapa', 'apa', 'yang', 'dimana']):
        lang = 'id'
    else:
        lang = 'en'
    
    print(f"Detected language: {lang.upper()}")
    
    entities_wiki = extract_entities_ner(stage1_q_wiki, language=lang)
    
    print(f"\nFound {len(entities_wiki)} entities:")
    if entities_wiki:
        for i, ent in enumerate(entities_wiki, 1):
            print(f"  {i}. \"{ent['text']}\" -> Type: {ent['label']}")
    else:
        print("  (No entities found by NER)")
    
    # Entity texts only
    entity_texts_wiki = [e['text'] for e in entities_wiki]
    print(f"\nEntity texts only: {entity_texts_wiki}")
else:
    print("ERROR: Decomposition failed")
    entity_texts_wiki = []

# Summary
print("\n" + "="*100)
print("NER EXTRACTION SUMMARY")
print("="*100)

if decomp_hotpot:
    print(f"\nHotpotQA:")
    print(f"  Stage 1 Question: {stage1_q_hotpot}")
    print(f"  Entities found: {len(entity_texts_hotpot)}")
    if entity_texts_hotpot:
        print(f"  Entity list: {', '.join(entity_texts_hotpot)}")
    else:
        print(f"  Entity list: (none)")

if decomp_wiki:
    print(f"\n2WikiMultihop:")
    print(f"  Stage 1 Question: {stage1_q_wiki}")
    print(f"  Entities found: {len(entity_texts_wiki)}")
    if entity_texts_wiki:
        print(f"  Entity list: {', '.join(entity_texts_wiki)}")
    else:
        print(f"  Entity list: (none)")

# Analysis
print("\n" + "="*100)
print("ANALYSIS: DID NER CAPTURE KEY ENTITIES?")
print("="*100)

if decomp_hotpot:
    print("\nHotpotQA:")
    print(f"  Stage 1 Q: {stage1_q_hotpot}")
    print(f"  Expected key entities: 'Arthur's Magazine' or similar")
    
    if entity_texts_hotpot:
        found_arthur = any("arthur" in e.lower() for e in entity_texts_hotpot)
        found_magazine = any("magazine" in e.lower() or "majalah" in e.lower() for e in entity_texts_hotpot)
        print(f"  Found 'Arthur': {'YES' if found_arthur else 'NO'}")
        print(f"  Found 'Magazine': {'YES' if found_magazine else 'NO'}")
        
        if found_arthur or found_magazine:
            print(f"  Status: PARTIAL - NER found some entities")
        else:
            print(f"  Status: FAILED - Key entities not found")
    else:
        print(f"  Status: FAILED - No entities extracted")

if decomp_wiki:
    print("\n2WikiMultihop:")
    print(f"  Stage 1 Q: {stage1_q_wiki}")
    print(f"  Expected key entities: 'El Extraño Viaje', 'sutradara'/'director'")
    
    if entity_texts_wiki:
        found_film = any("extraño" in e.lower() or "viaje" in e.lower() or "el" in e.lower() for e in entity_texts_wiki)
        found_director = any("director" in e.lower() or "sutradara" in e.lower() for e in entity_texts_wiki)
        print(f"  Found film name: {'YES' if found_film else 'NO'}")
        print(f"  Found 'director': {'YES' if found_director else 'NO'}")
        
        if found_film or found_director:
            print(f"  Status: PARTIAL - NER found some entities")
        else:
            print(f"  Status: FAILED - Key entities not found")
    else:
        print(f"  Status: FAILED - No entities extracted")

print("\n" + "="*100)
print("CONCLUSION")
print("="*100)

if not entity_texts_hotpot and not entity_texts_wiki:
    print("\nWARNING: NER extracted NO entities from either question!")
    print("\nPossible reasons:")
    print("  1. SpaCy multilingual model has limited entity coverage")
    print("  2. Indonesian/mixed language questions are challenging")
    print("  3. Entity types (magazine names, film titles) may not be in training data")
    print("\nRECOMMENDATION:")
    print("  Use REGEX + Domain Keywords approach instead of pure NER")
    print("  Or use HYBRID: NER + Regex fallback")
else:
    total_found = len(entity_texts_hotpot) + len(entity_texts_wiki)
    print(f"\nNER extracted {total_found} total entities")
    print(f"  HotpotQA: {len(entity_texts_hotpot)} entities")
    print(f"  2WikiMultihop: {len(entity_texts_wiki)} entities")
    
    if total_found >= 3:
        print("\n  Status: NER works reasonably well")
    else:
        print("\n  Status: NER has limited coverage")
        print("  Recommendation: Add Regex fallback for better coverage")

print("\n" + "="*100)
```

## Key Changes:

1. **Added try-except** untuk `noun_chunks`:
```python
if language == 'en':
    try:
        for chunk in doc.noun_chunks:
            # ... process noun chunks
    except NotImplementedError:
        pass  # Skip if not supported
```

2. **Better handling** jika no entities found

3. **More detailed analysis** dengan expected entities

Jalankan ini dan lihat hasilnya! Kemungkinan besar NER akan struggle dengan Indonesian mixed dengan entity names, jadi kita bisa compare dengan Regex approach.