import pytest
from rural_agent.config.rural_config import RuralConfig

def test_config_initialization():
    """测试配置类的初始化"""
    config = RuralConfig()
    assert config is not None

def test_llm_config():
    """测试LLM配置的获取"""
    config = RuralConfig()
    # 测试获取不同角色的LLM配置
    for role in ["strategic", "fast", "smart"]:
        llm_config = config.get_llm_config(role)
        assert isinstance(llm_config, dict)
        assert "provider" in llm_config
        assert "model" in llm_config

def test_ragflow_config():
    """测试RAGFlow配置"""
    config = RuralConfig()
    assert hasattr(config, 'ragflow_api_key')
    assert hasattr(config, 'ragflow_base_url')
    assert hasattr(config, 'ragflow_enabled')

def test_config_details():
    """测试并打印配置详情"""
    config = RuralConfig()
    
    # 将配置转换为字典并打印
    config_dict = config.to_dict()
    print("\n配置详情:")
    for key, value in config_dict.items():
        # 对敏感信息进行模糊处理
        if 'api_key' in key and value and isinstance(value, str):
            masked_value = value[:5] + "..." + (value[-3:] if len(value) > 8 else "")
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    
    # LLM配置详情
    print("\nLLM配置:")
    for role in ["strategic", "fast", "smart"]:
        config_dict = config.get_llm_config(role)
        print(f"  {role}: {config_dict}")
    
    # 确认配置已正确加载
    assert config.ragflow_base_url is not None 