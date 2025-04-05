from multi_agents.agents.utils.views import print_agent_output
from multi_agents.agents.utils.llms import call_model
from draft import rural_DraftState
from typing import Dict, Any
import asyncio

from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

# 修订模板
TEMPLATE = """你是一位专业的报告修订者。你的任务是根据审稿人的反馈修订报告初稿。"""

class ReviserAgent:
    def __init__(self, draft_state: rural_DraftState):
        # self.draft_state = draft_state
        pass

    async def revise_draft(self,draft_state) -> rural_DraftState:
        """
        根据审稿反馈修订报告初稿
        :return: 更新后的 draft_state，包含修订后的报告和修订说明
        """
        print(f"修订报告...\n报告意见：{draft_state['revision_notes']}")
        # 从 draft_state 中提取参数
        draft_versions = draft_state["draft"]
        review_feedback = draft_state["revision_notes"]
        model_name = draft_state.get("model")
        api_key = draft_state.get("api_key")
        base_url = draft_state.get("base_url")

        # 检查必要的参数是否存在
        if not draft_versions:
            raise ValueError("Draft content is missing in draft_state")
        if review_feedback is None:
            raise ValueError("Review feedback is missing in draft_state")

        # 获取最新版本的报告内容
        latest_draft = draft_versions[-1]["content"]

        # 构造修订提示
        prompt = [
            {"role": "system", "content": TEMPLATE},
            {
                "role": "user",
                "content": f"""报告初稿：
                {latest_draft}

                审稿人反馈：
                {review_feedback}

                请根据审稿人的反馈对报告初稿进行修订，并确保涵盖所有提出的要点。其他方面保持不变。
                """
            },
        ]

        # 调用模型进行修订
        model = ChatOpenAI(model=model_name, api_key=api_key, base_url=base_url)
        response = await model.ainvoke(prompt)

        # 更新 draft_state
        new_version = {
            "version": len(draft_versions) + 1,
            "content": response
        }
        draft_state["draft"].append(new_version)
        draft_state["revision_notes"] = "根据审稿反馈进行了修订。"


        return draft_state

    async def run(self,draft_state) -> rural_DraftState:
        """
        运行修订流程
        :return: 更新后的 draft_state
        """
        print("根据审稿反馈修订报告...")
        return await self.revise_draft(draft_state)

# 测试 ReviserAgent
async def main():
    load_dotenv()  # 加载环境变量
    # 示例报告初稿
    draft = """
    # 乡村规划报告

    ## 引言
    本报告旨在探讨小村庄的未来发展，重点关注基础设施建设、环境保护和经济发展。

    ## 基础设施建设
    计划在未来五年内修建新的道路和桥梁，改善交通状况。

    ## 环境保护
    将设立专门的环保区域，保护当地的自然生态。

    ## 经济发展
    计划引入新的农业技术和旅游项目，促进经济增长。

    ## 结论
    通过这些措施，小村庄将实现可持续发展。
    """

    # 审稿标准
    guidelines = [
        "报告是否涵盖了乡村规划的所有关键领域（基础设施、环境保护、经济发展等）",
        "报告是否提出了具体的实施措施和时间表",
        "报告是否考虑了可持续发展的要求",
        "报告是否具有逻辑性和连贯性"
    ]

    # 创建 rural_DraftState 实例
    rural_draft_state = rural_DraftState(
        draft=[{"version": 1, "content": draft}],  # 初始化为一个包含一个版本的列表
        review="未通过。需要加强环境保护部分的内容。",
        revision_notes="",
        guidelines=guidelines,
        village_name="海南省沙美村",
        query="海南省沙美村的乡村发展现状分析",
        model="glm-4-flash",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    # 初始化修订代理
    reviser_agent = ReviserAgent(rural_draft_state)
    # 运行修订流程
    updated_draft_state = await reviser_agent.run(rural_draft_state)
    # 打印修订结果
    for version in updated_draft_state["draft"]:
        print(f"Version {version['version']}:")
        print(version["content"])
        print("\n")
    # print(updated_draft_state["revision_notes"])

# 运行测试
if __name__ == "__main__":
    asyncio.run(main())