from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from typing import List
from langchain.schema import Document
import os


class KnowledgeLoader:
    def __init__(self):
        self.knowledge_type_mapping = {}  # 内存中维护知识库类型映射 {filename: type}

    def load_document(self, file_path: str, doc_type: str, knowledge_type: str) -> List[Document]:
        """
        加载知识库文档
        :param file_path:
        :param doc_type:
        :param knowledge_type:
        :return:
        """

        print(f"KnowledgeLoader->load_document知识库文档类型：{doc_type}")

        if doc_type.lower() == "txt":
            loader = TextLoader(file_path=file_path, encoding="utf-8")
        elif doc_type.lower() == "pdf":
            loader = PyMuPDFLoader(file_path=file_path)
        elif doc_type.lower() == "docx":
            loader = Docx2txtLoader(file_path=file_path)
        else:
            raise ValueError(f"不支持该文档类型: {doc_type}")

        # 记录文件到知识库类型的映射
        self.knowledge_type_mapping[os.path.basename(file_path)] = knowledge_type
        print(f"KnowledgeLoader->load_document知识库类型映射关系：{self.knowledge_type_mapping}")

        documents = loader.load()
        print(f"KnowledgeLoader->load_document加载的知识库文档：{documents}")

        # 实例化文本分割器
        text_spliter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        print(f"KnowledgeLoader->load_document分割器：{text_spliter}")
        # 分割文本
        return text_spliter.split_documents(documents=documents)