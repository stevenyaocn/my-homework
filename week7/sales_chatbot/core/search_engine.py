from serpapi import GoogleSearch
import os


class WebSearchEngine:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

    def search(self, query):
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google"
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            return self._parse_results(results)
        except Exception as e:
            return f"搜索失败：{str(e)}"

    def _parse_results(self, results):
        # 解析搜索结果
        return {
            "organic_results": results.get("organic_results", []),
            "answer_box": results.get("answer_box", {})
        }