from ragflow_sdk import RAGFlow

class RAGFlowQueryInterface:
    def __init__(self, api_key, base_url):
        """
        初始化 RAGFlow 查询接口
        :param api_key: RAGFlow API 密钥
        :param base_url: RAGFlow 服务的基础 URL
        """
        self.ragflow = RAGFlow(api_key=api_key, base_url=base_url)

    def query(self, question, dataset_ids=None, document_ids=None, top_k=5):
        """
        根据问题从 RAGFlow 中获取信息
        :param question: 用户的查询问题
        :param dataset_ids: 要搜索的数据集 ID 列表（可选）
        :param document_ids: 要搜索的文档 ID 列表（可选）
        :param top_k: 返回的最相关知识块数量，默认为 5
        :return: 查询结果，包含相关知识块的列表
        """
    # 如果没有指定 dataset_ids，则获取所有数据集的 ID
        if dataset_ids is None:
            datasets = self.ragflow.list_datasets()
            dataset_ids = [dataset.id for dataset in datasets]

        try:
            # 调用 RAGFlow 的 retrieve 方法检索知识块
            chunks = self.ragflow.retrieve(
                question=question,
                dataset_ids=dataset_ids,
                document_ids=document_ids,
                top_k=top_k,
                # highlight=True  # 启用高亮显示匹配的关键词
            )
            # 将检索到的知识块内容提取出来
            results = [chunk.content for chunk in chunks]
            return results
        except Exception as e:
            print(f"查询过程中发生错误：{e}")
            return []


if __name__ == "__main__":
    api_key = "ragflow-E3MDgxNWI2MGIwZTExZjBiZjQxNGE1YT"
    base_url = "http://127.0.0.1:7999"
    
    ragflow_interface = RAGFlowQueryInterface(api_key=api_key, base_url=base_url)
    
    question = "梅州市发展农业的有利政策"
    results = ragflow_interface.query(question=question)
    
    print("查询结果：")
    for result in results:
        print(result)