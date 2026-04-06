# 🏆 Slooze Software Engineer AI - Technical Challenge Guide

This document provides a comprehensive technical overview and implementation guide for the **AI RAG Agent** and **AI Web Search Agent**, designed for the Slooze Software Engineer AI take-home challenge.

---

## 🏛️ **System Architecture Overview**

The project is built on a "Clean System" philosophy, focusing on **reliability, speed, and minimalist design**. Both agents follow a modular architecture that separates retrieval logic from AI-generation logic.

### 🍱 **Core Components**
- **LLM Engine**: [Groq](https://groq.com/) (using `llama-3.3-70b-versatile`) for blazing-fast inference and high accuracy.
- **RAG Engine**: [FAISS](https://github.com/facebookresearch/faiss) for high-performance vector retrieval and [Sentence Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) for local embeddings.
- **Search Engine**: [DuckDuckGo](https://duckduckgo.com/) (Native API) with a [Google](https://www.google.com/) fallback for 100% search reliability.

---

## 📄 **Challenge A: AI Web Search Agent**
The objective was to build an agent capable of retrieving live information and synthesizing accurate answers with source references.

### ⚙️ **The Search Pipeline**
1.  **Query Sanitization**: Cleans the user query of punctuation and non-essential characters.
2.  **Primary Search (DDG)**: Uses the DuckDuckGo "Auto" backend for non-blocking, high-speed result retrieval.
3.  **Fallback Search (Google)**: If DDG is blocked by the local network, the agent instantly falls back to a Google search results parser.
4.  **AI Synthesis**: The retrieved snippets are passed to **Groq LLM** to generate a concise, grounded answer.
5.  **Evidence Reporting**: Always returns a list of sources for full transparency and verification.

---

## 📄 **Challenge B: PDF RAG Agent**
The objective was to build an agent that processes PDF documents and answers questions based solely on that content.

### ⚙️ **The RAG Pipeline**
1.  **Ingestion**: Processes local PDFs using `pypdf`.
2.  **Chunking**: Splitting the text into **500-token chunks** with a **50-token overlap** to maintain contextual continuity.
3.  **Embedding**: Converts chunks into 384-dimensional vectors locally—no external API is used for embedding.
4.  **Vector Store**: Uses **FAISS** to store and query the vectors for "top-k" most relevant text chunks.
5.  **Gen-AI Loop**: Passes the context and user query to **Gemini 1.5 Flash** (with fallback to **Pro**) for grounded answering.

---

## 🛠️ **Installation & Setup (Starting to Ending)**

### 1. **Preparation**
Ensure you have Python 3.10+ installed. Clone the repository and navigate to the project root.

### 2. **Environment Setup**
Create a virtual environment (`venv`) and install the required libraries:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **API Configuration**
Create a `.env` file in the root directory and add your API keys:
```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

### 4. **Running the Agents**

- **To run the Search Agent**:
```powershell
python agent/web_search_agent.py
```

- **To run the PDF RAG Agent**:
Ensure there is at least one PDF in the `data/` folder.
```powershell
python agent/pdf_rag.py
```

---

## 🚀 **Key Design Decisions**
- **Why Groq?** We prioritized speed. Groq provides the fastest inference on the market, making the AI feel like it's thinking in real-time.
- **Why Local Embeddings?** Local embedding generation ensures that we don't hit rate limits on external APIs during high-volume document processing.
- **Why FAISS?** It is an industry-standard for vector search, allowing this project to scale perfectly even if thousands of documents are added.
- **Why Dual Search?** Internet connectivity can be unpredictable. By providing a 5th-layer redundancy (DDG + Google), the system is production-hardened against network blocks.

---

## ✅ **Submission Details**
- **Author**: Yuvaraj
- **Role**: Software Engineer AI
- **Repository**: [ai-agent-rag-search](https://github.com/yuvarajaug-ctrl/ai-agent-rag-search)
