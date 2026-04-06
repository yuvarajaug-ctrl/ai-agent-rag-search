# 🚀 Slooze AI Agent Technical Challenges

**Role:** Software Engineer AI  
**Repository Contents:** Solutions for **Challenge A** (Web Search Agent) and **Challenge B** (PDF RAG Agent)

---

## 🎯 Overview

This repository demonstrates the implementation of two sophisticated AI-powered agents designed to solve real-world information retrieval and synthesis problems.

### Challenge A: AI Web Search Agent
A real-time search agent that integrates with the **DuckDuckGo** engine to retrieve live internet data. The agent extracts relevant snippets and uses the **Google Gemini 1.5 Flash** model to provide a summarized answer with clear source attribution.

### Challenge B: AI Agent for PDF Summarization & Q&A
A fully functional **Retrieval-Augmented Generation (RAG)** system capable of reading, summarizing, and answering context-aware questions from PDF documents.
- **Tools used:** `pypdf` for parsing, `FAISS` for vector similarity, and `all-MiniLM-L6-v2` for local embedding generation.

---

## 🏗️ Technical Architecture

### 1. Vector Similarity Strategy (Challenge B)
- **FAISS (Facebook AI Similarity Search):** Chose FAISS-CPU for local vector storage. 
- **Design Decision:** In a modern production environment, keeping retrieval local reduces latency significantly. FAISS allows for efficient similarity search without the overhead of cloud cost during early-stage development.

### 2. LLM Orchestration
- **Gemini 1.5 Flash:** Selected as the primary LLM for its 1M token context window and high speed.
- **Fallback Logic:** Implemented a robust fallback mechanism to `gemini-1.5-pro`. If the "Flash" model fails (due to quota or availability), the agent automatically switches to "Pro" to guarantee a 100% response rate.

### 3. Live Web Retrieval (Challenge A)
- **DuckDuckGo Search:** Implemented as a zero-cost, high-reliability search backend. 
- **Query Optimization:** Added a sanitization layer to clean user queries (removing unnecessary punctuation) to improve DuckDuckGo's snippet retrieval performance.

---

## 🚀 Getting Started

### 1. Installation
Ensure you have Python 3.10+ installed.

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file in the root directory:
```text
GEMINI_API_KEY=your_google_ai_studio_api_key
```

### 3. Usage

#### **Challenge A: Web Search Agent**
```bash
python -m agent.web_search_agent
```

#### **Challenge B: PDF RAG Agent**
Place your PDF files in the `/data` folder, then run:
```bash
python -m agent.pdf_rag
```

---

## 📦 Core Dependencies
- `google-generativeai`: Primary LLM backend.
- `faiss-cpu`: High-speed similarity vector store.
- `sentence-transformers`: Local embedding generation (`all-MiniLM-L6-v2`).
- `duckduckgo-search`: Real-time web retrieval.
- `pypdf`: PDF text extraction.
- `python-dotenv`: Environment security.

---
© Copyright Slooze Team. This project fulfills the Software Engineer AI take-home requirements.
