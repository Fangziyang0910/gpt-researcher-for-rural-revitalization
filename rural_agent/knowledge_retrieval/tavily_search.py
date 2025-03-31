import os
import requests
import json
from typing import List, Dict, Any
import asyncio
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class TavilySearchInterface:
    """Tavily搜索引擎接口，提供网络搜索功能"""
    
    def __init__(self, api_key: str):
        """
        初始化Tavily搜索接口
        
        Args:
            api_key: Tavily API密钥
        
        Raises:
            ValueError: 当API密钥为空或无效时抛出
        """
        # 检查参数是否存在
        if not api_key:
            raise ValueError("Tavily API Key not found. Please provide a valid API key.")

        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
        self.headers = {"Content-Type": "application/json"}
        
        # 验证API密钥是否有效
        try:
            # 发送一个简单的测试查询
            self.search_sync("test", max_results=1)
            print("Tavily API initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize Tavily API: {str(e)}"
            print(error_msg)
            raise ValueError(error_msg)
    
    async def search(self, 
                    query: str, 
                    max_results: int = 10, 
                    include_domains: List[str] = None,
                    search_depth: str = "basic") -> List[Dict[str, str]]:
        """
        执行Tavily搜索并返回格式化的结果
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            include_domains: 限制在特定域名内搜索
            search_depth: 搜索深度，可选 "basic" 或 "advanced"
            
        Returns:
            格式化的搜索结果列表，每项包含标题、链接和摘要
        
        Raises:
            ValueError: 当搜索请求失败时抛出
        """
        # 准备搜索请求参数
        data = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "api_key": self.api_key,
            "include_answer": False,
            "include_images": False,
            "use_cache": True
        }
        
        try:
            # 发送搜索请求
            response = requests.post(
                self.base_url, 
                data=json.dumps(data), 
                headers=self.headers,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"Tavily搜索失败，状态码：{response.status_code}"
                print(error_msg)
                raise ValueError(error_msg)
            
            # 解析搜索结果
            results = response.json().get("results", [])
            
            # 格式化结果
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "title": item.get("title", "无标题"),
                    "href": item.get("url", ""),
                    "body": item.get("content", "无内容摘要")
                })
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"Tavily搜索过程中发生错误：{str(e)}"
            print(error_msg)
            raise ValueError(error_msg)
    
    def search_sync(self, 
                   query: str, 
                   max_results: int = 7,
                   include_domains: List[str] = None,
                   search_depth: str = "basic") -> List[Dict[str, str]]:
        """
        同步版本的Tavily搜索方法，用于非异步环境
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            include_domains: 限制在特定域名内搜索
            search_depth: 搜索深度，可选 "basic" 或 "advanced"
            
        Returns:
            格式化的搜索结果列表
            
        Raises:
            ValueError: 当搜索请求失败时抛出
        """
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.search(query, max_results, include_domains, search_depth)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            error_msg = f"同步搜索过程中发生错误：{str(e)}"
            print(error_msg)
            raise ValueError(error_msg) 