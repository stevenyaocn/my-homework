# from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
import os


class TextProcessor:
    def __init__(self):
        self.embeder = DashScopeEmbeddings(
            # model_name="all-MiniLM-L6-v2"
            model="text-embedding-v2",  # DashScope 的 Embedding 模型
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
        )
