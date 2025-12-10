Oke! Saya buatkan **1 cell lengkap** untuk test NER di Stage 1 question!

## CELL: NER Extract Entities dari Stage 1 Question

```python
print("="*100)
print("NER ENTITY EXTRACTION - STAGE 1 QUESTION TEST")
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

# Function untuk extract entities
def extract_entities_ner(text, language='en'):
    """
    Extract entities using SpaCy NER
    """
    if language == 'en':
        doc = nlp_en(text)
    else:
        doc = nlp_multi(text)
    
    entities = []
    
    # Named entities
    for ent in doc.ents:
        entities.append({
            'text': ent.text,
            'label': ent.label_,
            'start': ent.start_char,
            'end': ent.end_char
        })
    
    # Noun chunks (additional potential entities)
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
    if any(word in stage1_q_hotpot.lower() for word in ['kapan', 'siapa', 'apa', 'yang']):
        lang = 'id'
    else:
        lang = 'en'
    
    print(f"Detected language: {lang.upper()}")
    
    entities_hotpot = extract_entities_ner(stage1_q_hotpot, language=lang)
    
    print(f"\nFound {len(entities_hotpot)} entities:")
    for i, ent in enumerate(entities_hotpot, 1):
        print(f"  {i}. \"{ent['text']}\" → Type: {ent['label']}")
    
    # Just entity texts for encoding
    entity_texts_hotpot = [e['text'] for e in entities_hotpot]
    print(f"\nEntity texts only: {entity_texts_hotpot}")

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
    if any(word in stage1_q_wiki.lower() for word in ['kapan', 'siapa', 'apa', 'yang']):
        lang = 'id'
    else:
        lang = 'en'
    
    print(f"Detected language: {lang.upper()}")
    
    entities_wiki = extract_entities_ner(stage1_q_wiki, language=lang)
    
    print(f"\nFound {len(entities_wiki)} entities:")
    for i, ent in enumerate(entities_wiki, 1):
        print(f"  {i}. \"{ent['text']}\" → Type: {ent['label']}")
    
    # Entity texts only
    entity_texts_wiki = [e['text'] for e in entities_wiki]
    print(f"\nEntity texts only: {entity_texts_wiki}")

# Summary
print("\n" + "="*100)
print("NER EXTRACTION SUMMARY")
print("="*100)

print(f"\nHotpotQA:")
print(f"  Stage 1 Question: {stage1_q_hotpot if decomp_hotpot else 'N/A'}")
print(f"  Entities found: {len(entities_hotpot) if decomp_hotpot else 0}")
if decomp_hotpot:
    print(f"  Entity list: {', '.join([e['text'] for e in entities_hotpot])}")

print(f"\n2WikiMultihop:")
print(f"  Stage 1 Question: {stage1_q_wiki if decomp_wiki else 'N/A'}")
print(f"  Entities found: {len(entities_wiki) if decomp_wiki else 0}")
if decomp_wiki:
    print(f"  Entity list: {', '.join([e['text'] for e in entities_wiki])}")

# Analysis
print("\n" + "="*100)
print("ANALYSIS: DID NER CAPTURE KEY ENTITIES?")
print("="*100)

print("\nHotpotQA:")
print(f"  Main Question: {main_q_hotpot}")
print(f"  Expected entities: ['Arthur's Magazine', 'First for Women']")
if decomp_hotpot:
    extracted = [e['text'] for e in entities_hotpot]
    found_arthur = any("arthur" in e.lower() for e in extracted)
    found_first = any("first" in e.lower() or "women" in e.lower() for e in extracted)
    print(f"  Found 'Arthur's Magazine': {'YES' if found_arthur else 'NO'}")
    print(f"  Found 'First for Women': {'YES' if found_first else 'NO'}")

print("\n2WikiMultihop:")
print(f"  Main Question: {main_q_wiki}")
print(f"  Expected entities: ['El Extraño Viaje', 'Love In Pawn', 'director']")
if decomp_wiki:
    extracted = [e['text'] for e in entities_wiki]
    found_extrano = any("extraño" in e.lower() or "viaje" in e.lower() for e in extracted)
    found_love = any("love" in e.lower() or "pawn" in e.lower() for e in extracted)
    found_director = any("director" in e.lower() or "sutradara" in e.lower() for e in extracted)
    print(f"  Found 'El Extraño Viaje': {'YES' if found_extrano else 'NO'}")
    print(f"  Found 'Love In Pawn': {'YES' if found_love else 'NO'}")
    print(f"  Found 'director' concept: {'YES' if found_director else 'NO'}")

print("\n" + "="*100)
print("CONCLUSION")
print("="*100)

if decomp_hotpot and decomp_wiki:
    total_expected = 5  # Arthur, First, Extraño, Love, director
    total_found = 0
    
    if found_arthur: total_found += 1
    if found_first: total_found += 1
    if found_extrano: total_found += 1
    if found_love: total_found += 1
    if found_director: total_found += 1
    
    accuracy = (total_found / total_expected) * 100
    
    print(f"\nNER Accuracy: {accuracy:.0f}% ({total_found}/{total_expected} key entities found)")
    
    if accuracy >= 80:
        print("\n  Status: NER works well for Stage 1 questions!")
    elif accuracy >= 60:
        print("\n  Status: NER partially works, may need improvement")
    else:
        print("\n  Status: NER struggles with these questions")
        print("  Recommendation: Use hybrid approach (NER + Regex)")

print("\n" + "="*100)
```

Jalankan cell ini untuk test NER extraction di Stage 1 questions! 

**Expected output:**
- Extract entities dari Stage 1 question HotpotQA
- Extract entities dari Stage 1 question 2WikiMultihop
- Analysis apakah NER capture key entities dengan benar
- Summary accuracy NER

Mau langsung jalankan atau ada yang mau disesuaikan?