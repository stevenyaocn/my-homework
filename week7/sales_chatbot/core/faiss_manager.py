import numpy as np
import os
from hashlib import md5
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from typing import Dict, List, Optional, Tuple


class FAISSManager:
    def __init__(self, index_dir: str = "knowledge_base"):
        self.index_dir = os.path.abspath(index_dir)
        self.type_mapping: Dict[str, List[str]] = {}  # 内存中维护 {category: [index_name]}
        os.makedirs(index_dir, exist_ok=True)

    def create_index(self,
                     category: str,
                     documents: List[Document],
                     embeddings: np.ndarray,
                     index_name: Optional[str] = None):
        """
        :param category: 知识库文档类别
        :param documents: 文档列表
        :param embeddings:
        :param index_name:
        :return:
        """

        # 考虑到上传的知识库含有中文等特殊字符，所以需要多上传的知识库进行MD5加密
        print(f"FAISSManager->create_index向量数据库名称：{index_name}")
        index_name = md5(index_name.encode("utf-8")).hexdigest()
        print(f"FAISSManager->create_indexMD5加密后的向量知识库名称：{index_name}")

        # 生成唯一索引名
        if not index_name:
            index_count = len(self.type_mapping.get(category, []))
            index_name = f"{category}_{index_count}"

        print(f"FAISSManager->create_index最终确定的向量知识库名称：{index_name}")

        # 创建FAISS索引
        texts = [doc.page_content for doc in documents]
        db = FAISS.from_texts(texts=texts, embedding=embeddings)
        # 保存索引文件
        """
        在较新版本的 langchain_community.vectorstores.faiss 中，save_local() 方法的参数签名已经发生了变化，
        不再接受 file_name 参数。相反，它现在只需要 folder_path 参数，索引会自动保存在该目录下的 index.faiss 和 index.pkl 文件中
        比如：FAISS 索引文件将保存在 ./index_dir/index_name目录下
        包含 index.faiss 和 index.pkl 两个文件。
        """
        index_path = os.path.join(self.index_dir, index_name)
        db.save_local(folder_path=index_path)

        print(f"FAISSManager->create_index原知识库类别和向量知识库映射关系：{self.type_mapping}")

        # 维护类型映射
        if category not in self.type_mapping:
            self.type_mapping[category] = []
        if index_name not in self.type_mapping[category]:
            self.type_mapping[category].append(index_name)

        print(f"FAISSManager->create_index维护后的知识库类别和向量知识库映射关系：{self.type_mapping}")
        pass

    def search_index(
            self,
            category: str,
            query: str,
            embeddings: np.ndarray,
            top_k: int = 1
    ) -> Optional[List[Tuple[str, float]]]:
        """
        使用 as_retriever() 方法进行向量检索 - 返回相似度最高的前k条结果

        :param category: 文档类别
        :param query: 查询文本
        :param embeddings: 嵌入模型
        :param top_k: 返回结果数量
        :return: 前5个匹配内容列表 或 None
        """
        # 输入验证
        if not query or not category or top_k <= 0:
            return None

        # 1. 加载索引（带缓存）
        if not hasattr(self, '_retriever_cache'):
            self._retriever_cache = {}

        if category not in self._retriever_cache:
            retrievers = []
            for index_name in self.type_mapping.get(category, []):
                index_path = os.path.join(self.index_dir, index_name)
                try:
                    db = FAISS.load_local(
                        folder_path=index_path,
                        embeddings=embeddings,
                        allow_dangerous_deserialization=True
                    )
                    # 创建检索器并设置top_k参数
                    retriever = db.as_retriever(
                        search_type="similarity_score_threshold",
                        search_kwargs={
                            "k": top_k,
                            "score_threshold": 0.3
                        }
                    )
                    retrievers.append(retriever)
                except Exception as e:
                    print(f"加载索引 {index_name} 失败: {str(e)}")
                    continue

            if not retrievers:
                return None

            self._retriever_cache[category] = retrievers

        retrievers = self._retriever_cache[category]

        # 2. 执行检索
        all_results = []
        for retriever in retrievers:
            try:
                # 使用retriever获取结果
                docs = retriever.get_relevant_documents(query)
                all_results.extend([
                    (doc.page_content, doc.metadata.get('score', 1.0))  # 从metadata中获取分数，默认1.0
                    for doc in docs
                    if hasattr(doc, 'page_content')
                ])
            except Exception as e:
                print(f"检索异常: {str(e)}")
                continue

        if not all_results:
            return None

        # 3. 去重处理（保留最高分）
        unique_results = {}
        for doc, score in all_results:
            if doc not in unique_results or score > unique_results[doc]:
                unique_results[doc] = score

        # 4. 按分数排序并返回前top_k个结果
        sorted_results = sorted(unique_results.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]