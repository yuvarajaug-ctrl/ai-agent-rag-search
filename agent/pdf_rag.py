import os
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
from dotenv import load_dotenv

import google.generativeai as genai

# Locate Project Root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)  # Goes up one level to z:/slooze-project

# Load API keys from root
load_dotenv(os.path.join(ROOT_DIR, ".env"))
API_KEY = os.getenv("GEMINI_API_KEY")

class PDFAgent:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        
        # Configure Gemini
        if API_KEY:
            genai.configure(api_key=API_KEY)
            # Using the latest stable aliases confirmed for the API key
            self.model_name = 'gemini-flash-latest'
            self.llm = genai.GenerativeModel(self.model_name)
        else:
            print("[!] WARNING: GEMINI_API_KEY not found in .env file.")

    def load_pdf(self, file_path):
        """Extract text from a PDF file."""
        print(f"Reading PDF: {file_path}...")
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text

    def get_chunks(self, text, chunk_size=500, overlap=50):
        """Split text into overlapping chunks."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        self.chunks = chunks
        return chunks

    def create_vector_store(self, chunks):
        """Convert text chunks into embeddings and store in FAISS."""
        print("Generating embeddings...")
        embeddings = self.model.encode(chunks)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))

    def save_index(self, folder_path='faiss_store'):
        """Save the FAISS index and chunks to disk."""
        if not os.path.exists(folder_path): os.makedirs(folder_path)
        faiss.write_index(self.index, os.path.join(folder_path, "index.faiss"))
        with open(os.path.join(folder_path, "chunks.pkl"), "wb") as f:
            pickle.dump(self.chunks, f)

    def load_index(self, folder_path='faiss_store'):
        """Load the FAISS index and chunks from disk."""
        print("Loading existing index...")
        self.index = faiss.read_index(os.path.join(folder_path, "index.faiss"))
        with open(os.path.join(folder_path, "chunks.pkl"), "rb") as f:
            self.chunks = pickle.load(f)

    def ask(self, query, top_k=3):
        """The main RAG query flow: Retrieve -> Augment -> Generate."""
        # 1. Retrieve
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        
        relevant_chunks = [self.chunks[i] for i in indices[0]]
        context = "\n---\n".join(relevant_chunks)
        
        # 2. Augment & Generate
        prompt = f"""
        You are a helpful AI assistant. Answer the question based ONLY on the provided context from a PDF.
        If the answer is not in the context, say you don't know.
        
        CONTEXT:
        {context}
        
        QUESTION: 
        {query}
        
        ANSWER:
        """
        
        try:
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback for robustness
            if "not found" in str(e).lower() or "404" in str(e):
                try:
                    fallback_llm = genai.GenerativeModel('gemini-pro-latest')
                    response = fallback_llm.generate_content(prompt)
                    return response.text
                except Exception as fe:
                    return f"Error: {fe}"
            return f"Error calling Gemini: {e}"

    def summarize(self):
        """Specifically handle the 'Summarize the document' requirement of Challenge B."""
        print("Generating document summary...")
        # Take the most important chunks (first few usually contain the intro/core)
        # or use a map-reduce strategy. For this challenge, we'll use the top 5 chunks.
        intro_context = "\n---\n".join(self.chunks[:10]) 
        
        prompt = f"""
        Summarize the following PDF document content based on these core chunks. 
        Provide a high-level overview and mention the main topics covered.

        CONTENT:
        {intro_context}
        
        SUMMARY:
        """
        return self.ask(prompt)

# --- Main Interaction Script ---
if __name__ == "__main__":
    agent = PDFAgent()
    
    faiss_path = os.path.join(ROOT_DIR, 'faiss_store')
    idx_file = os.path.join(faiss_path, 'index.faiss')
    chunks_file = os.path.join(faiss_path, 'chunks.pkl')

    # If the index and chunks exist, load them; otherwise, build them.
    if os.path.exists(idx_file) and os.path.exists(chunks_file):
        agent.load_index(faiss_path)
    else:
        # Create storage folder if missing
        if not os.path.exists(faiss_path): os.makedirs(faiss_path)
        
        data_folder = os.path.join(ROOT_DIR, 'data')
        if not os.path.exists(data_folder): 
            print(f"Error: Could not find 'data' folder at {data_folder}")
            exit()
            
        pdf_files = [f for f in os.listdir(data_folder) if f.endswith('.pdf')]
        if pdf_files:
            # Process the first PDF found
            pdf_path = os.path.join(data_folder, pdf_files[0])
            raw_text = agent.load_pdf(pdf_path)
            chunks = agent.get_chunks(raw_text)
            agent.create_vector_store(chunks)
            agent.save_index(faiss_path)
            print(f"[+] Successfully indexed: {pdf_files[0]}")
        else:
            print(f"Please add a PDF to the '{data_folder}' folder first.")
            exit()

    # Now, let's test it!
    print("\n--- PDF Agent Ready ---")
    while True:
        user_query = input("\nAsk your PDF a question (or type 'exit'): ")
        if user_query.lower() in ['exit', 'quit']: break
        
        answer = agent.ask(user_query)
        print(f"\nAI: {answer}")
