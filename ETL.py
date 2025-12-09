Oke, saya buatkan kode lengkap dari awal sampai retrieval untuk **comparison test**: IndoBERT vs mE5-base vs mE5-large!

## CELL 1: Setup Awal

```python
print("="*100)
print("RETRIEVAL MODEL COMPARISON: IndoBERT vs mE5-base vs mE5-large")
print("="*100)

from google.colab import drive
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Mount Drive
drive.mount('/content/drive')

# Set working directory
WORK_DIR = '/content/drive/MyDrive/QA_Experiments'
os.chdir(WORK_DIR)
LOG_DIR = os.path.join(WORK_DIR, 'experiment_logs')

print(f"Working directory: {WORK_DIR}")
print(f"Files available: {len(os.listdir(WORK_DIR))} files")
```

## CELL 2: Install & Import Libraries

```python
# Install required packages
print("Installing required packages...")
!pip install -q sentence-transformers torch

import torch
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import time

print("All libraries imported successfully")

# Check GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\nDevice: {device}")
if device == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

## CELL 3: Load Configuration & Datasets

```python
print("="*100)
print("LOADING CONFIGURATION & DATASETS")
print("="*100)

# Load configuration
with open(os.path.join(LOG_DIR, 'config.json'), 'r') as f:
    CONFIG = json.load(f)

print("Configuration loaded")

# Load datasets
datasets = {}
for dataset_name, filename in CONFIG['datasets'].items():
    filepath = os.path.join(WORK_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    datasets[dataset_name] = data
    
    # Count samples
    if 'samples' in data:
        num_samples = len(data['samples'])
    elif 'sampel' in data:
        num_samples = len(data['sampel'])
    elif isinstance(data, list):
        num_samples = len(data)
    else:
        num_samples = 0
    
    print(f"Loaded {dataset_name}: {num_samples} samples")

print("\nDatasets loaded successfully")
```

## CELL 4: Dataset Field Mappings & Utility Functions

```python
print("="*100)
print("DATASET FIELD MAPPINGS & UTILITY FUNCTIONS")
print("="*100)

# Field mappings
DATASET_FIELD_MAPPINGS = {
    "squad": {
        "samples_key": "samples",
        "question_key": "indonesian_data.pertanyaan",
        "answer_key": "indonesian_data.jawaban",
        "contexts_key": "contexts",
    },
    "hotpotqa": {
        "samples_key": None,
        "question_key": "question",
        "answer_key": "answer",
        "contexts_key": "context",
        "supporting_facts_key": "supporting_facts",
    },
    "2wikimultihop": {
        "samples_key": "sampel",
        "question_key": "pertanyaan",
        "answer_key": "jawaban",
        "contexts_key": "konteks",
    }
}

CONFIG['field_mappings'] = DATASET_FIELD_MAPPINGS

# Utility functions
def get_samples_list(data, dataset_name):
    if 'samples' in data:
        return data['samples']
    elif 'sampel' in data:
        return data['sampel']
    elif isinstance(data, list):
        return data
    return []

def get_nested_value(obj, key_path):
    if not key_path:
        return None
    keys = key_path.split('.')
    value = obj
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def get_question(sample, dataset_name):
    mapping = CONFIG['field_mappings'][dataset_name]
    question = get_nested_value(sample, mapping['question_key'])
    return str(question) if question else ""

def get_answer(sample, dataset_name):
    mapping = CONFIG['field_mappings'][dataset_name]
    answer = get_nested_value(sample, mapping['answer_key'])
    if isinstance(answer, list) and len(answer) > 0:
        answer = answer[0]
    return str(answer) if answer else ""

def get_contexts_hotpotqa(sample):
    if 'context' not in sample:
        return []
    context_obj = sample['context']
    titles = context_obj.get('title', [])
    sentences_list = context_obj.get('sentences', [])
    supporting_facts = sample.get('supporting_facts', {})
    gold_titles = supporting_facts.get('title', [])

    contexts = []
    for i, (title, sentences) in enumerate(zip(titles, sentences_list)):
        if isinstance(sentences, list):
            text = " ".join(sentences)
        else:
            text = str(sentences)
        is_gold = title in gold_titles
        contexts.append({
            "title": title,
            "text": text,
            "sentences": sentences,
            "index": i,
            "type": "gold" if is_gold else "distractor"
        })
    return contexts

def get_contexts(sample, dataset_name):
    if dataset_name == "hotpotqa":
        return get_contexts_hotpotqa(sample)
    mapping = CONFIG['field_mappings'][dataset_name]
    contexts = get_nested_value(sample, mapping['contexts_key'])
    if not contexts or not isinstance(contexts, list):
        return []
    return contexts

def get_context_text(context, dataset_name):
    if dataset_name == "squad":
        return context.get('text_indonesian', "")
    elif dataset_name == "hotpotqa":
        return context.get('text', "")
    elif dataset_name == "2wikimultihop":
        sentences = context.get('kalimat', [])
        if isinstance(sentences, list):
            return " ".join(sentences)
        return str(sentences)
    return ""

def get_context_title(context, dataset_name):
    return context.get('title', context.get('judul', "Untitled"))

def is_gold_passage(context, dataset_name):
    if dataset_name == "squad":
        return context.get('type') == 'gold_passage'
    elif dataset_name == "2wikimultihop":
        return context.get('tipe') == 'passage_emas'
    elif dataset_name == "hotpotqa":
        return context.get('type') == 'gold'
    return False

print("Utility functions loaded successfully")
```

## CELL 5: Load All Retrieval Models

```python
print("="*100)
print("LOADING RETRIEVAL MODELS")
print("="*100)

# Model 1: IndoBERT (current baseline)
print("\n[1/3] Loading IndoBERT...")
start_time = time.time()
model_indobert = SentenceTransformer('indobenchmark/indobert-base-p1')
model_indobert = model_indobert.to(device)
load_time_indobert = time.time() - start_time
print(f"      IndoBERT loaded in {load_time_indobert:.2f}s")
print(f"      Parameters: ~110M")
print(f"      Best for: Indonesian only")

# Model 2: mE5-base (multilingual)
print("\n[2/3] Loading mE5-base...")
start_time = time.time()
model_me5_base = SentenceTransformer('intfloat/multilingual-e5-base')
model_me5_base = model_me5_base.to(device)
load_time_me5_base = time.time() - start_time
print(f"      mE5-base loaded in {load_time_me5_base:.2f}s")
print(f"      Parameters: ~278M")
print(f"      Best for: 100+ languages (ID + EN)")

# Model 3: mE5-large (multilingual, best accuracy)
print("\n[3/3] Loading mE5-large...")
start_time = time.time()
model_me5_large = SentenceTransformer('intfloat/multilingual-e5-large')
model_me5_large = model_me5_large.to(device)
load_time_me5_large = time.time() - start_time
print(f"      mE5-large loaded in {load_time_me5_large:.2f}s")
print(f"      Parameters: ~560M")
print(f"      Best for: Maximum accuracy")

print("\n" + "="*80)
print("ALL MODELS LOADED SUCCESSFULLY")
print("="*80)
print(f"\nMemory usage:")
if device == 'cuda':
    print(f"  GPU allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
    print(f"  GPU reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

## CELL 6: Retrieval Functions (All Models)

```python
print("="*100)
print("RETRIEVAL FUNCTIONS FOR ALL MODELS")
print("="*100)

def retrieve_passages_indobert(question, contexts, dataset_name, k=5):
    """
    Retrieval using IndoBERT
    No prefix needed
    """
    # Extract passage texts
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    
    # Encode
    query_embedding = model_indobert.encode(question, convert_to_tensor=True)
    passage_embeddings = model_indobert.encode(passage_texts, convert_to_tensor=True)
    
    # Compute cosine similarity
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    
    # Get top-k indices
    top_k_indices = torch.argsort(similarities, descending=True)[:k].cpu().numpy()
    
    # Return top-k contexts with scores
    retrieved = []
    for rank, idx in enumerate(top_k_indices):
        ctx = contexts[idx].copy()
        ctx['retrieval_score'] = float(similarities[idx])
        ctx['retrieval_rank'] = rank + 1
        retrieved.append(ctx)
    
    return retrieved

def retrieve_passages_me5_base(question, contexts, dataset_name, k=5):
    """
    Retrieval using mE5-base
    IMPORTANT: Requires "query:" and "passage:" prefixes
    """
    # Extract passage texts
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    
    # Add prefixes (CRITICAL for mE5!)
    query_with_prefix = f"query: {question}"
    passages_with_prefix = [f"passage: {text}" for text in passage_texts]
    
    # Encode
    query_embedding = model_me5_base.encode(query_with_prefix, convert_to_tensor=True)
    passage_embeddings = model_me5_base.encode(passages_with_prefix, convert_to_tensor=True)
    
    # Compute cosine similarity
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    
    # Get top-k indices
    top_k_indices = torch.argsort(similarities, descending=True)[:k].cpu().numpy()
    
    # Return top-k contexts with scores
    retrieved = []
    for rank, idx in enumerate(top_k_indices):
        ctx = contexts[idx].copy()
        ctx['retrieval_score'] = float(similarities[idx])
        ctx['retrieval_rank'] = rank + 1
        retrieved.append(ctx)
    
    return retrieved

def retrieve_passages_me5_large(question, contexts, dataset_name, k=5):
    """
    Retrieval using mE5-large
    IMPORTANT: Requires "query:" and "passage:" prefixes
    """
    # Extract passage texts
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    
    # Add prefixes (CRITICAL for mE5!)
    query_with_prefix = f"query: {question}"
    passages_with_prefix = [f"passage: {text}" for text in passage_texts]
    
    # Encode
    query_embedding = model_me5_large.encode(query_with_prefix, convert_to_tensor=True)
    passage_embeddings = model_me5_large.encode(passages_with_prefix, convert_to_tensor=True)
    
    # Compute cosine similarity
    similarities = util.cos_sim(query_embedding, passage_embeddings)[0]
    
    # Get top-k indices
    top_k_indices = torch.argsort(similarities, descending=True)[:k].cpu().numpy()
    
    # Return top-k contexts with scores
    retrieved = []
    for rank, idx in enumerate(top_k_indices):
        ctx = contexts[idx].copy()
        ctx['retrieval_score'] = float(similarities[idx])
        ctx['retrieval_rank'] = rank + 1
        retrieved.append(ctx)
    
    return retrieved

print("Retrieval functions loaded for all 3 models")
```

## CELL 7: Recall Calculation Function

```python
print("="*100)
print("RECALL@K CALCULATION FUNCTION")
print("="*100)

def compute_recall_at_k(retrieved_contexts, all_contexts, dataset_name, k=5):
    """
    Compute Recall@K
    Measures: how many gold passages were retrieved in top-K
    """
    # Get all gold passage titles
    gold_titles = set()
    for ctx in all_contexts:
        if is_gold_passage(ctx, dataset_name):
            title = get_context_title(ctx, dataset_name)
            gold_titles.add(title)
    
    # Get retrieved passage titles
    retrieved_titles = set()
    for ctx in retrieved_contexts[:k]:
        title = get_context_title(ctx, dataset_name)
        retrieved_titles.add(title)
    
    # Calculate recall
    num_retrieved = len(gold_titles & retrieved_titles)
    num_total_gold = len(gold_titles)
    recall = num_retrieved / num_total_gold if num_total_gold > 0 else 0.0
    
    return recall, num_retrieved, num_total_gold

print("Recall@K function loaded")
```

## CELL 8: Test Single Sample (HotpotQA - Indonesian)

```python
print("="*100)
print("TEST 1: SINGLE SAMPLE - HOTPOTQA (INDONESIAN)")
print("="*100)

# Get HotpotQA sample
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')
hotpot_sample = hotpot_samples[0]

question = get_question(hotpot_sample, 'hotpotqa')
answer = get_answer(hotpot_sample, 'hotpotqa')
contexts = get_contexts(hotpot_sample, 'hotpotqa')

print(f"\nQuestion: {question}")
print(f"Gold Answer: {answer}")
print(f"Total passages: {len(contexts)}")

# Count gold passages
num_gold = sum(1 for c in contexts if is_gold_passage(c, 'hotpotqa'))
print(f"Gold passages: {num_gold}")

# Test each model
k = 5
results_hotpot = {}

# Model 1: IndoBERT
print(f"\n{'='*80}")
print("MODEL 1: IndoBERT")
print(f"{'='*80}")
start_time = time.time()
retrieved_indobert = retrieve_passages_indobert(question, contexts, 'hotpotqa', k=k)
time_indobert = time.time() - start_time
recall_indobert, num_ret_indobert, _ = compute_recall_at_k(retrieved_indobert, contexts, 'hotpotqa', k=k)

print(f"Retrieval time: {time_indobert:.3f}s")
print(f"Recall@{k}: {recall_indobert:.2%} ({num_ret_indobert}/{num_gold} gold retrieved)")
print(f"\nTop-{k} passages:")
for p in retrieved_indobert:
    title = get_context_title(p, 'hotpotqa')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, 'hotpotqa')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [Rank {p['retrieval_rank']}] {marker} {title[:60]:60s} (score: {score:.4f})")

results_hotpot['indobert'] = {
    'recall': recall_indobert,
    'time': time_indobert,
    'retrieved': retrieved_indobert
}

# Model 2: mE5-base
print(f"\n{'='*80}")
print("MODEL 2: mE5-base")
print(f"{'='*80}")
start_time = time.time()
retrieved_me5_base = retrieve_passages_me5_base(question, contexts, 'hotpotqa', k=k)
time_me5_base = time.time() - start_time
recall_me5_base, num_ret_me5_base, _ = compute_recall_at_k(retrieved_me5_base, contexts, 'hotpotqa', k=k)

print(f"Retrieval time: {time_me5_base:.3f}s")
print(f"Recall@{k}: {recall_me5_base:.2%} ({num_ret_me5_base}/{num_gold} gold retrieved)")
print(f"\nTop-{k} passages:")
for p in retrieved_me5_base:
    title = get_context_title(p, 'hotpotqa')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, 'hotpotqa')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [Rank {p['retrieval_rank']}] {marker} {title[:60]:60s} (score: {score:.4f})")

results_hotpot['me5_base'] = {
    'recall': recall_me5_base,
    'time': time_me5_base,
    'retrieved': retrieved_me5_base
}

# Model 3: mE5-large
print(f"\n{'='*80}")
print("MODEL 3: mE5-large")
print(f"{'='*80}")
start_time = time.time()
retrieved_me5_large = retrieve_passages_me5_large(question, contexts, 'hotpotqa', k=k)
time_me5_large = time.time() - start_time
recall_me5_large, num_ret_me5_large, _ = compute_recall_at_k(retrieved_me5_large, contexts, 'hotpotqa', k=k)

print(f"Retrieval time: {time_me5_large:.3f}s")
print(f"Recall@{k}: {recall_me5_large:.2%} ({num_ret_me5_large}/{num_gold} gold retrieved)")
print(f"\nTop-{k} passages:")
for p in retrieved_me5_large:
    title = get_context_title(p, 'hotpotqa')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, 'hotpotqa')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [Rank {p['retrieval_rank']}] {marker} {title[:60]:60s} (score: {score:.4f})")

results_hotpot['me5_large'] = {
    'recall': recall_me5_large,
    'time': time_me5_large,
    'retrieved': retrieved_me5_large
}

# Summary
print(f"\n{'='*80}")
print("SUMMARY: HotpotQA (Indonesian)")
print(f"{'='*80}")
print(f"\n{'Model':<15} {'Recall@5':<12} {'Time (s)':<12} {'Speed vs IndoBERT'}")
print(f"{'-'*60}")
print(f"{'IndoBERT':<15} {recall_indobert:>10.2%} {time_indobert:>10.3f}   {'1.00x'}")
print(f"{'mE5-base':<15} {recall_me5_base:>10.2%} {time_me5_base:>10.3f}   {time_me5_base/time_indobert:>5.2f}x")
print(f"{'mE5-large':<15} {recall_me5_large:>10.2%} {time_me5_large:>10.3f}   {time_me5_large/time_indobert:>5.2f}x")

print(f"\nRecall Improvement:")
print(f"  mE5-base vs IndoBERT:  {(recall_me5_base - recall_indobert)*100:+.1f} percentage points")
print(f"  mE5-large vs IndoBERT: {(recall_me5_large - recall_indobert)*100:+.1f} percentage points")
print(f"  mE5-large vs mE5-base: {(recall_me5_large - recall_me5_base)*100:+.1f} percentage points")
```

## CELL 9: Test Single Sample (2WikiMultihop - English)

```python
print("="*100)
print("TEST 2: SINGLE SAMPLE - 2WIKIMULTIHOP (ENGLISH)")
print("="*100)

# Get 2WikiMultihop sample
wiki_samples = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')
wiki_sample = wiki_samples[0]

question = get_question(wiki_sample, '2wikimultihop')
answer = get_answer(wiki_sample, '2wikimultihop')
contexts = get_contexts(wiki_sample, '2wikimultihop')

print(f"\nQuestion: {question}")
print(f"Gold Answer: {answer}")
print(f"Total passages: {len(contexts)}")

# Count gold passages
num_gold = sum(1 for c in contexts if is_gold_passage(c, '2wikimultihop'))
print(f"Gold passages: {num_gold}")

# Test each model
k = 5
results_wiki = {}

# Model 1: IndoBERT (should perform BADLY on English!)
print(f"\n{'='*80}")
print("MODEL 1: IndoBERT (EXPECTED TO BE BAD - Language Mismatch!)")
print(f"{'='*80}")
start_time = time.time()
retrieved_indobert = retrieve_passages_indobert(question, contexts, '2wikimultihop', k=k)
time_indobert = time.time() - start_time
recall_indobert, num_ret_indobert, _ = compute_recall_at_k(retrieved_indobert, contexts, '2wikimultihop', k=k)

print(f"Retrieval time: {time_indobert:.3f}s")
print(f"Recall@{k}: {recall_indobert:.2%} ({num_ret_indobert}/{num_gold} gold retrieved)")
print(f"\nTop-{k} passages:")
for p in retrieved_indobert:
    title = get_context_title(p, '2wikimultihop')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [Rank {p['retrieval_rank']}] {marker} {title[:60]:60s} (score: {score:.4f})")

results_wiki['indobert'] = {
    'recall': recall_indobert,
    'time': time_indobert,
    'retrieved': retrieved_indobert
}

# Model 2: mE5-base
print(f"\n{'='*80}")
print("MODEL 2: mE5-base")
print(f"{'='*80}")
start_time = time.time()
retrieved_me5_base = retrieve_passages_me5_base(question, contexts, '2wikimultihop', k=k)
time_me5_base = time.time() - start_time
recall_me5_base, num_ret_me5_base, _ = compute_recall_at_k(retrieved_me5_base, contexts, '2wikimultihop', k=k)

print(f"Retrieval time: {time_me5_base:.3f}s")
print(f"Recall@{k}: {recall_me5_base:.2%} ({num_ret_me5_base}/{num_gold} gold retrieved)")
print(f"\nTop-{k} passages:")
for p in retrieved_me5_base:
    title = get_context_title(p, '2wikimultihop')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [Rank {p['retrieval_rank']}] {marker} {title[:60]:60s} (score: {score:.4f})")

results_wiki['me5_base'] = {
    'recall': recall_me5_base,
    'time': time_me5_base,
    'retrieved': retrieved_me5_base
}

# Model 3: mE5-large
print(f"\n{'='*80}")
print("MODEL 3: mE5-large")
print(f"{'='*80}")
start_time = time.time()
retrieved_me5_large = retrieve_passages_me5_large(question, contexts, '2wikimultihop', k=k)
time_me5_large = time.time() - start_time
recall_me5_large, num_ret_me5_large, _ = compute_recall_at_k(retrieved_me5_large, contexts, '2wikimultihop', k=k)

print(f"Retrieval time: {time_me5_large:.3f}s")
print(f"Recall@{k}: {recall_me5_large:.2%} ({num_ret_me5_large}/{num_gold} gold retrieved)")
print(f"\nTop-{k} passages:")
for p in retrieved_me5_large:
    title = get_context_title(p, '2wikimultihop')
    score = p['retrieval_score']
    is_gold = is_gold_passage(p, '2wikimultihop')
    marker = "[GOLD]" if is_gold else "[DIST]"
    print(f"  [Rank {p['retrieval_rank']}] {marker} {title[:60]:60s} (score: {score:.4f})")

results_wiki['me5_large'] = {
    'recall': recall_me5_large,
    'time': time_me5_large,
    'retrieved': retrieved_me5_large
}

# Summary
print(f"\n{'='*80}")
print("SUMMARY: 2WikiMultihop (English)")
print(f"{'='*80}")
print(f"\n{'Model':<15} {'Recall@5':<12} {'Time (s)':<12} {'Speed vs IndoBERT'}")
print(f"{'-'*60}")
print(f"{'IndoBERT':<15} {recall_indobert:>10.2%} {time_indobert:>10.3f}   {'1.00x'}")
print(f"{'mE5-base':<15} {recall_me5_base:>10.2%} {time_me5_base:>10.3f}   {time_me5_base/time_indobert:>5.2f}x")
print(f"{'mE5-large':<15} {recall_me5_large:>10.2%} {time_me5_large:>10.3f}   {time_me5_large/time_indobert:>5.2f}x")

print(f"\nRecall Improvement:")
print(f"  mE5-base vs IndoBERT:  {(recall_me5_base - recall_indobert)*100:+.1f} percentage points")
print(f"  mE5-large vs IndoBERT: {(recall_me5_large - recall_indobert)*100:+.1f} percentage points")
print(f"  mE5-large vs mE5-base: {(recall_me5_large - recall_me5_base)*100:+.1f} percentage points")
```

## CELL 10: Test 10 Samples Per Dataset

```python
print("="*100)
print("TEST 3: 10 SAMPLES PER DATASET - COMPREHENSIVE COMPARISON")
print("="*100)

num_test_samples = 10

# Storage for aggregate results
aggregate_results = {
    'hotpotqa': {
        'indobert': {'recalls': [], 'times': []},
        'me5_base': {'recalls': [], 'times': []},
        'me5_large': {'recalls': [], 'times': []}
    },
    '2wikimultihop': {
        'indobert': {'recalls': [], 'times': []},
        'me5_base': {'recalls': [], 'times': []},
        'me5_large': {'recalls': [], 'times': []}
    }
}

# Test HotpotQA
print(f"\n{'='*80}")
print("DATASET 1: HotpotQA (Indonesian)")
print(f"{'='*80}")

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:num_test_samples]

for sample_idx, sample in enumerate(tqdm(hotpot_samples, desc="HotpotQA")):
    question = get_question(sample, 'hotpotqa')
    contexts = get_contexts(sample, 'hotpotqa')
    
    # IndoBERT
    start = time.time()
    retrieved = retrieve_passages_indobert(question, contexts, 'hotpotqa', k=5)
    elapsed = time.time() - start
    recall, _, _ = compute_recall_at_k(retrieved, contexts, 'hotpotqa', k=5)
    aggregate_results['hotpotqa']['indobert']['recalls'].append(recall)
    aggregate_results['hotpotqa']['indobert']['times'].append(elapsed)
    
    # mE5-base
    start = time.time()
    retrieved = retrieve_passages_me5_base(question, contexts, 'hotpotqa', k=5)
    elapsed = time.time() - start
    recall, _, _ = compute_recall_at_k(retrieved, contexts, 'hotpotqa', k=5)
    aggregate_results['hotpotqa']['me5_base']['recalls