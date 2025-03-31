"""pytest配置文件，包含共享的测试配置和fixture"""

import os
import pytest
from typing import Dict, Any

# 启用异步测试支持
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """配置pytest-asyncio插件"""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as requiring asyncio"
    )

# 共享的API密钥fixture
@pytest.fixture
def tavily_api_key() -> str:
    """获取Tavily API密钥"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        pytest.skip("需要设置TAVILY_API_KEY环境变量来运行测试")
    return api_key

@pytest.fixture
def ragflow_api_key() -> str:
    """获取RAGFlow API密钥"""
    api_key = os.getenv("RAGFLOW_API_KEY")
    if not api_key:
        pytest.skip("需要设置RAGFLOW_API_KEY环境变量来运行测试")
    return api_key

@pytest.fixture
def ragflow_base_url() -> str:
    """获取RAGFlow基础URL"""
    base_url = os.getenv("RAGFLOW_BASE_URL")
    if not base_url:
        pytest.skip("需要设置RAGFLOW_BASE_URL环境变量来运行测试")
    return base_url

# 共享的测试数据
@pytest.fixture
def test_search_queries() -> Dict[str, Any]:
    """常用的测试搜索查询"""
    return {
        "simple": {
            "query": "Python programming language",
            "max_results": 3
        },
        "advanced": {
            "query": "Rural development in China",
            "max_results": 5,
            "search_depth": "advanced"
        },
        "domain_specific": {
            "query": "Smart agriculture technology",
            "max_results": 3,
            "include_domains": ["gov.cn", "edu.cn"]
        }
    }

@pytest.fixture
def expected_result_format() -> Dict[str, type]:
    """搜索结果的预期格式"""
    return {
        "title": str,
        "href": str,
        "body": str
    }

# 共享的验证函数
@pytest.fixture
def validate_search_result():
    """验证搜索结果的格式"""
    def _validate(result: Dict[str, Any], expected_format: Dict[str, type]) -> bool:
        try:
            assert isinstance(result, dict), "结果必须是字典类型"
            for key, expected_type in expected_format.items():
                assert key in result, f"缺少必需的键：{key}"
                assert isinstance(result[key], expected_type), f"{key}的类型不正确"
                assert result[key], f"{key}不能为空"
            return True
        except AssertionError as e:
            print(f"验证失败：{str(e)}")
            return False
    return _validate 