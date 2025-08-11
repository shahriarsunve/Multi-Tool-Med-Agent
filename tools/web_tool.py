import os
from typing import Any, Dict, List
from .base import Tool

class MedicalWebSearchTool(Tool):
    name = "MedicalWebSearchTool"

    def __init__(self, provider: str = "tavily"):
        self.provider = provider

    def describe(self) -> str:
        return "Web search for general medical knowledge (definitions, symptoms, treatments)."

    def _tavily(self, query: str) -> List[Dict[str, Any]]:
        from tavily import TavilyClient
        tv = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        res = tv.search(query=query, include_answer=True, max_results=5)
        results = []
        for item in res.get("results", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content", "")[:300]
            })
        return results

    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        provider = self.provider.lower()
        try:
            if provider == "tavily":
                items = self._tavily(query)
                if not items:
                    return {"tool": self.name, "result": "No web results."}
                bullets = []
                for it in items:
                    bullets.append(f"- {it.get('title','(no title)')}: {it.get('url')}")
                return {"tool": self.name, "result": "Top references:\n" + "\n".join(bullets)}
            else:
                return {"tool": self.name, "result": f"Provider '{self.provider}' not configured."}
        except Exception as e:
            return {"tool": self.name, "error": str(e), "result": "Search failed."}
