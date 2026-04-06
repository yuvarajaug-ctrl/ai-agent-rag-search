from duckduckgo_search import DDGS
with DDGS() as ddgs:
    results = ddgs.text("Gemini 1.5 Flash", region="wt-wt", max_results=1)
    for r in results:
        print(r)
