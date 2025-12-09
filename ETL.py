Baik! Saya buatkan cell untuk **testing question decomposition** dengan visualisasi stage-by-stage dan space untuk jawaban!

## CELL: Test Question Decomposition dengan Visualisasi Stage

```python
print("="*100)
print("TEST QUESTION DECOMPOSITION - STAGE-BY-STAGE VISUALIZATION")
print("="*100)

import getpass

# Setup OpenAI API (jika belum)
try:
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print("OpenAI API already connected")
except:
    print("Setting up OpenAI API...")
    api_key = getpass.getpass("Enter OpenAI API key: ")
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    print("OpenAI API connected")

def decompose_question_visualized(question, dataset_name):
    """
    Decompose question dan visualisasi stage-by-stage
    """
    
    decomposition_prompt = f"""Analyze this multi-hop question and decompose it into sequential sub-questions.

QUESTION: {question}

QUESTION TYPES & DECOMPOSITION RULES:

1. BRIDGE QUESTIONS (requires finding intermediate entity):
   - Pattern: "What X does Y have?" where Y's property needs to be found first
   - Example: "Apa agama dari negara tempat Ajay Chabra lahir?"
   - Decomposition:
     Stage 1: Find intermediate entity (Where was Ajay Chabra born?)
     Stage 2: Use Stage 1 answer (What is the religion of [ANSWER_STAGE_1]?)

2. COMPARISON QUESTIONS (requires comparing attributes):
   - Pattern: "Which/Who/What ... more/less/older/younger/earlier/later ... A or B?"
   - Example: "Which film director was born later, director of Film A or director of Film B?"
   - Decomposition:
     Stage 1: Find entity A
     Stage 2: Find attribute of entity A (e.g., birth date)
     Stage 3: Find entity B
     Stage 4: Find attribute of entity B
     (Final synthesis will compare)

3. INTERSECTION QUESTIONS (requires finding common elements):
   - Pattern: "What do X and Y have in common?"
   - Example: "What genre do Film A and Film B share?"
   - Decomposition:
     Stage 1: Find property of X
     Stage 2: Find property of Y
     (Final synthesis will find intersection)

DETAILED EXAMPLES:

Example 1 - BRIDGE:
Q: "Apa agama dari negara tempat Ajay Chabra lahir?"
{{
  "question_type": "bridge",
  "reasoning": "Need to find birth country first, then find its religion",
  "num_stages": 2,
  "sub_questions": [
    {{"stage": 1, "question": "Di negara mana Ajay Chabra lahir?", "purpose": "Find birth country", "depends_on": []}},
    {{"stage": 2, "question": "Apa agama mayoritas di [ANSWER_STAGE_1]?", "purpose": "Find religion of that country", "depends_on": [1]}}
  ]
}}

Example 2 - COMPARISON (with nested attributes):
Q: "Film mana yang memiliki sutradara yang lahir lebih belakangan, El Extraño Viaje atau Love In Pawn?"
{{
  "question_type": "comparison",
  "reasoning": "Need to find both directors' birth dates, then compare",
  "num_stages": 4,
  "sub_questions": [
    {{"stage": 1, "question": "Siapa sutradara El Extraño Viaje?", "purpose": "Find director of film A", "depends_on": []}},
    {{"stage": 2, "question": "Kapan [ANSWER_STAGE_1] lahir?", "purpose": "Find birth date of director A", "depends_on": [1]}},
    {{"stage": 3, "question": "Siapa sutradara Love In Pawn?", "purpose": "Find director of film B", "depends_on": []}},
    {{"stage": 4, "question": "Kapan [ANSWER_STAGE_3] lahir?", "purpose": "Find birth date of director B", "depends_on": [3]}}
  ]
}}

Example 3 - COMPARISON (direct attributes):
Q: "Majalah mana yang didirikan lebih dulu, Arthur's Magazine atau First for Women?"
{{
  "question_type": "comparison",
  "reasoning": "Direct comparison of founding dates",
  "num_stages": 2,
  "sub_questions": [
    {{"stage": 1, "question": "Kapan Arthur's Magazine didirikan?", "purpose": "Find founding year of magazine A", "depends_on": []}},
    {{"stage": 2, "question": "Kapan First for Women didirikan?", "purpose": "Find founding year of magazine B", "depends_on": []}}
  ]
}}

Now decompose this question:
QUESTION: {question}

First, identify the question type (bridge/comparison/intersection), then provide the decomposition.

Return ONLY valid JSON with these fields:
- question_type: string
- reasoning: string (explain why this decomposition)
- num_stages: integer
- sub_questions: array with stage, question, purpose, depends_on

JSON:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a multi-hop question decomposition expert. 
You must:
1. Identify question type (bridge/comparison/intersection)
2. Decompose into ALL necessary sub-questions
3. For bridge: find intermediate entities first
4. For comparison: find ALL attributes being compared
5. Use [ANSWER_STAGE_N] placeholders for dependencies
6. Include depends_on field to show dependencies
Return valid JSON only."""
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
        return result

    except Exception as e:
        print(f"Error: {e}")
        return None

def visualize_decomposition(question, decomposition_result, gold_answer=None):
    """
    Visualize decomposition dengan space untuk jawaban
    """
    
    print(f"\n{'='*100}")
    print("QUESTION DECOMPOSITION VISUALIZATION")
    print(f"{'='*100}")
    
    print(f"\nOriginal Question:")
    print(f"  {question}")
    
    if gold_answer:
        print(f"\nGold Answer:")
        print(f"  {gold_answer}")
    
    print(f"\n{'-'*100}")
    print("DECOMPOSITION ANALYSIS")
    print(f"{'-'*100}")
    
    print(f"\nQuestion Type: {decomposition_result.get('question_type', 'unknown').upper()}")
    print(f"Number of Stages: {decomposition_result.get('num_stages', 0)}")
    print(f"\nReasoning:")
    print(f"  {decomposition_result.get('reasoning', 'N/A')}")
    
    print(f"\n{'='*100}")
    print("STAGE-BY-STAGE BREAKDOWN")
    print(f"{'='*100}")
    
    sub_questions = decomposition_result.get('sub_questions', [])
    
    for sq in sub_questions:
        stage = sq['stage']
        question_text = sq['question']
        purpose = sq.get('purpose', 'N/A')
        depends_on = sq.get('depends_on', [])
        
        print(f"\n{'-'*100}")
        print(f"STAGE {stage}")
        print(f"{'-'*100}")
        
        print(f"\nSub-question:")
        print(f"  {question_text}")
        
        print(f"\nPurpose:")
        print(f"  {purpose}")
        
        if depends_on:
            print(f"\nDepends on:")
            print(f"  Stage(s): {', '.join(map(str, depends_on))}")
            print(f"  (Uses answers from previous stage(s))")
        else:
            print(f"\nDepends on:")
            print(f"  None (independent stage)")
        
        # Space for answer
        print(f"\n┌{'─'*98}┐")
        print(f"│ ANSWER STAGE {stage}:                                                                              │")
        print(f"│                                                                                                  │")
        print(f"│ [ Space for answer from Stage {stage} ]                                                            │")
        print(f"│                                                                                                  │")
        print(f"└{'─'*98}┘")
    
    # Final synthesis section
    print(f"\n{'='*100}")
    print("FINAL SYNTHESIS")
    print(f"{'='*100}")
    
    print(f"\nCombine answers from all stages:")
    for sq in sub_questions:
        print(f"  Stage {sq['stage']}: [ANSWER_STAGE_{sq['stage']}]")
    
    print(f"\n┌{'─'*98}┐")
    print(f"│ FINAL ANSWER:                                                                                    │")
    print(f"│                                                                                                  │")
    print(f"│ [ Synthesized answer from all stages ]                                                          │")
    print(f"│                                                                                                  │")
    print(f"└{'─'*98}┘")
    
    print(f"\n{'='*100}")

print("Functions loaded successfully")
```

## CELL: Test Decomposition - HotpotQA Sample

```python
print("="*100)
print("TEST 1: HOTPOTQA SAMPLE - COMPARISON QUESTION")
print("="*100)

# Get HotpotQA sample
hotpot_samples = get_samples_list(datasets['hotpotqa'], 'hotpotqa')
hotpot_sample = hotpot_samples[0]

question = get_question(hotpot_sample, 'hotpotqa')
gold_answer = get_answer(hotpot_sample, 'hotpotqa')

print(f"\nDecomposing question...")
print(f"This may take 5-10 seconds...")

decomposition = decompose_question_visualized(question, 'hotpotqa')

if decomposition:
    visualize_decomposition(question, decomposition, gold_answer)
    
    # Summary
    print(f"\n{'='*100}")
    print("DECOMPOSITION SUMMARY")
    print(f"{'='*100}")
    
    print(f"\nQuestion Type: {decomposition['question_type']}")
    print(f"Total Stages: {decomposition['num_stages']}")
    
    # Check if all entities are covered
    print(f"\nStage Questions:")
    for i, sq in enumerate(decomposition['sub_questions'], 1):
        has_dependency = len(sq.get('depends_on', [])) > 0
        dep_marker = " (depends on previous)" if has_dependency else " (independent)"
        print(f"  {i}. {sq['question']}{dep_marker}")
else:
    print("Failed to decompose question")
```

## CELL: Test Decomposition - 2WikiMultihop Sample

```python
print("="*100)
print("TEST 2: 2WIKIMULTIHOP SAMPLE - COMPARISON QUESTION")
print("="*100)

# Get 2WikiMultihop sample
wiki_samples = get_samples_list(datasets['2wikimultihop'], '2wikimultihop')
wiki_sample = wiki_samples[0]

question = get_question(wiki_sample, '2wikimultihop')
gold_answer = get_answer(wiki_sample, '2wikimultihop')

print(f"\nDecomposing question...")
print(f"This may take 5-10 seconds...")

decomposition = decompose_question_visualized(question, '2wikimultihop')

if decomposition:
    visualize_decomposition(question, decomposition, gold_answer)
    
    # Summary
    print(f"\n{'='*100}")
    print("DECOMPOSITION SUMMARY")
    print(f"{'='*100}")
    
    print(f"\nQuestion Type: {decomposition['question_type']}")
    print(f"Total Stages: {decomposition['num_stages']}")
    
    print(f"\nStage Questions:")
    for i, sq in enumerate(decomposition['sub_questions'], 1):
        has_dependency = len(sq.get('depends_on', [])) > 0
        dep_marker = " (depends on previous)" if has_dependency else " (independent)"
        print(f"  {i}. {sq['question']}{dep_marker}")
    
    # Dependency graph
    print(f"\nDependency Graph:")
    for sq in decomposition['sub_questions']:
        stage = sq['stage']
        deps = sq.get('depends_on', [])
        if deps:
            print(f"  Stage {stage} <- depends on Stage(s) {deps}")
        else:
            print(f"  Stage {stage} <- independent")
else:
    print("Failed to decompose question")
```

## CELL: Test Multiple Questions (Different Types)

```python
print("="*100)
print("TEST 3: MULTIPLE QUESTIONS - DIFFERENT TYPES")
print("="*100)

# Test questions
test_questions = [
    {
        "question": "Majalah mana yang didirikan lebih dulu, Arthur's Magazine atau First for Women?",
        "dataset": "hotpotqa",
        "expected_type": "comparison",
        "expected_stages": 2
    },
    {
        "question": "Film mana yang memiliki sutradara yang lahir lebih belakangan, El Extraño Viaje atau Love In Pawn?",
        "dataset": "2wikimultihop",
        "expected_type": "comparison",
        "expected_stages": 4
    },
    {
        "question": "Apa agama dari negara tempat Ajay Chabra lahir?",
        "dataset": "hotpotqa",
        "expected_type": "bridge",
        "expected_stages": 2
    },
    {
        "question": "What is the place of birth of the director of film Blind Shaft?",
        "dataset": "2wikimultihop",
        "expected_type": "bridge",
        "expected_stages": 2
    }
]

results = []

for i, test in enumerate(test_questions, 1):
    print(f"\n{'='*100}")
    print(f"TEST {i}/{len(test_questions)}: {test['expected_type'].upper()}")
    print(f"{'='*100}")
    
    print(f"\nQuestion: {test['question']}")
    print(f"Expected Type: {test['expected_type']}")
    print(f"Expected Stages: {test['expected_stages']}")
    
    print(f"\nDecomposing...")
    decomposition = decompose_question_visualized(test['question'], test['dataset'])
    
    if decomposition:
        actual_type = decomposition.get('question_type', 'unknown')
        actual_stages = decomposition.get('num_stages', 0)
        
        # Check correctness
        type_correct = actual_type.lower() == test['expected_type'].lower()
        stages_correct = actual_stages == test['expected_stages']
        
        print(f"\n{'-'*100}")
        print("DECOMPOSITION RESULT")
        print(f"{'-'*100}")
        
        print(f"\nActual Type: {actual_type} {'✓' if type_correct else '✗ MISMATCH'}")
        print(f"Actual Stages: {actual_stages} {'✓' if stages_correct else '✗ MISMATCH'}")
        
        print(f"\nReasoning: {decomposition.get('reasoning', 'N/A')}")
        
        print(f"\nStage Breakdown:")
        for sq in decomposition['sub_questions']:
            stage = sq['stage']
            q = sq['question']
            purpose = sq.get('purpose', 'N/A')
            deps = sq.get('depends_on', [])
            
            dep_str = f" <- Stage(s) {deps}" if deps else " (independent)"
            print(f"  Stage {stage}{dep_str}")
            print(f"    Q: {q}")
            print(f"    Purpose: {purpose}")
        
        # Store result
        results.append({
            'question': test['question'],
            'expected_type': test['expected_type'],
            'actual_type': actual_type,
            'type_correct': type_correct,
            'expected_stages': test['expected_stages'],
            'actual_stages': actual_stages,
            'stages_correct': stages_correct,
            'decomposition': decomposition
        })
    else:
        print(f"\n✗ Decomposition failed")
        results.append({
            'question': test['question'],
            'expected_type': test['expected_type'],
            'actual_type': 'failed',
            'type_correct': False,
            'expected_stages': test['expected_stages'],
            'actual_stages': 0,
            'stages_correct': False
        })

# Summary of all tests
print(f"\n{'='*100}")
print("OVERALL DECOMPOSITION TEST SUMMARY")
print(f"{'='*100}")

correct_type = sum(1 for r in results if r['type_correct'])
correct_stages = sum(1 for r in results if r['stages_correct'])
total = len(results)

print(f"\nAccuracy:")
print(f"  Question Type: {correct_type}/{total} ({correct_type/total*100:.0f}%)")
print(f"  Number of Stages: {correct_stages}/{total} ({correct_stages/total*100:.0f}%)")

print(f"\nDetailed Results:")
for i, r in enumerate(results, 1):
    type_marker = '✓' if r['type_correct'] else '✗'
    stages_marker = '✓' if r['stages_correct'] else '✗'
    print(f"\n  Test {i}: {type_marker}{stages_marker}")
    print(f"    Q: {r['question'][:70]}...")
    print(f"    Type: {r['expected_type']} -> {r['actual_type']}")
    print(f"    Stages: {r['expected_stages']} -> {r['actual_stages']}")
```

## CELL: Visualize Dependency Graph

```python
print("="*100)
print("TEST 4: DEPENDENCY GRAPH VISUALIZATION")
print("="*100)

def visualize_dependency_graph(decomposition):
    """
    Visualize stage dependencies as a graph
    """
    
    print(f"\nDependency Graph:")
    print(f"{'='*60}")
    
    sub_questions = decomposition.get('sub_questions', [])
    
    # Build dependency map
    dep_map = {}
    for sq in sub_questions:
        stage = sq['stage']
        deps = sq.get('depends_on', [])
        dep_map[stage] = deps
    
    # Visualize
    for stage in sorted(dep_map.keys()):
        deps = dep_map[stage]
        
        if not deps:
            # Independent stage
            print(f"\n  Stage {stage}")
            print(f"    |")
            print(f"    └─> (independent)")
        else:
            # Has dependencies
            print(f"\n  Stage {stage}")
            print(f"    |")
            for dep in deps:
                print(f"    ├─> depends on Stage {dep}")
                print(f"    |   (uses [ANSWER_STAGE_{dep}])")
    
    print(f"\n{'='*60}")
    
    # Show execution order
    print(f"\nExecution Order:")
    print(f"{'-'*60}")
    
    # Simple topological sort
    executed = set()
    order = []
    
    while len(executed) < len(sub_questions):
        for sq in sub_questions:
            stage = sq['stage']
            deps = sq.get('depends_on', [])
            
            if stage not in executed:
                # Check if all dependencies are executed
                can_execute = all(d in executed for d in deps)
                
                if can_execute:
                    order.append(stage)
                    executed.add(stage)
                    
                    if deps:
                        print(f"  {len(order)}. Execute Stage {stage} (after Stage(s) {deps})")
                    else:
                        print(f"  {len(order)}. Execute Stage {stage} (no dependencies)")
    
    print(f"{'-'*60}")

# Test with a complex question
test_question = "Film mana yang memiliki sutradara yang lahir lebih belakangan, El Extraño Viaje atau Love In Pawn?"

print(f"Question: {test_question}")
print(f"\nDecomposing...")

decomposition = decompose_question_visualized(test_question, '2wikimultihop')

if decomposition:
    print(f"\n{'-'*100}")
    print(f"Decomposition: {decomposition['num_stages']} stages")
    print(f"{'-'*100}")
    
    for sq in decomposition['sub_questions']:
        print(f"\nStage {sq['stage']}: {sq['question']}")
    
    visualize_dependency_graph(decomposition)
else:
    print("Decomposition failed")
```

## Expected Output:

```
================================================================================
STAGE-BY-STAGE BREAKDOWN
================================================================================

--------------------------------------------------------------------------------
STAGE 1
--------------------------------------------------------------------------------

Sub-question:
  Siapa sutradara El Extraño Viaje?

Purpose:
  Find director of film A

Depends on:
  None (independent stage)

┌──────────────────────────────────────────────────────────────────────────────┐
│ ANSWER STAGE 1:                                                              │
│                                                                              │
│ [ Space for answer from Stage 1 ]                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

--------------------------------------------------------------------------------
STAGE 2
--------------------------------------------------------------------------------

Sub-question:
  Kapan [ANSWER_STAGE_1] lahir?

Purpose:
  Find birth date of director A

Depends on:
  Stage(s): 1
  (Uses answers from previous stage(s))

┌──────────────────────────────────────────────────────────────────────────────┐
│ ANSWER STAGE 2:                                                              │
│                                                                              │
│ [ Space for answer from Stage 2 ]                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

... (stages 3, 4)

================================================================================
FINAL SYNTHESIS
================================================================================

Combine answers from all stages:
  Stage 1: [ANSWER_STAGE_1]
  Stage 2: [ANSWER_STAGE_2]
  Stage 3: [ANSWER_STAGE_3]
  Stage 4: [ANSWER_STAGE_4]

┌──────────────────────────────────────────────────────────────────────────────┐
│ FINAL ANSWER:                                                                │
│                                                                              │
│ [ Synthesized answer from all stages ]                                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Jalankan cell-cell ini untuk test decomposition dengan visualisasi lengkap!