from typing import TypedDict, List, Dict, Any


# 定义 rural_DraftState
class rural_DraftState(TypedDict):
    draft: List[Dict[str, Any]]  # 每个版本的内容存储为字典
    village_name: str
    guidelines: List[str]  
    review: str
    revision_notes: List[str]
    query: str
    model: str
    api_key: str
    base_url: str
