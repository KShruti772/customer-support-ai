# Datasets Directory

This directory contains all datasets for the Multi-Agent AI Customer Support Assistant project.

## Overview

The datasets are organized into categorical subdirectories based on their primary use case. Total size is approximately **12 GB** with the complaints dataset being the largest.

**⚠️ Important:** 
- Large datasets (raw/) should NOT be committed to Git
- Documentation files (README.md, manifests/) ARE committed
- See `.gitignore` in this directory for specific rules

---

## Directory Structure

```
datasets/
├── intent_detection/        → Banking sector intent classification
├── retrieval/               → Large-scale passage retrieval corpus & queries
├── qa_datasets/             → Question-answering datasets (QA)
├── customer_support/        → Customer complaints & multilingual dialogues
├── manifests/               → Structured metadata for all datasets
└── README.md                → This file
```

---

## 1. Intent Detection

### Location: `intent_detection/banking77/`

**Dataset Name:** BANKING77  
**Source:** Hugging Face Datasets / Financial Intent Detection  
**Purpose:** Fine-tune models for customer intent classification in banking domain  
**File Format:** CSV

**Files:**
- `raw/train.csv` - 10,014 training examples
- `raw/test.csv` - 3,083 test examples

**Schema:**
```
text,category
"I am still waiting on my card?", "card_arrival"
```

**Key Characteristics:**
- ✓ Balanced across 77 banking intent categories
- ✓ Real customer inquiries
- ✓ Train/test split already provided
- ✓ Ready for fine-tuning

**Project Use:**
- Train intent router agent
- Classify incoming customer messages
- Route to appropriate support agent (billing, technical, product, FAQ, etc.)

**Size:** ~1 MB  
**Should be in Git:** NO (dataset files)

---

## 2. Retrieval (Information Retrieval)

### Location: `retrieval/msmarco/`

**Dataset Name:** MS MARCO (v1)  
**Source:** Microsoft Machine Reading Comprehension  
**Purpose:** Pre-trained passage retrieval corpus; evaluate dense retrieval models  
**File Format:** TSV (Tab-separated values)

**Files:**
- `raw/collection.tsv` - 8,841,823 passages (~2.9 GB)
  - Format: `passage_id<TAB>passage_text`
- `raw/queries.train.tsv` - 808,731 training queries (~33.5 MB)
  - Format: `query_id<TAB>query_text`
- `raw/queries.dev.tsv` - Development queries (~4.24 MB)
- `raw/queries.eval.tsv` - Evaluation queries (~4.25 MB)
- `raw/qrels.dev.tsv` - Relevance judgments for dev queries (~1.15 MB)
  - Format: `query_id<TAB>0<TAB>passage_id<TAB>relevance_score`

**Project Use:**
- **RAG Knowledge Base:** Passages can be indexed for retrieval augmented generation
- **Retrieval Evaluation:** Assess retrieval quality
- **Training Dense Retrievers:** Fine-tune embedding models
- Support FAQ, product, and technical agents with information retrieval

**Important Notes:**
- ⚠️ Collection is VERY large (2.9 GB)
- Requires efficient indexing (FAISS, Elasticsearch, etc.)
- Passages cover diverse topics (academic, news, web)
- Not all passages may be relevant to customer support
- Consider filtering to financial/support-relevant subset

**Size:** 3.1 GB  
**Should be in Git:** NO

---

## 3. Question-Answering Datasets

### Location: `qa_datasets/squad/`

**Dataset Name:** SQuAD v1.1 & v2.0  
**Source:** Stanford Question Answering Dataset  
**Purpose:** Evaluate QA systems; optionally use passages as RAG knowledge base  
**File Format:** JSON (SQuAD format)

**Files:**
- `raw/train-v1.1.json` - 87,599 training examples (~28.89 MB)
- `raw/dev-v1.1.json` - 10,570 dev examples (~4.63 MB)
- `raw/train-v2.0.json` - 130,319 training examples with unanswerable (~40.17 MB)
- `raw/dev-v2.0.json` - 11,873 dev examples with unanswerable (~4.17 MB)

**Schema:**
```json
{
  "data": [
    {
      "title": "String",
      "paragraphs": [
        {
          "context": "Passage text...",
          "qas": [
            {
              "question": "What is...",
              "id": "unique_id",
              "answers": [{"text": "...", "answer_start": 123}],
              "is_impossible": false
            }
          ]
        }
      ]
    }
  ]
}
```

**Key Characteristics:**
- ✓ v1.1: All questions are answerable
- ✓ v2.0: Includes unanswerable questions (more challenging)
- ✓ Wikipedia-based passages and questions
- ✓ Multiple answer spans per question

**Project Use:**
- **Knowledge Base:** Passages can augment FAQ agent with diverse Q&A pairs
- **Evaluation:** Measure QA performance on held-out set
- **Optional:** Train QA model for customer support answers

**Comparison (v1.1 vs v2.0):**
| Aspect | v1.1 | v2.0 |
|--------|------|------|
| Answerable | 100% | ~50% |
| Difficulty | Easier | Harder |
| Use Case | Baseline evaluation | Production-ready evaluation |

**Note:** SQuAD covers general knowledge (history, science, sports), not financial/customer support topics. Useful for baseline evaluation and comparison, but complaints.csv is more domain-relevant.

**Size:** 77 MB  
**Should be in Git:** NO

---

## 4. Customer Support

### Location: `customer_support/`

This directory contains real-world customer data in two subdirectories:

#### 4a. Financial Complaints

**Location:** `customer_support/complaints/`

**Dataset Name:** CFPB Consumer Complaint Database (2023 snapshot)  
**Source:** Consumer Financial Protection Bureau (CFPB)  
**Purpose:** Ground-truth customer support data; knowledge base for complaints agent  
**File Format:** CSV

**File:**
- `raw/complaints.csv` - 23,346,984 real consumer complaints (~8.7 GB)

**Schema (16 columns):**
```csv
Date received,Product,Sub-product,Issue,Sub-issue,
Consumer complaint narrative,Company public response,Company,
State,ZIP code,Tags,Submitted via,Date sent to company,
Company response to consumer,Timely response?,Complaint ID
```

**Key Fields for Customer Support:**
- **Product** (e.g., "Checking or savings account", "Credit card")
- **Sub-product** (e.g., "Checking account", "Credit card")
- **Issue** (e.g., "Managing an account", "Billing disputes")
- **Sub-issue** (e.g., "Deposits and withdrawals")
- **Consumer complaint narrative** - The complaint text (primary data)
- **Company response** - How company responded
- **Company** - Financial institution name
- **Timely response?** - Whether response was timely

**Project Use:**
- **Intent Detection:** Train complaint classifier (issue categorization)
- **Knowledge Base:** FAQ agent can search similar complaints & resolutions
- **Routing:** Determine complaint urgency and route to appropriate agent
- **Response Generation:** Use example responses for complaint resolution agent
- **Evaluation:** Test end-to-end system on real customer scenarios

**Important Notes:**
- ⚠️ MASSIVE dataset (23M+ records, 8.7 GB)
- Consider sampling for local development
- PII is masked (e.g., `{$14000.00}`, `XXXX`)
- Reflects real customer frustration & complex issues
- Highly relevant to customer support domain

**Example Complaint:**
```
Product: Checking or savings account
Issue: Managing an account
Complaint: "In XX/XX/2023 a third party deposited a check... 
My account was frozen. I don't know why..."
Response: "Closed with explanation"
```

**Size:** 8.7 GB  
**Should be in Git:** NO

---

#### 4b. Multilingual Dialogues

**Location:** `customer_support/dialogues/`

**Dataset Name:** Multilingual Dialogue Dataset  
**Source:** Conversational AI research  
**Purpose:** Train & evaluate conversational agents across languages  
**File Format:** Text (dialogue format) + Metadata

**Language Coverage:**
- English (en_*_human.txt)
- German (de_*_human.txt)
- Italian (it_*_human.txt)
- Chinese/Mandarin (zh_*_human.txt)

**Files per Language (4 languages × 3 splits):**

| Split | File | Purpose |
|-------|------|---------|
| Train | `*_train_human.txt` | Model training |
| Dev | `*_dev_human.txt` | Validation & hyperparameter tuning |
| Test | `*_test_human.txt` | Final evaluation |

**Examples:**
- English: `raw/multilingual/en/{en_train_human.txt, en_dev_human.txt, en_test_human.txt}`
- German: `raw/multilingual/de/{de_train_human.txt, de_dev_human.txt, de_test_human.txt}`
- (Similarly for Italian and Chinese)

**Data Format:**
```
Dialogue turn 1 __eou__ Dialogue turn 2 __eou__ ... dialogue_metadata
```

**Metadata Files:**
- `raw/metadata/1k_part_data/dialogues_emotion.txt` - Emotion labels (1k subset)
- `raw/metadata/1k_part_data/dialogues_action.txt` - Action labels (1k subset)
- `raw/metadata/1k_part_data/dialogues_topic.txt` - Topic labels (1k subset)
- `raw/metadata/1k_part_data/dialogues_text_{En,De,It,Zh}.txt` - Language-specific text

**Schema:**
Each dialogue contains:
- Multiple speaker turns separated by `__eou__` (end of utterance)
- Emotion annotation (optional)
- Action/intent annotation (optional)
- Topic annotation (optional)

**Project Use:**
- **Multilingual Support:** Train agents that handle English, German, Italian, Chinese
- **Dialogue Quality Evaluation:** Measure conversational coherence & fluency
- **Intent Recognition:** Extract action/intent from dialogue
- **Emotion Analysis:** Detect customer sentiment during conversation
- **End-to-End Testing:** Evaluate full agent on realistic dialogues

**Sizes:**
- English: ~6.94 MB (train ~5.83 MB)
- German: ~6.37 MB (train ~6.04 MB)
- Italian: ~6.64 MB (train ~5.56 MB)
- Chinese: ~5.95 MB (train ~4.97 MB)

**Total:** ~26 MB  
**Should be in Git:** NO

**Loader Script:**
- `dataset.py` - Hugging Face datasets loader for easy integration with training pipelines

**Usage Example:**
```python
from datasets import load_dataset
dataset = load_dataset("path/to/dataset.py", data_files={
    "train": "raw/multilingual/en/en_train_human.txt",
    "validation": "raw/multilingual/en/en_dev_human.txt",
    "test": "raw/multilingual/en/en_test_human.txt"
})
```

---

## 5. Manifests

### Location: `manifests/`

**Contents:**
- `dataset_manifest.json` - Structured metadata for all datasets
- `registry.json` - Dynamic dataset loading configuration

These files enable programmatic access to dataset information for automated pipelines.

---

## Storage & Git Guidelines

### Files to Commit (Small Metadata)
```
✓ datasets/README.md
✓ datasets/manifests/dataset_manifest.json
✓ datasets/manifests/registry.json
✓ datasets/*/README.md (if created)
✓ datasets/*/.gitkeep (to preserve directory structure)
```

### Files to IGNORE (Large Data)
```
✗ datasets/*/raw/
✗ datasets/*/processed/
✗ datasets/*/*.csv
✗ datasets/*/*.tsv
✗ datasets/*/*.json
✗ datasets/*/*.txt
```

**See `.gitignore` in this directory for exact rules.**

---

## Data Processing Workflow

For each dataset, follow this pattern:

1. **Raw Data** (`raw/`)
   - Original, unmodified files
   - Never change these
   - Safe to re-download if needed

2. **Processed Data** (`processed/`)
   - Cleaned, filtered, or transformed versions
   - Generated by preprocessing scripts
   - NOT in Git (can be regenerated)

3. **Derived Products** (e.g., FAISS indices, embeddings)
   - Store in `processed/`
   - Document in metadata

---

## Dataset Statistics Summary

| Dataset | Type | Size | Records | Purpose |
|---------|------|------|---------|---------|
| BANKING77 | Classification | 1 MB | 13,097 | Intent detection |
| MS MARCO | Retrieval | 3.1 GB | 8.8M passages, 808k queries | RAG corpus |
| SQuAD | QA | 77 MB | 130k+ Q&A pairs | Knowledge base / Evaluation |
| Complaints | Classification/NLU | 8.7 GB | 23.3M complaints | Domain knowledge |
| Dialogues (Multi) | Conversation | 26 MB | ~20k dialogues | Multilingual evaluation |
| **TOTAL** | Mixed | ~12 GB | - | - |

---

## Setup for Development

### Quick Start

1. **Install dataset dependencies:**
   ```bash
   pip install datasets huggingface_hub faiss-cpu pandas
   ```

2. **Load a dataset programmatically:**
   ```python
   import pandas as pd
   
   # Load BANKING77
   banking_train = pd.read_csv("intent_detection/banking77/raw/train.csv")
   
   # Load MS MARCO queries
   queries = pd.read_csv("retrieval/msmarco/raw/queries.dev.tsv", sep='\t', header=None)
   
   # Load SQuAD
   import json
   with open("qa_datasets/squad/raw/train-v2.0.json") as f:
       squad = json.load(f)
   
   # Load complaints
   complaints = pd.read_csv("customer_support/complaints/raw/complaints.csv")
   ```

3. **Sample large datasets locally:**
   ```python
   # Sample for faster iteration
   complaints_sample = complaints.sample(frac=0.01, random_state=42)  # 1% sample
   ```

---

## Important Warnings

⚠️ **Before Using Large Datasets:**
1. **Memory:** Complaints.csv is 8.7 GB; load with chunking or sampling
2. **Storage:** Total 12 GB; ensure sufficient disk space
3. **Privacy:** CFPB complaints contain real customer data (PII masked)
4. **Versioning:** If datasets change, re-run preprocessing pipelines

⚠️ **Domain Mismatch:**
- SQuAD covers general knowledge (Wikipedia topics)
- MS MARCO includes diverse web passages
- Only complaints.csv is specific to financial/customer support
- Consider domain-specific filtering for better performance

---

## Contributing

When adding new datasets:

1. Create appropriate subdirectory under `datasets/`
2. Place raw files in `raw/`
3. Create `README.md` with dataset documentation
4. Update `manifests/dataset_manifest.json`
5. Update this main `README.md`
6. Add entry to `.gitignore` if necessary

---

## Further Documentation

For detailed information about each dataset:
- See individual `README.md` files in each subdirectory (coming soon)
- See `manifests/dataset_manifest.json` for machine-readable metadata
- Refer to original dataset sources:
  - BANKING77: https://huggingface.co/datasets/banking77
  - MS MARCO: https://microsoft.github.io/msmarco/
  - SQuAD: https://rajpurkar.github.io/SQuAD-explorer/
  - CFPB Complaints: https://www.consumerfinance.gov/data-research/consumer-complaints/
  - Multilingual Dialogues: (Academic source)

---

**Last Updated:** 2026-08-16  
**Organized By:** ML/Data Engineering Team  
**Status:** ✓ Phase 1-5 Complete
