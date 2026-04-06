import os
import sys
from dotenv import load_dotenv
from groq import Groq
from duckduckgo_search import DDGS
from googlesearch import search

# --- Setup & Configuration ---
# Locate environment variables in the project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
load_dotenv(os.path.join(ROOT_DIR, ".env"))

class WebSearchAgent:
    """A clean, dual-strategy AI search agent powered by Groq."""
    
    def __init__(self, model_name='llama-3.3-70b-versatile'):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or "gsk_" not in self.api_key:
            print("[!] FATAL: GROQ_API_KEY not set in .env file.")
            sys.exit(1)
            
        self.client = Groq(api_key=self.api_key)
        self.model_name = model_name

    def perform_search(self, query, max_results=5):
        """Primary DDG Search with a clean Google Fallback."""
        results = []
        clean_query = query.strip()
        print(f"[*] Reserching: '{clean_query}'...")

        # 1. Primary Strategy: DuckDuckGo
        try:
            with DDGS() as ddgs:
                ddg_data = list(ddgs.text(clean_query, max_results=max_results))
                if ddg_data:
                    print(f"  [+] Success: Data retrieved via DuckDuckGo.")
                    return [{"title": r['title'], "body": r['body'], "href": r['href']} for r in ddg_data]
        except Exception as e:
            print(f"  [-] DuckDuckGo unavailable, switching to fallback...")

        # 2. Fallback Strategy: Google
        try:
            google_data = list(search(clean_query, num_results=max_results, advanced=True))
            if google_data:
                print(f"  [+] Success: Data retrieved via Google.")
                return [{"title": r.title, "body": r.description, "href": r.url} for r in google_data]
        except Exception as e:
            print(f"  [!] Fallback failed: {e}")

        return []

    def ask(self, query):
        """Orchestrate Search -> Context Preparation -> LLM Synthesis."""
        # Step 1: Retrieval
        search_results = self.perform_search(query)
        if not search_results:
            return "Unable to retrieve search results at this time. Please try again.", []

        # Step 2: Context Preparation
        context_blocks = []
        source_urls = []
        for i, res in enumerate(search_results, 1):
            context_blocks.append(f"Result [{i}]:\nTitle: {res['title']}\nSnippet: {res['body']}\nURL: {res['href']}")
            source_urls.append(res['href'])
            
        # Step 3: Synthesis via Groq
        prompt = f"""
        Answer this query: '{query}'
        
        Using only the following search context:
        {chr(10).join(context_blocks)}
        
        Answer concisely and accurately:
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1024
            )
            return completion.choices[0].message.content, source_urls
        except Exception as e:
            return f"AI Generation Error: {e}", source_urls

# --- Execution ---
if __name__ == "__main__":
    # Initialize the high-performance search agent
    agent = WebSearchAgent()
    
    print("\n" + "="*40)
    print("AI Web Search Agent Active")
    print("="*40)
    
    while True:
        try:
            user_input = input("\nEnter your query (or 'exit'): ").strip()
            if user_input.lower() in ['exit', 'quit']: break
            if not user_input: continue
            
            print("Thinking...\n")
            ans, sources = agent.ask(user_input)
            
            print(f"Answer: {ans}")
            print("\nSources:")
            for s in sources: print(f"- {s}")
            
        except KeyboardInterrupt:
            break
