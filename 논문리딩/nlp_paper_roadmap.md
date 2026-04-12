# NLP 핵심 논문 로드맵

> 월 / 목마다 1편씩 읽기

---

## 📚 1단계 · Word Representation

| 논문 | 발행처 | 상태 |
|------|--------|------|
| **Word2Vec** — Mikolov et al., 2013 | arXiv | ✅ 완료 |
| **GloVe: Global Vectors for Word Representation** — Pennington et al., 2014 | EMNLP 2014 | |

---

## 🔁 2단계 · RNN / LSTM / GRU / 인코더·디코더

| 논문 | 발행처 | 비고 |
|------|--------|------|
| [**Finding Structure in Time**](https://doi.org/10.1207/S15516709COG1402_1) — Elman (1990) | Cognitive Science | RNN 구조를 정립한 논문 |
| **Learning Long-Term Dependencies with Gradient Descent is Difficult** — Bengio et al. (1994) | IEEE Trans. Neural Networks | |
| **Long Short-Term Memory** — Hochreiter & Schmidhuber (1997) | Neural Computation (MIT Press) | |
| **Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation** — Cho et al. (2014) | EMNLP 2014 | GRU 제안 논문 |
| **Generating Sequences With Recurrent Neural Networks** — Graves (2013) | arXiv | 시퀀스 모델링 응용 |
| **Sequence to Sequence Learning with Neural Networks** — Sutskever et al. (2014) | NeurIPS 2014 | |

---

## 🤖 3단계 · Transformer

| 논문 | 발행처 | 비고 |
|------|--------|------|
| [**Deep Residual Learning for Image Recognition**](https://arxiv.org/abs/1512.03385) — He et al. (2016) | CVPR 2016 | |
| [**Neural Machine Translation by Jointly Learning to Align and Translate**](https://arxiv.org/pdf/1409.0473) — Bahdanau et al. (2015) | ICLR 2015 | |
| [**Effective Approaches to Attention-based Neural Machine Translation**](https://dl.acm.org/doi/10.5555/3305381.3305510) — Luong et al. (2015) | EMNLP 2015 | |
| [**Attention is All You Need**](https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html) — Vaswani et al. (2017) | NeurIPS 2017 | 인용 ~120,000회 |

---

## 🧠 4단계 · Pre-trained Models

| 논문 | 발행처 | 비고 |
|------|--------|------|
| [**ELMo: Deep contextualized word representations**](https://ar5iv.labs.arxiv.org/html/1810.04805) — Peters et al. (2018) | NAACL 2018 | |
| [**BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding**](https://aclanthology.org/N19-1423/) — Devlin et al. (2019) | NAACL 2019 | 인용 ~100,000회 |
| [**RoBERTa: A Robustly Optimized BERT Pretraining Approach**](https://ar5iv.labs.arxiv.org/html/1907.11692) — Liu et al. (2019) | arXiv | |
| **T5: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer** — Raffel et al. (2020) | JMLR 2020 | 학술지 게재 |
| [**Language Models are Few-Shot Learners**](https://samuelalbanie.com/digests/2022-07-gpt-3/) — Brown et al. (2020) | NeurIPS 2020 | GPT-3 |
| [**Training language models to follow instructions with human feedback**](https://proceedings.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract-Conference.html) — Ouyang et al. (2022) | NeurIPS 2022 | InstructGPT |
| [**Chain-of-Thought Prompting Elicits Reasoning in Large Language Models**](https://proceedings.neurips.cc/paper_files/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract-Conference.html) — Wei et al. (2022) | NeurIPS 2022 | |

### 자연어 생성 및 평가 지표 (선택적)

| 논문 | 발행처 |
|------|--------|
| [**BLEU: a Method for Automatic Evaluation of Machine Translation**](https://aclanthology.org/2025.mcg-1.pdf) — Papineni et al. (2002) | ACL 2002 |
| [**ROUGE: A Package for Automatic Evaluation of Summaries**](https://aclanthology.org/W04-1013/) — Lin (2004) | ACL Workshop 2004 |

---

## 🔍 5단계 · RAG / QA / 지식 베이스

### RAG

| 논문 | 발행처 |
|------|--------|
| [**Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**](https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf) — Lewis et al. (2020) | NeurIPS 2020 |
| [**REALM: Retrieval-Augmented Language Model Pre-training**](https://openreview.net/pdf?id=drYpdSnRJk) — Guu et al. (2020) | ICML 2020 |

### QA

| 논문 | 발행처 |
|------|--------|
| **SQuAD: 100,000+ Questions for Machine Comprehension of Text** — Rajpurkar et al. (2016) | EMNLP 2016 |
| **HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering** — Yang et al. (2018) | EMNLP 2018 |

### KG 기반 QA

| 논문 | 발행처 |
|------|--------|
| [**Semantic Parsing on Freebase from Question-Answer Pairs**](https://aclanthology.org/W14-2416.pdf) — Berant et al. (2013) | EMNLP 2013 |
| [**The Value of Semantic Parse Labeling for Knowledge Base Question Answering**](https://aclanthology.org/P16-2033/) — Yih et al. (2016) | ACL 2016 |
| **QA-GNN: Reasoning with Language Models and Knowledge Graphs** — Yasunaga et al. (2021) | NAACL 2021 |
| **Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (FiD)** — Izacard & Grave (2021) | EACL 2021 |

### 지식 베이스

| 논문 | 발행처 |
|------|--------|
| **The Semantic Web** — Berners-Lee et al. (2001) | Scientific American |
| [**Unifying Large Language Models and Knowledge Graphs: A Roadmap**](http://www.comp.hkbu.edu.hk/~xinhuang/publications/pdfs/TKDE25-Survey.pdf) — Pan et al. (2024) | IEEE TKDE |
| [**Freebase: A Collaboratively Created Graph Database for Structuring Human Knowledge**](https://dl.acm.org/doi/abs/10.1145/2736277.2741651) — Bollacker et al. (2008) | ACM SIGMOD 2008 |
| **WordNet: A Lexical Database for English** — Miller (1995) | Communications of the ACM |
| **DBpedia: A Nucleus for a Web of Open Data** — Auer et al. (2007) | ISWC 2007 |

---

## ⚙️ 지식 증류 / 경량화

| 논문 | 발행처 |
|------|--------|
| [**Distilling the Knowledge in a Neural Network**](https://openreview.net/pdf?id=drYpdSnRJk) — Hinton et al. (2015) | arXiv + NeurIPS Workshop 2014 |
| **LoRA: Low-Rank Adaptation of Large Language Models** — Hu et al. (2022) | ICLR 2022 |

---

## 📰 학술지(Journal) 게재 논문 정리

> NLP/ML 분야는 학회 발표가 학술지 못지않게 권위 있음. 아래는 전통적 의미의 학술지 게재 논문.

| 논문 | 학술지 | 출판사 |
|------|--------|--------|
| **Finding Structure in Time** — Elman (1990) | Cognitive Science, Vol.14 | Wiley |
| **Learning Long-Term Dependencies** — Bengio et al. (1994) | IEEE Transactions on Neural Networks, Vol.5 | IEEE |
| **Long Short-Term Memory** — Hochreiter & Schmidhuber (1997) | Neural Computation, Vol.9(8) | MIT Press |
| **WordNet** — Miller (1995) | Communications of the ACM | ACM |
| **The Semantic Web** — Berners-Lee et al. (2001) | Scientific American | Springer Nature |
| **T5** — Raffel et al. (2020) | Journal of Machine Learning Research (JMLR) | JMLR.org |
| **LLMs and Knowledge Graphs** — Pan et al. (2024) | IEEE Transactions on Knowledge and Data Engineering (TKDE) | IEEE |
