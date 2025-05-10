from week7.sales_chatbot.core.faiss_manager import FAISSManager
from week7.sales_chatbot.core.text_processor import TextProcessor
from week7.sales_chatbot.core.document_loader import KnowledgeLoader
from week7.sales_chatbot.core.search_engine import WebSearchEngine
import os
import re
from typing import List, Tuple


class ChatEngine:
    def __init__(self):
        self.faiss_mgr = FAISSManager()
        self.text_processor = TextProcessor()
        self.search_engine = WebSearchEngine()
        self.loader = KnowledgeLoader()  # 新增加载器实例
        self.max_history_length = 10  # 保留最近5轮对话历史

    def upload_knowledge(self, file_path: str, file_type: str, knowledge_type: str):
        """
        上传知识库
        :param file_path:
        :param file_type:
        :param knowledge_type:
        :return:
        """
        # print(f"上传的知识库文件路径：{file_path}")
        # print(f"知识库类别：{knowledge_type}")
        # 1. 加载文档
        documents = self.loader.load_document(
            file_path=file_path,
            doc_type=file_type,
            knowledge_type=knowledge_type
        )

        print(f"ChatEngine->upload_knowledge加载后的文档：{documents}")

        # 2. 使用文件名作为索引名
        index_name = os.path.splitext(os.path.basename(file_path))[0]

        # 3. 创建FAISS向量数据库索引
        self.faiss_mgr.create_index(
            category=knowledge_type,
            documents=documents,
            embeddings=self.text_processor.embeder,
            index_name=index_name
        )

        return f"问题类型：{knowledge_type}\n知识库'{index_name}'上传成功!"

    def get_response(self, query: str, category: str, history: List[Tuple[str, str]]) -> str:
        """
        根据用户输入的问题，从知识库根据相似度匹配检索答案，如果从知识库没有检索到符合条件的答案。联网检索
        :param query:
        :param category:
        :param history:
        :return:
        """
        try:
            # 1. 知识库检索
            answers = self.faiss_mgr.search_index(
                category=category,
                query=query,
                embeddings=self.text_processor.embeder
            )
            print(f"知识库检索结果：{answers}")

            # 2. 处理对话历史上下文
            # context = self._prepare_context(query, history)
            # print(f"处理后的历史上下文结果：{context}")

            # 3. 网络搜索兜底
            # if not answers:
            #     answers = self._search_web(query=query, category=category)
            #     print(f"联网检索结果：{answers}")
            if answers:
                texts = []
                for ans, _ in answers:
                    results = re.findall(r"\[.*?回答\]：(.*?)(?=\n\n|\Z)", ans, re.DOTALL)
                    if results:
                        for res in results:
                            texts.append(res)
                return "知识库答案：\n"+"\n".join(texts)
            else:
                return "知识库没有检索到符合您问题的答案，待进一步完善联网检索功能..."
        except Exception as e:
            return f"系统错误: {str(e)}"
