from draft import rural_DraftState
from typing import Dict, List, Any
import asyncio

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv



# 定义 RuralAnalysisAgent
class RuralAnalysisAgent:
    def __init__(self,draft_state: rural_DraftState):
        # print(a)
        pass

    async def generate_analysis(self,draft_state) -> Dict[str, str]:
        # 构造提示
        prompt = f"""
        请根据以下查询生成关于 {draft_state['village_name']} 的乡村发展现状分析：
        {draft_state['query']}
        """
        # 调用模型生成报告
        model = ChatOpenAI(model_name=draft_state["model"], api_key=draft_state["api_key"], base_url=draft_state["base_url"])
        response = await model.ainvoke(prompt)
        # 获取生成的报告内容
        if isinstance(response, AIMessage):
            analysis_content = response.content  # 假设 AIMessage 对象有一个 content 属性
        else:
            raise ValueError(f"Unexpected response type: {type(response)}")
        # 更新 draft_state
        draft_state["draft"].append({
            "version": len(draft_state["draft"]) + 1,  # 版本号
            "content": analysis_content  # 报告内容
        })
        return draft_state


# 测试 RuralAnalysisAgent
async def main():
    # 创建 rural_DraftState 实例
    rural_draft_state = rural_DraftState(
        draft=[],  # 初始为空列表
        review="",
        revision_notes="",
        village_name="海南省沙美村",
        query="海南省沙美村的乡村发展现状分析",
        model="glm-4-flash",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    # 初始化分析代理
    analysis_agent = RuralAnalysisAgent()
    # 生成分析报告
    updated_draft_state = await analysis_agent.generate_analysis(rural_DraftState)
    # 打印生成的分析内容
    for version in updated_draft_state["draft"]:
        print(f"Version {version['version']}:")
        print(version["content"])
        print("\n")


# 运行测试
if __name__ == "__main__":
    asyncio.run(main())