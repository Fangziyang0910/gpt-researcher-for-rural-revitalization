import os
from dotenv import load_dotenv
from ragflow_sdk import RAGFlow

# 加载 .env 文件中的环境变量
load_dotenv()

class RAGFlowQueryInterface:
    def __init__(self, api_key: str, base_url: str):
        """
        初始化 RAGFlow 查询接口。
        
        Args:
            api_key: RAGFlow API密钥
            base_url: RAGFlow 基础URL
        """
        # 检查参数是否存在
        if not api_key:
            raise ValueError("RAGFlow API Key not found. Please provide a valid API key.")
        if not base_url:
            raise ValueError("RAGFlow Base URL not found. Please provide a valid base URL.")

        self.api_key = api_key
        self.base_url = base_url

        # 初始化RAGFlow客户端
        try:
            self.ragflow = RAGFlow(api_key=self.api_key, base_url=self.base_url)
            print(f"RAGFlow SDK initialized for URL: {self.base_url}")
        except Exception as e:
            print(f"Failed to initialize RAGFlow SDK: {e}")
            raise # Re-raise the exception after logging

    def query(self, question, dataset_ids=None, document_ids=None, top_k=5):
        """
        根据问题从 RAGFlow 中获取信息
        :param question: 用户的查询问题
        :param dataset_ids: 要搜索的数据集 ID 列表（可选）
        :param document_ids: 要搜索的文档 ID 列表（可选）
        :param top_k: 返回的最相关知识块数量，默认为 5
        :return: 查询结果，包含相关知识块内容的列表 (注意：之前返回的是列表，现在保持一致)
        """
        # 如果没有指定 dataset_ids，则获取所有数据集的 ID 
        if dataset_ids is None:
            try:
                datasets = self.ragflow.list_datasets()
                dataset_ids = [dataset.id for dataset in datasets]
            except Exception as e:
                print(f"无法获取数据集列表: {e}. 将尝试不带 dataset_ids 查询。")
                dataset_ids = None # 或者根据需要处理

        try:
            # 调用 RAGFlow 的 retrieve 方法检索知识块
            chunks = self.ragflow.retrieve(
                question=question,
                dataset_ids=dataset_ids,
                document_ids=document_ids,
                top_k=top_k,
            )
            # 将检索到的知识块内容提取出来
            results = [chunk.content for chunk in chunks]
            return results
        except Exception as e:
            print(f"查询 RAGFlow 过程中发生错误：{e}")
            return [] # 返回空列表表示查询失败 