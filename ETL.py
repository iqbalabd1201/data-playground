====================================================================================================
QUICK TEST: 10 HOTPOTQA SAMPLES
====================================================================================================

Testing 10 HotpotQA samples...
Expected time: ~5-7 minutes
====================================================================================================
Processing:   0%|          | 0/10 [00:00<?, ?it/s]
====================================================================================================
SAMPLE 1 - HOTPOTQA
====================================================================================================
Main Question: Majalah mana yang didirikan lebih dulu Arthur's Magazine atau First for Women?
Gold Answer: Arthur's Magazine
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 2 stages:
  Stage 1: Kapan Arthur's Magazine didirikan?
    Purpose: Find founding year of Arthur's Magazine
  Stage 2: Kapan First for Women didirikan?
    Purpose: Find founding year of First for Women

================================================================================
STAGE 1
================================================================================
Current Question: Kapan Arthur's Magazine didirikan?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✓ Arthur's Magazine                                  (score: 0.5106)
    [2] ✗ Echosmith                                          (score: 0.4485)

  Generating answer with K=2...
  Answer: 1844
  Confidence: 0.90
  Reasoning: Arthur's Magazine didirikan pada tahun 1844, seperti disebutkan dalam Passage 1.
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Kapan First for Women didirikan?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Arthur's Magazine

    P2P Retrieved 3 passages:
      [1] ✓ Arthur's Magazine                             (source, sim: 0.5106)
      [2] ✗ Radio City (Indian radio station)             (P2P, sim: 0.6915)
      [3] ✓ First for Women                               (P2P, sim: 0.6774)

    Testing P2P with full multi-stage context...
    P2P Answer: 1989
    P2P Confidence: 0.90
    P2P Reasoning: First for Women didirikan pada tahun 1989, seperti yang disebutkan dalam Passage 3.
    ✓ P2P SUCCESSFUL (conf 0.90 >= 0.8)
    → Using P2P result, skipping Q2P

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Arthur's Magazine

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Arthur's Magazine
Gold Answer: Arthur's Magazine
Total unique passages used: 4
Number of stages: 2
Processing:  10%|█         | 1/10 [00:09<01:22,  9.13s/it]
[1/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: Arthur's Magazine

====================================================================================================
SAMPLE 2 - HOTPOTQA
====================================================================================================
Main Question: Keluarga Oberoi adalah bagian dari perusahaan hotel yang memiliki kantor pusat di kota mana?
Gold Answer: Delhi
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 2 stages:
  Stage 1: Apa nama perusahaan hotel yang dimiliki oleh Keluarga Oberoi?
    Purpose: Find the name of the hotel company owned by the Oberoi family
  Stage 2: Di kota mana [ANSWER_STAGE_1] memiliki kantor pusat?
    Purpose: Find the city where the hotel company has its headquarters

================================================================================
STAGE 1
================================================================================
Current Question: Apa nama perusahaan hotel yang dimiliki oleh Keluarga Oberoi?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✓ Oberoi family                                      (score: 0.6208)
    [2] ✓ The Oberoi Group                                   (score: 0.5535)

  Generating answer with K=2...
  Answer: The Oberoi Group
  Confidence: 0.90
  Reasoning: Keluarga Oberoi terlibat dalam hotel melalui The Oberoi Group (Passage 1).
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Di kota mana The Oberoi Group memiliki kantor pusat?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Oberoi family

    P2P Retrieved 3 passages:
      [1] ✓ Oberoi family                                 (source, sim: 0.6208)
      [2] ✗ Mohan Singh Oberoi                            (P2P, sim: 0.7268)
      [3] ✗ Hotel Tallcorn                                (P2P, sim: 0.6530)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada informasi mengenai lokasi kantor pusat The Oberoi Group dalam konteks yang diberikan.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 2 question: 'Di kota mana The Oberoi Group memiliki kantor pusat?'

    Q2P Retrieved 2 passages:
      [1] ✓ Oberoi family                                 (Q2P score: 0.6599)
      [2] ✓ The Oberoi Group                              (Q2P score: 0.6341)

    Generating answer with Q2P passages...
    Q2P Answer: Delhi
    Q2P Confidence: 0.90
    Q2P Reasoning: The Oberoi Group memiliki kantor pusat di Delhi, seperti disebutkan dalam Passage 2.
    ✓ Using Q2P result

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Delhi

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Delhi
Gold Answer: Delhi
Total unique passages used: 2
Number of stages: 2
Processing:  20%|██        | 2/10 [00:19<01:19,  9.88s/it]
[2/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: Delhi

====================================================================================================
SAMPLE 3 - HOTPOTQA
====================================================================================================
Main Question: Musisi dan satiris Allie Goertz menulis lagu tentang karakter "The Simpsons" Milhouse, yang dinamai Matt Groening setelah siapa?
Gold Answer: President Richard Nixon
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 3 stages:
  Stage 1: Siapa Milhouse dalam 'The Simpsons'?
    Purpose: Find out who Milhouse is in 'The Simpsons'
  Stage 2: Siapa Matt Groening?
    Purpose: Find out who Matt Groening is
  Stage 3: Siapa yang dinamai Milhouse oleh Matt Groening?
    Purpose: Find out who Milhouse is named after by Matt Groening

================================================================================
STAGE 1
================================================================================
Current Question: Siapa Milhouse dalam 'The Simpsons'?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✓ Allie Goertz                                       (score: 0.5970)
    [2] ✗ The Simpsons: An Uncensored, Unauthorized History  (score: 0.5809)

  Generating answer with K=2...
  Answer: Karakter dari acara 'The Simpsons'
  Confidence: 0.90
  Reasoning: Milhouse disebut sebagai subjek lagu Allie Goertz yang berfokus pada 'The Simpsons' (Passage 1).
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Siapa Matt Groening?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Allie Goertz

    P2P Retrieved 3 passages:
      [1] ✓ Allie Goertz                                  (source, sim: 0.5970)
      [2] ✗ Marge Simpson                                 (P2P, sim: 0.8813)
      [3] ✗ Bart Simpson                                  (P2P, sim: 0.8756)

    Testing P2P with full multi-stage context...
    P2P Answer: Kartunis menciptakan 'The Simpsons'
    P2P Confidence: 0.90
    P2P Reasoning: Matt Groening adalah kartunis yang menciptakan dan merancang karakter dalam 'The Simpsons', seperti yang dijelaskan dalam Passage 2 dan Passage 3.
    ✓ P2P SUCCESSFUL (conf 0.90 >= 0.8)
    → Using P2P result, skipping Q2P

================================================================================
STAGE 3
================================================================================
Current Question: Siapa yang dinamai Milhouse oleh Matt Groening?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Allie Goertz

    P2P Retrieved 3 passages:
      [1] ✓ Allie Goertz                                  (source, sim: 0.5970)
      [2] ✗ Homer Simpson                                 (P2P, sim: 0.8751)
      [3] ✗ List of The Simpsons video games              (P2P, sim: 0.8683)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada informasi tentang siapa yang dinamai Milhouse oleh Matt Groening dalam konteks yang diberikan.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 3 question: 'Siapa yang dinamai Milhouse oleh Matt Groening?'

    Q2P Retrieved 2 passages:
      [1] ✓ Milhouse Van Houten                           (Q2P score: 0.5769)
      [2] ✗ Bart Simpson                                  (Q2P score: 0.5432)

    Generating answer with Q2P passages...
    Q2P Answer: Richard Nixon
    Q2P Confidence: 0.90
    Q2P Reasoning: Milhouse dinamai berdasarkan nama tengah Presiden Richard Nixon, seperti yang disebutkan dalam Passage 1.
    ✓ Using Q2P result

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Richard Nixon

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Richard Nixon
Gold Answer: President Richard Nixon
Total unique passages used: 5
Number of stages: 3
Processing:  30%|███       | 3/10 [00:37<01:34, 13.52s/it]
[3/10] EM: 0 | F1: 0.80 | Judge: CORRECT | Answer: Richard Nixon

====================================================================================================
SAMPLE 4 - HOTPOTQA
====================================================================================================
Main Question: Kewarganegaraan apa yang dimiliki istri James Henry Miller?
Gold Answer: American
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 2 stages:
  Stage 1: Siapa istri James Henry Miller?
    Purpose: Find the name of James Henry Miller's wife
  Stage 2: Apa kewarganegaraan [ANSWER_STAGE_1]?
    Purpose: Find the nationality of James Henry Miller's wife

================================================================================
STAGE 1
================================================================================
Current Question: Siapa istri James Henry Miller?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✗ June Miller                                        (score: 0.5647)
    [2] ✗ James Henry Deakin (junior)                        (score: 0.5626)

  Generating answer with K=2...
  Answer: Tidak ada informasi
  Confidence: 1.00
  Reasoning: Tidak ada informasi tentang istri James Henry Miller dalam konteks.
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Apa kewarganegaraan Tidak ada informasi?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: June Miller

    P2P Retrieved 3 passages:
      [1] ✗ June Miller                                   (source, sim: 0.5647)
      [2] ✓ Ewan MacColl                                  (P2P, sim: 0.7356)
      [3] ✗ Jim Miller (Australian footballer, born 1919) (P2P, sim: 0.6740)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada informasi tentang kewarganegaraan istri James Henry Miller dalam konteks yang diberikan.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 2 question: 'Apa kewarganegaraan Tidak ada informasi?'

    Q2P Retrieved 2 passages:
      [1] ✗ Incest: From a Journal of Love                (Q2P score: 0.3025)
      [2] ✗ Launceston by-election, 1874                  (Q2P score: 0.2999)

    Generating answer with Q2P passages...
    Q2P Answer: Tidak ada informasi
    Q2P Confidence: 1.00
    Q2P Reasoning: Tidak ada informasi tentang istri James Henry Miller dalam konteks.
    ✓ Using Q2P result

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Tidak ada informasi

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Tidak ada informasi
Gold Answer: American
Total unique passages used: 4
Number of stages: 2
Processing:  40%|████      | 4/10 [00:48<01:14, 12.38s/it]
[4/10] EM: 0 | F1: 0.00 | Judge: INCORRECT | Answer: Tidak ada informasi

====================================================================================================
SAMPLE 5 - HOTPOTQA
====================================================================================================
Main Question: Cadmium Chloride sedikit larut dalam bahan kimia ini, itu juga disebut apa?
Gold Answer: alcohol
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 3 stages:
  Stage 1: Apa itu Cadmium Chloride?
    Purpose: Find definition or description of Cadmium Chloride
  Stage 2: Dalam bahan kimia apa Cadmium Chloride sedikit larut?
    Purpose: Identify the chemical in which Cadmium Chloride is slightly soluble
  Stage 3: Apa nama lain dari Cadmium Chloride?
    Purpose: Find alternative names for Cadmium Chloride

================================================================================
STAGE 1
================================================================================
Current Question: Apa itu Cadmium Chloride?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✗ Water blue                                         (score: 0.5204)
    [2] ✗ Gold(III) chloride                                 (score: 0.4994)

  Generating answer with K=2...
  Answer: Tidak ada informasi
  Confidence: 1.00
  Reasoning: Tidak ada informasi tentang Cadmium Chloride dalam konteks yang diberikan.
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Dalam bahan kimia apa Cadmium Chloride sedikit larut?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Water blue

    P2P Retrieved 3 passages:
      [1] ✗ Water blue                                    (source, sim: 0.5204)
      [2] ✗ Benzamide                                     (P2P, sim: 0.8392)
      [3] ✓ Cadmium chloride                              (P2P, sim: 0.8240)

    Testing P2P with full multi-stage context...
    P2P Answer: Alkohol
    P2P Confidence: 0.90
    P2P Reasoning: Cadmium chloride sedikit larut dalam alkohol, menurut Passage 3.
    ✓ P2P SUCCESSFUL (conf 0.90 >= 0.8)
    → Using P2P result, skipping Q2P

================================================================================
STAGE 3
================================================================================
Current Question: Apa nama lain dari Cadmium Chloride?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Water blue

    P2P Retrieved 3 passages:
      [1] ✗ Water blue                                    (source, sim: 0.5204)
      [2] ✗ Heptanoic acid                                (P2P, sim: 0.8033)
      [3] ✓ Ethanol                                       (P2P, sim: 0.7976)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada informasi mengenai nama lain dari Cadmium Chloride dalam konteks yang diberikan.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 3 question: 'Apa nama lain dari Cadmium Chloride?'

    Q2P Retrieved 2 passages:
      [1] ✗ Water blue                                    (Q2P score: 0.5491)
      [2] ✗ Gold(III) chloride                            (Q2P score: 0.5348)

    Generating answer with Q2P passages...
    Q2P Answer: Tidak ada informasi
    Q2P Confidence: 0.00
    Q2P Reasoning: Tidak ada informasi mengenai nama lain dari Cadmium Chloride dalam konteks yang diberikan.
    ✓ Using Q2P result

  ────────────────────────────────────────────────────────────────────────────
  [STEP 3] PROGRESSIVE EXPANSION
  ────────────────────────────────────────────────────────────────────────────
    Current confidence: 0.00 < 0.65

    Expanding to K=3...
      + Added: Benzamide
    New Answer: Tidak ada informasi
    New Confidence: 0.00

    Expanding to K=4...
      + Added: Tributyltin oxide
    New Answer: Tidak ada informasi
    New Confidence: 0.00

    Expanding to K=5...
      + Added: Magnesium chloride
    New Answer: Tidak ada informasi
    New Confidence: 0.00

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Alkohol

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Alkohol
Gold Answer: alcohol
Total unique passages used: 6
Number of stages: 3
Processing:  50%|█████     | 5/10 [01:11<01:21, 16.30s/it]
[5/10] EM: 0 | F1: 0.00 | Judge: CORRECT | Answer: Alkohol

====================================================================================================
SAMPLE 6 - HOTPOTQA
====================================================================================================
Main Question: Pemain tenis mana yang memenangkan lebih banyak gelar Grand Slam, Henri Leconte atau Jonathan Stark?
Gold Answer: Jonathan Stark
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 2 stages:
  Stage 1: Berapa banyak gelar Grand Slam yang dimenangkan oleh Henri Leconte?
    Purpose: Find the number of Grand Slam titles won by Henri Leconte
  Stage 2: Berapa banyak gelar Grand Slam yang dimenangkan oleh Jonathan Stark?
    Purpose: Find the number of Grand Slam titles won by Jonathan Stark

================================================================================
STAGE 1
================================================================================
Current Question: Berapa banyak gelar Grand Slam yang dimenangkan oleh Henri Leconte?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✗ 1986 Grand Prix German Open                        (score: 0.5527)
    [2] ✓ Henri Leconte                                      (score: 0.5375)

  Generating answer with K=2...
  Answer: Satu gelar ganda Grand Slam
  Confidence: 0.70
  Reasoning: Henri Leconte memenangkan gelar ganda putra French Open pada 1984 (Passage 2), tetapi tidak ada informasi tentang gelar tunggal Grand Slam yang dimenangkannya.
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Berapa banyak gelar Grand Slam yang dimenangkan oleh Jonathan Stark?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: 1986 Grand Prix German Open

    P2P Retrieved 3 passages:
      [1] ✗ 1986 Grand Prix German Open                   (source, sim: 0.5527)
      [2] ✗ Steffi Graf                                   (P2P, sim: 0.8289)
      [3] ✗ Larisa Neiland                                (P2P, sim: 0.8201)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada informasi tentang gelar Grand Slam Jonathan Stark dalam konteks.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 2 question: 'Berapa banyak gelar Grand Slam yang dimenangkan oleh Jonathan Stark?'

    Q2P Retrieved 2 passages:
      [1] ✓ Jonathan Stark (tennis)                       (Q2P score: 0.5260)
      [2] ✗ 2009 Serena Williams tennis season            (Q2P score: 0.5074)

    Generating answer with Q2P passages...
    Q2P Answer: Dua gelar ganda Grand Slam
    Q2P Confidence: 0.90
    Q2P Reasoning: Jonathan Stark memenangkan dua gelar ganda Grand Slam, yaitu 1994 French Open Men's Doubles dan 1995 Wimbledon Championships Mixed Doubles (Passage 1).
    ✓ Using Q2P result

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Jonathan Stark

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Jonathan Stark
Gold Answer: Jonathan Stark
Total unique passages used: 4
Number of stages: 2
Processing:  60%|██████    | 6/10 [01:25<01:02, 15.51s/it]
[6/10] EM: 1 | F1: 1.00 | Judge: CORRECT | Answer: Jonathan Stark

====================================================================================================
SAMPLE 7 - HOTPOTQA
====================================================================================================
Main Question: Genus ngengat mana di negara terbesar ketujuh di dunia yang hanya memiliki satu spesies?
Gold Answer: Crambidae
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 2 stages:
  Stage 1: Apa negara terbesar ketujuh di dunia?
    Purpose: Find the seventh largest country in the world
  Stage 2: Apa genus ngengat yang hanya memiliki satu spesies di [ANSWER_STAGE_1]?
    Purpose: Find the genus of moth that has only one species in the seventh largest country

================================================================================
STAGE 1
================================================================================
Current Question: Apa negara terbesar ketujuh di dunia?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✗ List of companies of India                         (score: 0.5641)
    [2] ✗ Geography of India                                 (score: 0.4214)

  Generating answer with K=2...
  Answer: India
  Confidence: 0.90
  Reasoning: India disebut sebagai negara terbesar ketujuh di dunia dalam Passage 1 dan Passage 2.
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Apa genus ngengat yang hanya memiliki satu spesies di India?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: List of companies of India

    P2P Retrieved 3 passages:
      [1] ✗ List of companies of India                    (source, sim: 0.5641)
      [2] ✓ India                                         (P2P, sim: 0.8214)
      [3] ✗ Parectropis                                   (P2P, sim: 0.5943)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada informasi tentang genus ngengat di India dalam konteks.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 2 question: 'Apa genus ngengat yang hanya memiliki satu spesies di India?'

    Q2P Retrieved 2 passages:
      [1] ✓ Indogrammodes                                 (Q2P score: 0.6989)
      [2] ✗ Nepita                                        (Q2P score: 0.6775)

    Generating answer with Q2P passages...
    Q2P Answer: Indogrammodes
    Q2P Confidence: 0.90
    Q2P Reasoning: Indogrammodes adalah genus ngengat dengan satu spesies di India (Passage 1).
    ✓ Using Q2P result

================================================================================
FINAL ANSWER SYNTHESIS
================================================================================
✓ Synthesized final answer: Indogrammodes

====================================================================================================
FINAL RESULT
====================================================================================================
Final Answer: Indogrammodes
Gold Answer: Crambidae
Total unique passages used: 4
Number of stages: 2
Processing:  70%|███████   | 7/10 [01:37<00:43, 14.40s/it]
[7/10] EM: 0 | F1: 0.00 | Judge: INCORRECT | Answer: Indogrammodes

====================================================================================================
SAMPLE 8 - HOTPOTQA
====================================================================================================
Main Question: Siapa yang pernah dianggap sebagai kick boxer terbaik di dunia, namun dia terlibat dalam sejumlah kontroversi terkait dengan "perilaku tidak sportif" dalam olahraga dan kejahatan kekerasan di luar ring.
Gold Answer: Badr Hari
Total passages available: 10

────────────────────────────────────────────────────────────────────────────────
Pre-computing passage similarity matrix...
────────────────────────────────────────────────────────────────────────────────
  Computing passage embeddings...
  ✓ Similarity matrix: torch.Size([10, 10])

────────────────────────────────────────────────────────────────────────────────
STEP 1: Question Decomposition
────────────────────────────────────────────────────────────────────────────────
✓ Decomposed into 3 stages:
  Stage 1: Siapa yang dianggap sebagai kick boxer terbaik di dunia?
    Purpose: Find the person considered the best kickboxer in the world
  Stage 2: Apa saja kontroversi yang melibatkan [ANSWER_STAGE_1] terkait dengan perilaku tidak sportif dalam olahraga?
    Purpose: Identify controversies related to unsportsmanlike behavior in sports involving the person
  Stage 3: Apa saja kejahatan kekerasan yang melibatkan [ANSWER_STAGE_1] di luar ring?
    Purpose: Identify violent crimes involving the person outside the ring

================================================================================
STAGE 1
================================================================================
Current Question: Siapa yang dianggap sebagai kick boxer terbaik di dunia?

🔍 Retrieval: Question-to-Passage (Q2P)

  Retrieving top-2 passages...
    [1] ✓ Badr Hari                                          (score: 0.5513)
    [2] ✓ Global Fighting Championship                       (score: 0.4911)

  Generating answer with K=2...
  Answer: Badr Hari
  Confidence: 0.80
  Reasoning: Badr Hari pernah dianggap sebagai kickboxer terbaik di dunia (Passage 1).
  ✓ Sufficient confidence

================================================================================
STAGE 2
================================================================================
Current Question: Apa saja kontroversi yang melibatkan Badr Hari terkait dengan perilaku tidak sportif dalam olahraga?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Badr Hari

    P2P Retrieved 3 passages:
      [1] ✓ Badr Hari                                     (source, sim: 0.5513)
      [2] ✗ Guerra de Titanes (1998)                      (P2P, sim: 0.7513)
      [3] ✗ Verano de Escándalo (1998)                    (P2P, sim: 0.7311)

    Testing P2P with full multi-stage context...
    P2P Answer: Perilaku tidak sportif dan kejahatan kekerasan
    P2P Confidence: 0.90
    P2P Reasoning: Badr Hari terlibat dalam kontroversi perilaku tidak sportif dan kejahatan kekerasan, seperti disebutkan dalam Passage 1.
    ✓ P2P SUCCESSFUL (conf 0.90 >= 0.8)
    → Using P2P result, skipping Q2P

================================================================================
STAGE 3
================================================================================
Current Question: Apa saja kejahatan kekerasan yang melibatkan Badr Hari di luar ring?

🔗 Retrieval: Conditional P2P → Q2P Fallback

  ────────────────────────────────────────────────────────────────────────────
  [STEP 1] TRYING P2P (Passage-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Source passage: Badr Hari

    P2P Retrieved 3 passages:
      [1] ✓ Badr Hari                                     (source, sim: 0.5513)
      [2] ✗ Triplemanía VII                               (P2P, sim: 0.7223)
      [3] ✗ Outrageous Betrayal                           (P2P, sim: 0.6848)

    Testing P2P with full multi-stage context...
    P2P Answer: Tidak ada informasi
    P2P Confidence: 0.00
    P2P Reasoning: Tidak ada detail mengenai kejahatan kekerasan spesifik Badr Hari di luar ring dalam konteks yang diberikan.
    ✗ P2P FAILED (conf 0.00 < 0.8)
    → Discarding P2P result, triggering Q2P fallback...

  ────────────────────────────────────────────────────────────────────────────
  [STEP 2] Q2P FALLBACK (Question-to-Passage)
  ────────────────────────────────────────────────────────────────────────────
    Retrieving based on Stage 3 question: 'Apa saja kejahatan kekerasan yang melibatkan Badr Hari di luar ring?'

    Q2P Retrieved 2 passages:
      [1] ✗ Prosecution of gender-targeted crimes         (Q2P score: 0.4909)
      [2] ✗ Protection racket                             (Q2P score: 0.4196)

    Generating answer with Q2P passages...
    Q2P Answer: Tidak ada informasi
    Q2P Confidence: 0.00
    Q2P Reasoning: Tidak ada informasi mengenai kejahatan kekerasan Badr Hari di luar ring dalam konteks yang diberikan.
    ✓ Using Q2P result

  ────────────────────────────────────────────────────────────────────────────
  [STEP 3] PROGRESSIVE EXPANSION
  ────────────────────────────────────────────────────────────────────────────
    Current confidence: 0.00 < 0.65

    Expanding to K=3...
      + Added: Badr Hari
    New Answer: Tidak ada informasi
    New Confidence: 0.00

    Expanding to K=4...
      + Added: Guerra de Titanes (1998)
    New Answer: Tidak ada informasi
    New Confidence: 0.00

    Expanding to K=5...
      + Added: Global Fighting Championship
