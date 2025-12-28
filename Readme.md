# Event Driven Multilingual AI Translation Pipeline with DeepSeek LLM

A **production ready, serverless AI translation system** that automatically translates uploaded files into multiple languages using a **locally hosted Large Language Model** deployed on **Google Cloud Functions**.

This project demonstrates how to combine **Cloud Native architecture**, **LLMs**, **concurrency**, and **event driven processing** to build a scalable AI service suitable for media, localization, and enterprise workflows.

---

## What This Project Does

Whenever a file is uploaded to a Google Cloud Storage bucket, the system automatically:

- Detects the source language
- Translates the content into multiple target languages
- Preserves original formatting for subtitles and structured data
- Stores translated outputs in a dedicated output bucket
- Prevents duplicate or parallel reprocessing safely

### Supported input formats
- `.txt` plain text files
- `.srt` subtitle files
- `.json` structured transcription data

### Supported target languages
- English  
- Arabic  
- Japanese  

---

## Why This Project Matters

This is not a demo script.

It solves **real problems companies face**:

- Video subtitle localization
- Podcast and media translation
- Multilingual customer support content
- AI driven transcription post processing
- Automated translation pipelines without third party APIs

It also shows **how to deploy LLMs without relying on external SaaS APIs**, giving full control over cost, privacy, and performance.

---

## 🏗️ Architecture Overview

<img width="712" height="527" alt="Screenshot 2025-12-28 at 4 49 33 PM" src="https://github.com/user-attachments/assets/39a29368-7253-4e62-9229-d7052bdc3c68" />

### Event Driven Flow

1. File uploaded to Cloud Storage input folder  
2. Google Cloud Function is triggered automatically  
3. The function downloads and loads a DeepSeek LLM from GCS  
4. Text is chunked and translated concurrently  
5. Outputs are written to a separate translation bucket


## Tech Stack

### Cloud Platform
- Google Cloud Platform  
- Cloud Functions Gen 2  
- Cloud Storage  
- Eventarc  

### AI and NLP
- DeepSeek LLM hosted in GCS  
- HuggingFace Transformers  
- spaCy for sentence segmentation  
- LangDetect for language detection  


## Project Structure

├── main.py                # Cloud Function entry point
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation


---

## Key Features

- **Lazy Model Loading**  
  The LLM is downloaded and loaded only when needed to reduce cold start overhead.

- **Parallel Translation**  
  Sentences are chunked and processed concurrently for speed.

- **Format Preservation**  
  Subtitle timestamps and JSON structure are retained exactly.

- **Safe Execution Locks**  
  `.processing` and `.done` flags prevent race conditions.

- **Language Detection**  
  Automatically detects source language before translation.

---

```
deepseek-input/interview.srt

```

Result:

- Arabic translated subtitle file  
- Japanese translated subtitle file  
- Same timestamps  
- Same line structure  
- Fully automated  

No API calls. No manual steps.


## Author

**Anasieze Ikenna**  
Cloud and AI Engineer  
Focused on Cloud Native AI systems, LLM deployment, and scalable backend design


