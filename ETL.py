Oke! **Bikin ulang dari awal** - 1 mega cell yang complete:

```python
# ==================== MEGA CELL: COMPLETE 10 HOTPOTQA TEST ====================
print("="*100)
print("COMPLETE TEST: 10 HOTPOTQA SAMPLES - FROM SCRATCH")
print("="*100)

# ==================== SETUP ====================
import os
import json
import numpy as np
import torch
import time
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# Device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Device: {device}")

# OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
print("✓ OpenAI client initialized")

# Load embedding model
print("Loading embedding model...")
embedding_model = SentenceTransformer('sentence-transformers/LaBSE')
embedding_model = embedding_model.to(device)
print("✓ Embedding model loaded")

# ==================== HELPER FUNCTIONS ====================
def get_samples_list(dataset, dataset_name):
    return [dataset[i] for i in range(len(dataset))]

def get_question(sample, dataset_name):
    return sample.get('question', '')

def get_answer(sample, dataset_name):
    return sample.get('answer', '')

def get_contexts(sample, dataset_name):
    contexts = []
    context_data = sample.get('context', {})
    titles = context_data.get('title', [])
    sentences = context_data.get('sentences', [])
    for title, sents in zip(titles, sentences):
        contexts.append({
            'title': title,
            'sentences': sents,
            'text': ' '.join(sents)
        })
    return contexts

def get_context_title(context, dataset_name):
    return context.get('title', 'Unknown')

def get_context_text(context, dataset_name):
    if 'text' in context:
        return context['text']
    sents = context.get('sentences', [])
    return ' '.join(sents) if isinstance(sents, list) else sents

def is_gold_passage(passage, dataset_name):
    return passage.get('is_gold', False)

def exact_match(prediction, ground_truth):
    return int(prediction.strip().lower() == ground_truth.strip().lower())

def f1_score(prediction, ground_truth):
    pred_tokens = prediction.lower().split()
    gold_tokens = ground_truth.lower().split()
    if not pred_tokens or not gold_tokens:
        return int(pred_tokens == gold_tokens)
    common = set(pred_tokens) & set(gold_tokens)
    if not common:
        return 0
    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gold_tokens)
    return (2 * precision * recall) / (precision + recall)

print("✓ Helper functions loaded")

# ==================== RETRIEVAL ====================
def retrieve_passages_dense(question, contexts, dataset_name, k=3):
    """Dense retrieval using FULL passage text"""
    # Encode question
    question_emb = embedding_model.encode(question, convert_to_tensor=True, device=device)
    
    # Encode FULL passage texts
    passage_texts = [get_context_text(ctx, dataset_name) for ctx in contexts]
    passage_embs = embedding_model.encode(passage_texts, convert_to_tensor=True, device=device)
    
    # Cosine similarity
    similarities = torch.nn.functional.cosine_similarity(
        question_emb.unsqueeze(0), 
        passage_embs
    )
    
    # Top-k
    top_k_indices = torch.topk(similarities, min(k, len(contexts))).indices.cpu().tolist()
    
    retrieved = []
    for rank, idx in enumerate(top_k_indices, 1):
        ctx = contexts[idx].copy()
        ctx['retrieval_rank'] = rank
        ctx['retrieval_score'] = similarities[idx].item()
        retrieved.append(ctx)
    
    return retrieved

print("✓ Retrieval function loaded")

# ==================== DECOMPOSITION ====================
def decompose_question(question, dataset_name):
    """Decompose multi-hop question"""
    prompt = f"""Decompose this multi-hop question into sub-questions.

Question: {question}

For comparison questions (e.g., "which was founded earlier"), include stages to find comparable attributes.

Return JSON:
{{
  "sub_questions": [
    {{"stage": 1, "question": "...", "purpose": "..."}},
    {{"stage": 2, "question": "...", "purpose": "..."}}
  ]
}}

JSON:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Decompose questions into necessary sub-questions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        result = json.loads(response.choices[0].message.content)
        return result.get('sub_questions', [{"stage": 1, "question": question}])
    except:
        return [{"stage": 1, "question": question}]

print("✓ Decomposition function loaded")

# ==================== ANSWER GENERATION ====================
def generate_answer(stage_question, contexts, dataset_name):
    """Generate answer from passages"""
    context_parts = []
    for i, ctx in enumerate(contexts, 1):
        title = get_context_title(ctx, dataset_name)
        text = get_context_text(ctx, dataset_name)
        context_parts.append(f"Passage {i} ({title}):\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    prompt = f"""Answer the question based on the passages.

PASSAGES:
{context_str}

QUESTION: {stage_question}

RULES:
1. Answer from passages only
2. Use logical inference when clearly implied
3. Short answer (max 10 words)
4. If no info: "Tidak ada informasi"

JSON:
{{
  "answer": "...",
  "confidence": 0-100,
  "reasoning": "..."
}}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract answers from passages."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        result = json.loads(response.choices[0].message.content)
        answer = result.get('answer', '')
        confidence = result.get('confidence', 50) / 100.0
        reasoning = result.get('reasoning', '')
        
        if "tidak ada informasi" in answer.lower() and confidence > 0.3:
            confidence = 0.10
        
        return answer, confidence, reasoning
    except:
        return "", 0.0, ""

print("✓ Generation function loaded")

# ==================== SMART PROGRESSIVE STAGE 1 ====================
def smart_progressive_stage1(question, all_passages, dataset_name, verbose=True):
    """Smart progressive: rank 1-3, then 4-6, then 7-9"""
    
    if verbose:
        print(f"\n{'─'*80}")
        print(f"🔍 RETRIEVAL: Smart Progressive")
        print(f"{'─'*80}")
    
    # Get full ranking
    all_ranked = retrieve_passages_dense(question, all_passages, dataset_name, k=len(all_passages))
    
    windows = [(0, 3, "Rank 1-3"), (3, 6, "Rank 4-6"), (6, 9, "Rank 7-9")]
    
    all_attempts = []
    accumulated = []
    
    for start, end, label in windows:
        if verbose:
            print(f"\n  WINDOW: {label}")
        
        window_passages = all_ranked[start:end]
        
        if verbose:
            for p in window_passages:
                title = get_context_title(p, dataset_name)
                score = p.get('retrieval_score', 0)
                rank = p.get('retrieval_rank', 0)
                marker = "✓" if is_gold_passage(p, dataset_name) else "✗"
                print(f"    [{rank}] {marker} {title[:45]:45s} ({score:.4f})")
        
        answer, conf, reasoning = generate_answer(question, window_passages, dataset_name)
        
        if verbose:
            print(f"  → {answer} (conf: {conf:.2f})")
        
        all_attempts.append({
            'window': label,
            'answer': answer,
            'confidence': conf,
            'passages': window_passages
        })
        
        accumulated.extend(window_passages)
        
        if conf >= 0.7:
            if verbose:
                print(f"  ✅ Sufficient!")
            break
    
    best = max(all_attempts, key=lambda x: x['confidence'])
    return best['answer'], best['confidence'], best.get('reasoning', ''), accumulated, all_attempts

print("✓ Smart progressive loaded")

# ==================== TEST SAMPLE ====================
def test_sample(sample, sample_id, dataset_name, verbose=True):
    """Test single sample"""
    
    if verbose:
        print(f"\n{'='*100}")
        print(f"SAMPLE {sample_id}")
        print(f"{'='*100}")
    
    question = get_question(sample, dataset_name)
    gold_answer = get_answer(sample, dataset_name)
    all_passages = get_contexts(sample, dataset_name)
    
    if verbose:
        print(f"Q: {question}")
        print(f"Gold: {gold_answer}")
        print(f"Passages: {len(all_passages)}")
    
    # Decompose
    sub_questions = decompose_question(question, dataset_name)
    
    if verbose:
        print(f"\n{'─'*80}")
        print(f"Decomposed into {len(sub_questions)} stages:")
        for sq in sub_questions:
            print(f"  Stage {sq['stage']}: {sq['question']}")
    
    # Process stages
    stage_results = []
    previous_answers = {}
    
    for stage_idx, sq in enumerate(sub_questions):
        stage_num = sq['stage']
        stage_question = sq['question']
        
        # Replace placeholders
        for prev_stage, prev_answer in previous_answers.items():
            stage_question = stage_question.replace(f"[ANSWER_STAGE_{prev_stage}]", prev_answer)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"STAGE {stage_num}: {stage_question}")
            print(f"{'='*80}")
        
        if stage_idx == 0:
            answer, conf, reasoning, used_passages, attempts = smart_progressive_stage1(
                stage_question, all_passages, dataset_name, verbose=verbose
            )
        else:
            retrieved = retrieve_passages_dense(stage_question, all_passages, dataset_name, k=3)
            answer, conf, reasoning = generate_answer(stage_question, retrieved, dataset_name)
            used_passages = retrieved
            if verbose:
                print(f"\n  Q2P → {answer} (conf: {conf:.2f})")
        
        stage_results.append({
            'stage': stage_num,
            'answer': answer,
            'confidence': conf,
            'passages': used_passages
        })
        
        previous_answers[stage_num] = answer
    
    # Synthesis
    synthesis_prompt = f"Q: {question}\nStages:\n"
    for s in stage_results:
        synthesis_prompt += f"Stage {s['stage']}: {s['answer']}\n"
    synthesis_prompt += "\nFinal answer (max 5 words):"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": synthesis_prompt}],
            max_tokens=15,
            temperature=0
        )
        final_answer = response.choices[0].message.content.strip().rstrip('.')
    except:
        final_answer = stage_results[-1]['answer']
    
    # Evaluate
    em = exact_match(final_answer, gold_answer)
    f1 = f1_score(final_answer, gold_answer)
    
    total_passages = len(set(get_context_title(p, dataset_name) for s in stage_results for p in s['passages']))
    
    if verbose:
        print(f"\n{'─'*80}")
        print(f"Final: {final_answer}")
        print(f"Gold: {gold_answer}")
        print(f"EM: {em} | F1: {f1:.2f} | Passages: {total_passages}/10")
    
    return {
        'sample_id': sample_id,
        'question': question,
        'gold_answer': gold_answer,
        'predicted_answer': final_answer,
        'em': em,
        'f1': f1,
        'total_passages': total_passages,
        'num_stages': len(stage_results)
    }

print("✓ Test function loaded")

# ==================== RUN 10 SAMPLES ====================
print(f"\n{'='*100}")
print("RUNNING 10 SAMPLES")
print(f"{'='*100}")

start_time = time.time()

hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')[:10]
all_results = []

for i, sample in enumerate(hotpot_samples, 1):
    try:
        result = test_sample(sample, i, 'hotpotqa', verbose=True)
        all_results.append(result)
    except Exception as e:
        print(f"\n❌ Error sample {i}: {e}")
        all_results.append({'sample_id': i, 'error': str(e), 'em': 0, 'f1': 0})

elapsed = time.time() - start_time

# ==================== SUMMARY ====================
print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}")

valid = [r for r in all_results if 'error' not in r]

for r in valid:
    status = "✅" if r['em'] == 1 else "❌"
    print(f"{status} Sample {r['sample_id']:2d}: EM={r['em']} F1={r['f1']:.2f} Passages={r['total_passages']}/10")

if valid:
    avg_em = np.mean([r['em'] for r in valid])
    avg_f1 = np.mean([r['f1'] for r in valid])
    avg_pass = np.mean([r['total_passages'] for r in valid])
    
    print(f"\n{'─'*80}")
    print(f"EM: {avg_em*100:.1f}%")
    print(f"F1: {avg_f1:.3f}")
    print(f"Avg passages: {avg_pass:.1f}/10")
    print(f"Time: {elapsed:.1f}s")
    print(f"\nBaseline K=5: 34% | Ours: {avg_em*100:.1f}% | Δ: {(avg_em*100-34):+.1f}pp")

print(f"\n{'='*100}")
print("✓ COMPLETE!")
print(f"{'='*100}")
```

Run **1 cell ini aja** - everything from scratch! 🚀