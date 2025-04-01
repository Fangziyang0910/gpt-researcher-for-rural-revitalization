import os
from rural_agent.knowledge_retrieval.ragflow_interface import RAGFlowQueryInterface
from rural_agent.config.rural_config import RuralConfig

class RuralPlanOrchestrator:
    """
    顶层协调器，负责管理乡村振兴方案生成的整个流程。
    配置信息通过 RuralConfig 类管理。
    """
    def __init__(self):
        """
        初始化协调器。
        """
        # 初始化配置
        self.config = RuralConfig()
        
        # 初始化 RAGFlow 检索器
        self._init_ragflow_retriever()
        
        # 初始化 Tavily 检索器
        self._init_tavily_retriever()
        
    def _init_ragflow_retriever(self):
        """初始化 RAGFlow 检索器"""
        # 检查是否有必要的配置
        if not self.config.ragflow_api_key or not self.config.ragflow_base_url:
            print("RAGFlow disabled: missing API key or base URL.")
            self.ragflow_retriever = None
            return

        try:
            self.ragflow_retriever = RAGFlowQueryInterface(
                api_key=self.config.ragflow_api_key,
                base_url=self.config.ragflow_base_url
            )
            print("RAGFlow Retriever initialized successfully.")
        except ValueError as e:
            print(f"Warning: {e}. RAGFlow retrieval will be unavailable.")
            self.ragflow_retriever = None
        except Exception as e:
            print(f"Error initializing RAGFlow Query Interface: {e}")
            self.ragflow_retriever = None 
            
    def _init_tavily_retriever(self):
        """初始化 Tavily 检索器"""
        # 检查是否有必要的配置
        if not self.config.tavily_api_key:
            print("Tavily disabled: missing API key.")
            self.tavily_retriever = None
            return
            
        try:
            from gpt_researcher.retrievers.tavily.tavily_search import TavilySearch
            # 在这里我们不直接初始化检索器，因为它需要查询参数
            # 我们将在需要进行查询时创建实例
            print("Tavily Retriever initialized successfully.")
            self.tavily_api_key = self.config.tavily_api_key
            self.tavily_retriever_available = True
        except ImportError as e:
            print(f"Warning: {e}. Tavily retrieval will be unavailable.")
            self.tavily_retriever_available = False
        except Exception as e:
            print(f"Error initializing Tavily Retriever: {e}")
            self.tavily_retriever_available = False
            
    def search_with_tavily(self, query, topic="general", query_domains=None, max_results=10):
        """
        使用Tavily执行搜索查询
        
        Args:
            query (str): 搜索查询字符串
            topic (str, optional): 搜索主题，默认为"general"
            query_domains (list, optional): 要包含在搜索中的域名列表，默认为None
            max_results (int, optional): 返回的最大结果数，默认为10
            
        Returns:
            list: 搜索结果列表，每个结果包含'href'和'body'键
        """
        if not hasattr(self, 'tavily_retriever_available') or not self.tavily_retriever_available:
            print("Tavily retriever is not available. Unable to perform search.")
            return []
            
        try:
            from gpt_researcher.retrievers.tavily.tavily_search import TavilySearch
            
            # 创建包含API密钥的请求头
            headers = {"tavily_api_key": self.tavily_api_key}
            
            # 实例化Tavily搜索
            tavily_search = TavilySearch(
                query=query,
                headers=headers,
                topic=topic,
                query_domains=query_domains
            )
            
            # 执行搜索
            results = tavily_search.search(max_results=max_results)
            
            return results
        except Exception as e:
            print(f"Error searching with Tavily: {e}")
            return [] 