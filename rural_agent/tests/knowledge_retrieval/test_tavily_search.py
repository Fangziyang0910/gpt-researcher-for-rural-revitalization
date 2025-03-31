import pytest
import asyncio
from typing import Dict, Any, Callable
from rural_agent.knowledge_retrieval.tavily_search import TavilySearchInterface

class TestTavilySearchInterface:
    """TavilySearchInterface的测试类"""
    
    @pytest.fixture
    def search_interface(self, tavily_api_key: str) -> TavilySearchInterface:
        """创建TavilySearchInterface实例"""
        return TavilySearchInterface(api_key=tavily_api_key)
    
    def test_initialization(self, tavily_api_key: str):
        """测试接口初始化"""
        # 测试正常初始化
        interface = TavilySearchInterface(api_key=tavily_api_key)
        assert interface.api_key == tavily_api_key
        assert interface.base_url == "https://api.tavily.com/search"
        
        # 测试空API密钥
        with pytest.raises(ValueError) as exc_info:
            TavilySearchInterface(api_key="")
        assert "Tavily API Key not found" in str(exc_info.value)
        
        # 测试无效API密钥
        with pytest.raises(ValueError) as exc_info:
            interface = TavilySearchInterface(api_key="invalid_key_12345")
        assert "Failed to initialize Tavily API" in str(exc_info.value)
    
    def test_sync_search(
        self, 
        search_interface: TavilySearchInterface,
        test_search_queries: Dict[str, Any],
        expected_result_format: Dict[str, type],
        validate_search_result: Callable
    ):
        """测试同步搜索功能"""
        # 使用简单查询进行测试
        query_config = test_search_queries["simple"]
        results = search_interface.search_sync(**query_config)
        
        # 验证返回结果
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= query_config["max_results"]
        
        # 验证每个结果的格式
        for result in results:
            assert validate_search_result(result, expected_result_format)
    
    @pytest.mark.asyncio
    async def test_async_search(
        self, 
        search_interface: TavilySearchInterface,
        test_search_queries: Dict[str, Any],
        expected_result_format: Dict[str, type],
        validate_search_result: Callable
    ):
        """测试异步搜索功能"""
        # 使用高级查询进行测试
        query_config = test_search_queries["advanced"]
        results = await search_interface.search(**query_config)
        
        # 验证返回结果
        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= query_config["max_results"]
        
        # 验证每个结果的格式
        for result in results:
            assert validate_search_result(result, expected_result_format)
    
    @pytest.mark.asyncio
    async def test_concurrent_async_search(
        self, 
        search_interface: TavilySearchInterface,
        test_search_queries: Dict[str, Any],
        expected_result_format: Dict[str, type],
        validate_search_result: Callable
    ):
        """测试并发异步搜索"""
        # 准备多个搜索查询
        queries = [
            test_search_queries["simple"],
            test_search_queries["advanced"],
            test_search_queries["domain_specific"]
        ]
        
        # 并发执行搜索
        tasks = [
            search_interface.search(**query)
            for query in queries
        ]
        results = await asyncio.gather(*tasks)
        
        # 验证所有查询都返回结果
        assert len(results) == len(queries)
        for i, query_results in enumerate(results):
            assert isinstance(query_results, list)
            assert len(query_results) > 0
            assert len(query_results) <= queries[i]["max_results"]
            
            # 验证每个结果的格式
            for result in query_results:
                assert validate_search_result(result, expected_result_format) 