import pytest
from rural_agent.knowledge_retrieval.ragflow_interface import RAGFlowQueryInterface

def test_ragflow_interface_initialization():
    """测试RAGFlow接口的初始化"""
    # 使用测试用的API密钥和URL
    api_key = "ragflow-E3MDgxNWI2MGIwZTExZjBiZjQxNGE1YT"
    base_url = "http://127.0.0.1:7999"
    
    interface = RAGFlowQueryInterface(api_key=api_key, base_url=base_url)
    assert interface.api_key == api_key
    assert interface.base_url == base_url

def test_ragflow_interface_invalid_initialization():
    """测试无效初始化参数的情况"""
    with pytest.raises(ValueError):
        RAGFlowQueryInterface(api_key="", base_url="http://test.example.com")
    
    with pytest.raises(ValueError):
        RAGFlowQueryInterface(api_key="test_api_key", base_url="")

def test_query_real():
    """测试RAGFlow真实查询功能"""
    api_key = "ragflow-E3MDgxNWI2MGIwZTExZjBiZjQxNGE1YT"
    base_url = "http://127.0.0.1:7999"
    
    # 创建真实接口实例
    interface = RAGFlowQueryInterface(api_key=api_key, base_url=base_url)
    
    # 执行实际查询
    query_text = "乡村振兴战略的主要政策有哪些？"
    results = interface.query(query_text)
    
    # 验证返回结果
    assert results is not None
    print(f"查询 '{query_text}' 的结果数量: {len(results)}")
    
    # 打印结果类型和部分内容，以便理解实际返回格式
    print(f"结果类型: {type(results)}")
    
    # 如果结果是列表，尝试打印第一个元素
    if isinstance(results, list) and results:
        first_item = results[0]
        print(f"第一个结果类型: {type(first_item)}")
        
        # 如果第一个结果是字典
        if isinstance(first_item, dict):
            if "content" in first_item:
                print(f"内容: {first_item['content'][:100]}...")
            if "metadata" in first_item:
                print(f"元数据: {first_item['metadata']}")
        # 如果第一个结果是字符串
        elif isinstance(first_item, str):
            print(f"内容: {first_item[:100]}...")
    # 如果结果是字符串
    elif isinstance(results, str):
        print(f"内容: {results[:100]}...")
        
    # 确保至少返回了一些内容
    assert len(results) > 0 