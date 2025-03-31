import os
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# 导入基础LLM支持的提供商列表
from gpt_researcher.llm_provider.generic.base import _SUPPORTED_PROVIDERS as LLM_SUPPORTED_PROVIDERS


class RuralConfig:
    """乡村振兴方案生成器的配置管理类"""

    def __init__(self):
        """
        初始化配置类
        """
        # 先加载环境变量
        load_dotenv()
        
        # LLM配置
        self._init_llm_config()
        
        # RAGFlow配置
        self._init_ragflow_config()
        
        # Tavily配置
        self._init_tavily_config()
        
        # 嵌入模型配置
        self._init_embedding_config()

    def _init_llm_config(self):
        """初始化与LLM相关的配置"""
        # 解析三种角色的LLM配置
        self.strategic_llm_provider, self.strategic_llm_model = self.parse_llm(os.getenv("STRATEGIC_LLM"))
        self.fast_llm_provider, self.fast_llm_model = self.parse_llm(os.getenv("FAST_LLM"))
        self.smart_llm_provider, self.smart_llm_model = self.parse_llm(os.getenv("SMART_LLM"))
        
        # 收集所有API密钥
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "dashscope": os.getenv("DASHSCOPE_API_KEY"),
        }
        
        # 其他LLM相关配置
        self.openai_base_url = os.getenv("OPENAI_BASE_URL")

    def _init_ragflow_config(self):
        """初始化RAGFlow相关配置"""
        self.ragflow_api_key = os.getenv("RAGFLOW_API_KEY")
        self.ragflow_base_url = os.getenv("RAGFLOW_BASE_URL", "http://127.0.0.1:7999")

    def _init_tavily_config(self):
        """初始化Tavily搜索相关配置"""
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")

    def _init_embedding_config(self):
        """初始化嵌入模型相关配置"""
        embedding_str = os.getenv("EMBEDDING")
        if embedding_str and ":" in embedding_str:
            self.embedding_provider, self.embedding_model = embedding_str.split(":", 1)
        else:
            raise ValueError("必须通过 EMBEDDING 环境变量指定嵌入模型,格式为 'provider:model'")

    @staticmethod
    def parse_llm(llm_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """解析LLM字符串为提供商和模型名"""
        if not llm_str:
            return None, None
            
        try:
            if ":" in llm_str:
                provider, model = llm_str.split(":", 1)
                provider = provider.lower()
                if provider not in LLM_SUPPORTED_PROVIDERS:
                    print(f"警告：不支持的LLM提供商 '{provider}'。支持的提供商有: {', '.join(LLM_SUPPORTED_PROVIDERS)}")
                return provider, model
            else:
                # 如果只提供了模型名，默认使用OpenAI
                return "openai", llm_str
        except Exception as e:
            print(f"解析LLM配置 '{llm_str}' 时出错: {e}")
            return None, None
            
    def get_llm_config(self, role: str) -> Dict[str, Any]:
        """
        获取特定角色LLM的配置信息
        
        Args:
            role: LLM角色，可以是 'strategic', 'fast' 或 'smart'
            
        Returns:
            包含provider和model信息的字典
        """
        if role not in ["strategic", "fast", "smart"]:
            raise ValueError(f"不支持的LLM角色: {role}。支持的角色有: strategic, fast, smart")
            
        provider = getattr(self, f"{role}_llm_provider")
        model = getattr(self, f"{role}_llm_model")
        
        return {
            "provider": provider,
            "model": model
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置导出为字典"""
        result = {}
        for key, value in self.__dict__.items():
            # 过滤掉私有属性
            if not key.startswith('_'):
                result[key] = value
        return result 