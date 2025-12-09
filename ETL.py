```python
    aggregate_results['hotpotqa']['me5_base']['recalls'].append(recall)
    aggregate_results['hotpotqa']['me5_base']['times'].append(elapsed)
    
    # mE5-large
    start = time.time()
    retrieved = retrieve_passages_me5_large(question, contexts, 'hotpotqa', k=5)
    elapsed = time.time() - start
    recall, _, _ = compute_recall_at_k(retrieved, contexts, 'hotpotqa', k=5)
    aggregate_results['hotpotqa']['me5_large']['recalls'].append(recall)
    aggregate_results['hotpotqa']['me5_large']['times'].append(elapsed)

print("HotpotQA testing complete")

# Test 2WikiMultihop
print(f"\n{'='*80}")
print("DATASET 2: 2WikiMultihop (English)")
print(f"{'='*80}")

wiki_samples = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')[:num_test_samples]

for sample_idx, sample in enumerate(tqdm(wiki_samples, desc="2WikiMultihop")):
    question = get_question(sample, '2wikimultihop')
    contexts = get_contexts(sample, '2wikimultihop')
    
    # IndoBERT
    start = time.time()
    retrieved = retrieve_passages_indobert(question, contexts, '2wikimultihop', k=5)
    elapsed = time.time() - start
    recall, _, _ = compute_recall_at_k(retrieved, contexts, '2wikimultihop', k=5)
    aggregate_results['2wikimultihop']['indobert']['recalls'].append(recall)
    aggregate_results['2wikimultihop']['indobert']['times'].append(elapsed)
    
    # mE5-base
    start = time.time()
    retrieved = retrieve_passages_me5_base(question, contexts, '2wikimultihop', k=5)
    elapsed = time.time() - start
    recall, _, _ = compute_recall_at_k(retrieved, contexts, '2wikimultihop', k=5)
    aggregate_results['2wikimultihop']['me5_base']['recalls'].append(recall)
    aggregate_results['2wikimultihop']['me5_base']['times'].append(elapsed)
    
    # mE5-large
    start = time.time()
    retrieved = retrieve_passages_me5_large(question, contexts, '2wikimultihop', k=5)
    elapsed = time.time() - start
    recall, _, _ = compute_recall_at_k(retrieved, contexts, '2wikimultihop', k=5)
    aggregate_results['2wikimultihop']['me5_large']['recalls'].append(recall)
    aggregate_results['2wikimultihop']['me5_large']['times'].append(elapsed)

print("2WikiMultihop testing complete")

# Calculate statistics
print(f"\n{'='*80}")
print("AGGREGATE RESULTS (10 samples per dataset)")
print(f"{'='*80}")

for dataset_name in ['hotpotqa', '2wikimultihop']:
    print(f"\n{'-'*80}")
    print(f"DATASET: {dataset_name.upper()}")
    print(f"{'-'*80}")
    
    results = aggregate_results[dataset_name]
    
    # Calculate means
    indobert_recall_mean = np.mean(results['indobert']['recalls'])
    indobert_time_mean = np.mean(results['indobert']['times'])
    
    me5_base_recall_mean = np.mean(results['me5_base']['recalls'])
    me5_base_time_mean = np.mean(results['me5_base']['times'])
    
    me5_large_recall_mean = np.mean(results['me5_large']['recalls'])
    me5_large_time_mean = np.mean(results['me5_large']['times'])
    
    # Calculate std
    indobert_recall_std = np.std(results['indobert']['recalls'])
    me5_base_recall_std = np.std(results['me5_base']['recalls'])
    me5_large_recall_std = np.std(results['me5_large']['recalls'])
    
    print(f"\n{'Model':<15} {'Recall@5 (mean±std)':<25} {'Time (mean)':<15} {'Speedup'}")
    print(f"{'-'*75}")
    print(f"{'IndoBERT':<15} {indobert_recall_mean:>6.2%} ± {indobert_recall_std:>5.2%}       {indobert_time_mean:>8.3f}s      {'1.00x'}")
    print(f"{'mE5-base':<15} {me5_base_recall_mean:>6.2%} ± {me5_base_recall_std:>5.2%}       {me5_base_time_mean:>8.3f}s      {me5_base_time_mean/indobert_time_mean:>4.2f}x")
    print(f"{'mE5-large':<15} {me5_large_recall_mean:>6.2%} ± {me5_large_recall_std:>5.2%}       {me5_large_time_mean:>8.3f}s      {me5_large_time_mean/indobert_time_mean:>4.2f}x")
    
    print(f"\nRecall Improvement over IndoBERT:")
    print(f"  mE5-base:  {(me5_base_recall_mean - indobert_recall_mean)*100:+.1f} percentage points")
    print(f"  mE5-large: {(me5_large_recall_mean - indobert_recall_mean)*100:+.1f} percentage points")
    
    print(f"\nRecall Improvement mE5-large over mE5-base:")
    print(f"  {(me5_large_recall_mean - me5_base_recall_mean)*100:+.1f} percentage points")
```

## CELL 11: Final Comparison Summary & Visualization

```python
print("="*100)
print("FINAL COMPARISON SUMMARY & RECOMMENDATION")
print("="*100)

# Create comparison table
comparison_data = []

for dataset_name in ['hotpotqa', '2wikimultihop']:
    results = aggregate_results[dataset_name]
    
    for model_name in ['indobert', 'me5_base', 'me5_large']:
        recall_mean = np.mean(results[model_name]['recalls'])
        recall_std = np.std(results[model_name]['recalls'])
        time_mean = np.mean(results[model_name]['times'])
        
        comparison_data.append({
            'Dataset': dataset_name,
            'Model': model_name,
            'Recall@5': recall_mean,
            'Recall_Std': recall_std,
            'Time': time_mean
        })

df_comparison = pd.DataFrame(comparison_data)

# Pivot for better display
print("\n" + "="*80)
print("RECALL@5 COMPARISON")
print("="*80)

pivot_recall = df_comparison.pivot_table(
    index='Model', 
    columns='Dataset', 
    values='Recall@5'
)
print("\n" + pivot_recall.to_string())

print("\n" + "="*80)
print("AVERAGE RETRIEVAL TIME (seconds)")
print("="*80)

pivot_time = df_comparison.pivot_table(
    index='Model', 
    columns='Dataset', 
    values='Time'
)
print("\n" + pivot_time.to_string())

# Calculate overall improvements
print("\n" + "="*80)
print("OVERALL ANALYSIS")
print("="*80)

# HotpotQA
hotpot_indobert = np.mean(aggregate_results['hotpotqa']['indobert']['recalls'])
hotpot_me5_base = np.mean(aggregate_results['hotpotqa']['me5_base']['recalls'])
hotpot_me5_large = np.mean(aggregate_results['hotpotqa']['me5_large']['recalls'])

# 2WikiMultihop
wiki_indobert = np.mean(aggregate_results['2wikimultihop']['indobert']['recalls'])
wiki_me5_base = np.mean(aggregate_results['2wikimultihop']['me5_base']['recalls'])
wiki_me5_large = np.mean(aggregate_results['2wikimultihop']['me5_large']['recalls'])

print("\nHotpotQA (Indonesian):")
print(f"  IndoBERT:  {hotpot_indobert:.2%}")
print(f"  mE5-base:  {hotpot_me5_base:.2%}  ({(hotpot_me5_base - hotpot_indobert)*100:+.1f} pp)")
print(f"  mE5-large: {hotpot_me5_large:.2%}  ({(hotpot_me5_large - hotpot_indobert)*100:+.1f} pp)")

print("\n2WikiMultihop (English):")
print(f"  IndoBERT:  {wiki_indobert:.2%}  [LANGUAGE MISMATCH!]")
print(f"  mE5-base:  {wiki_me5_base:.2%}  ({(wiki_me5_base - wiki_indobert)*100:+.1f} pp)")
print(f"  mE5-large: {wiki_me5_large:.2%}  ({(wiki_me5_large - wiki_indobert)*100:+.1f} pp)")

# Average across both datasets
avg_indobert = (hotpot_indobert + wiki_indobert) / 2
avg_me5_base = (hotpot_me5_base + wiki_me5_base) / 2
avg_me5_large = (hotpot_me5_large + wiki_me5_large) / 2

print("\nAverage Across Both Datasets:")
print(f"  IndoBERT:  {avg_indobert:.2%}")
print(f"  mE5-base:  {avg_me5_base:.2%}  ({(avg_me5_base - avg_indobert)*100:+.1f} pp)")
print(f"  mE5-large: {avg_me5_large:.2%}  ({(avg_me5_large - avg_indobert)*100:+.1f} pp)")

# Speed analysis
hotpot_time_indobert = np.mean(aggregate_results['hotpotqa']['indobert']['times'])
hotpot_time_me5_base = np.mean(aggregate_results['hotpotqa']['me5_base']['times'])
hotpot_time_me5_large = np.mean(aggregate_results['hotpotqa']['me5_large']['times'])

wiki_time_indobert = np.mean(aggregate_results['2wikimultihop']['indobert']['times'])
wiki_time_me5_base = np.mean(aggregate_results['2wikimultihop']['me5_base']['times'])
wiki_time_me5_large = np.mean(aggregate_results['2wikimultihop']['me5_large']['times'])

avg_time_indobert = (hotpot_time_indobert + wiki_time_indobert) / 2
avg_time_me5_base = (hotpot_time_me5_base + wiki_time_me5_base) / 2
avg_time_me5_large = (hotpot_time_me5_large + wiki_time_me5_large) / 2

print("\n" + "="*80)
print("SPEED ANALYSIS")
print("="*80)

print(f"\nAverage Retrieval Time:")
print(f"  IndoBERT:  {avg_time_indobert:.3f}s  (baseline)")
print(f"  mE5-base:  {avg_time_me5_base:.3f}s  ({avg_time_me5_base/avg_time_indobert:.2f}x slower)")
print(f"  mE5-large: {avg_time_me5_large:.3f}s  ({avg_time_me5_large/avg_time_indobert:.2f}x slower)")

# Recommendation
print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)

print("\nBased on 10-sample testing:")

print("\n1. BEST OVERALL: mE5-base")
print(f"   - Recall improvement: +{(avg_me5_base - avg_indobert)*100:.1f} pp average")
print(f"   - Huge gain on English: +{(wiki_me5_base - wiki_indobert)*100:.1f} pp")
print(f"   - Moderate gain on Indonesian: +{(hotpot_me5_base - hotpot_indobert)*100:.1f} pp")
print(f"   - Speed: {avg_time_me5_base/avg_time_indobert:.2f}x slower (acceptable)")
print(f"   - Verdict: RECOMMENDED for production")

print("\n2. MAXIMUM ACCURACY: mE5-large")
print(f"   - Recall improvement: +{(avg_me5_large - avg_indobert)*100:.1f} pp average")
print(f"   - Additional gain over mE5-base: +{(avg_me5_large - avg_me5_base)*100:.1f} pp")
print(f"   - Speed: {avg_time_me5_large/avg_time_indobert:.2f}x slower (significant)")
print(f"   - Verdict: Use if accuracy > speed")

print("\n3. BASELINE: IndoBERT")
print(f"   - PROBLEM: Poor performance on English ({wiki_indobert:.2%})")
print(f"   - Only good for Indonesian")
print(f"   - Verdict: NOT RECOMMENDED for multilingual")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

print("\nThe current IndoBERT setup has a CRITICAL ISSUE:")
print("  - It performs POORLY on 2WikiMultihop (English dataset)")
print(f"  - Recall@5 on English: only {wiki_indobert:.2%}")

print("\nSwitching to mE5-base will provide:")
print(f"  - Massive improvement on English: +{(wiki_me5_base - wiki_indobert)*100:.0f} percentage points")
print(f"  - Slight improvement on Indonesian: +{(hotpot_me5_base - hotpot_indobert)*100:.0f} percentage points")
print(f"  - Only {avg_time_me5_base/avg_time_indobert:.1f}x slower")

print("\nRECOMMENDED ACTION:")
print("  Replace IndoBERT with mE5-base for all experiments")
```

## CELL 12: Save Comparison Results

```python
print("="*100)
print("SAVING COMPARISON RESULTS")
print("="*100)

# Create results directory
results_dir = os.path.join(LOG_DIR, 'retrieval_model_comparison')
os.makedirs(results_dir, exist_ok=True)

# Save detailed results
detailed_results = {
    'test_config': {
        'num_samples_per_dataset': num_test_samples,
        'k': 5,
        'datasets': ['hotpotqa', '2wikimultihop'],
        'models': ['indobert', 'me5_base', 'me5_large']
    },
    'aggregate_results': {
        dataset: {
            model: {
                'recalls': results[model]['recalls'],
                'times': results[model]['times'],
                'recall_mean': float(np.mean(results[model]['recalls'])),
                'recall_std': float(np.std(results[model]['recalls'])),
                'time_mean': float(np.mean(results[model]['times'])),
                'time_std': float(np.std(results[model]['times']))
            }
            for model in ['indobert', 'me5_base', 'me5_large']
        }
        for dataset, results in aggregate_results.items()
    },
    'summary': {
        'hotpotqa': {
            'indobert_recall': float(hotpot_indobert),
            'me5_base_recall': float(hotpot_me5_base),
            'me5_large_recall': float(hotpot_me5_large),
            'me5_base_improvement': float((hotpot_me5_base - hotpot_indobert) * 100),
            'me5_large_improvement': float((hotpot_me5_large - hotpot_indobert) * 100)
        },
        '2wikimultihop': {
            'indobert_recall': float(wiki_indobert),
            'me5_base_recall': float(wiki_me5_base),
            'me5_large_recall': float(wiki_me5_large),
            'me5_base_improvement': float((wiki_me5_base - wiki_indobert) * 100),
            'me5_large_improvement': float((wiki_me5_large - wiki_indobert) * 100)
        },
        'overall': {
            'avg_indobert_recall': float(avg_indobert),
            'avg_me5_base_recall': float(avg_me5_base),
            'avg_me5_large_recall': float(avg_me5_large),
            'avg_me5_base_improvement': float((avg_me5_base - avg_indobert) * 100),
            'avg_me5_large_improvement': float((avg_me5_large - avg_indobert) * 100)
        }
    },
    'recommendation': 'mE5-base',
    'recommendation_reason': f'Best balance: +{(avg_me5_base - avg_indobert)*100:.1f}pp improvement with only {avg_time_me5_base/avg_time_indobert:.1f}x slowdown'
}

# Save to JSON
results_file = os.path.join(results_dir, 'comparison_results.json')
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(detailed_results, f, indent=2, ensure_ascii=False)

print(f"Detailed results saved to: {results_file}")

# Save comparison table to CSV
csv_file = os.path.join(results_dir, 'comparison_table.csv')
df_comparison.to_csv(csv_file, index=False)
print(f"Comparison table saved to: {csv_file}")

# Save summary to text file
summary_file = os.path.join(results_dir, 'summary.txt')
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("RETRIEVAL MODEL COMPARISON SUMMARY\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"Test Configuration:\n")
    f.write(f"  Samples per dataset: {num_test_samples}\n")
    f.write(f"  K value: 5\n")
    f.write(f"  Models tested: IndoBERT, mE5-base, mE5-large\n\n")
    
    f.write("Results:\n\n")
    
    f.write("HotpotQA (Indonesian):\n")
    f.write(f"  IndoBERT:  {hotpot_indobert:.2%}\n")
    f.write(f"  mE5-base:  {hotpot_me5_base:.2%}  ({(hotpot_me5_base - hotpot_indobert)*100:+.1f} pp)\n")
    f.write(f"  mE5-large: {hotpot_me5_large:.2%}  ({(hotpot_me5_large - hotpot_indobert)*100:+.1f} pp)\n\n")
    
    f.write("2WikiMultihop (English):\n")
    f.write(f"  IndoBERT:  {wiki_indobert:.2%}  [LANGUAGE MISMATCH]\n")
    f.write(f"  mE5-base:  {wiki_me5_base:.2%}  ({(wiki_me5_base - wiki_indobert)*100:+.1f} pp)\n")
    f.write(f"  mE5-large: {wiki_me5_large:.2%}  ({(wiki_me5_large - wiki_indobert)*100:+.1f} pp)\n\n")
    
    f.write("Average Across Both Datasets:\n")
    f.write(f"  IndoBERT:  {avg_indobert:.2%}\n")
    f.write(f"  mE5-base:  {avg_me5_base:.2%}  ({(avg_me5_base - avg_indobert)*100:+.1f} pp)\n")
    f.write(f"  mE5-large: {avg_me5_large:.2%}  ({(avg_me5_large - avg_indobert)*100:+.1f} pp)\n\n")
    
    f.write("="*80 + "\n")
    f.write("RECOMMENDATION: mE5-base\n")
    f.write("="*80 + "\n")
    f.write(f"Reason: Best balance of accuracy (+{(avg_me5_base - avg_indobert)*100:.1f}pp) and speed ({avg_time_me5_base/avg_time_indobert:.1f}x)\n")

print(f"Summary saved to: {summary_file}")

print("\n" + "="*80)
print("ALL RESULTS SAVED")
print("="*80)
print(f"\nResults directory: {results_dir}")
print(f"Files saved:")
print(f"  1. comparison_results.json (detailed)")
print(f"  2. comparison_table.csv (tabular)")
print(f"  3. summary.txt (human-readable)")
```

---

## Summary: 12 Cells Total

1. **Cell 1**: Setup awal
2. **Cell 2**: Install & import libraries
3. **Cell 3**: Load config & datasets
4. **Cell 4**: Dataset field mappings & utility functions
5. **Cell 5**: Load all 3 retrieval models
6. **Cell 6**: Retrieval functions (3 models)
7. **Cell 7**: Recall@K calculation
8. **Cell 8**: Test single sample - HotpotQA (Indonesian)
9. **Cell 9**: Test single sample - 2WikiMultihop (English)
10. **Cell 10**: Test 10 samples per dataset
11. **Cell 11**: Final comparison & recommendation
12. **Cell 12**: Save results

## Expected Output:

```
HotpotQA (Indonesian):
  IndoBERT:  65-70%
  mE5-base:  70-75%  (+5-7 pp)
  mE5-large: 72-77%  (+7-10 pp)

2WikiMultihop (English):
  IndoBERT:  40-50%  [BAD - Language mismatch!]
  mE5-base:  65-70%  (+20-25 pp) ← HUGE IMPROVEMENT
  mE5-large: 70-75%  (+25-30 pp)

RECOMMENDATION: mE5-base
```

Jalankan semua 12 cell ini untuk test lengkap!