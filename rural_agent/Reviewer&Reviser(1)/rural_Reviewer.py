from multi_agents.agents.utils.views import print_agent_output
from multi_agents.agents.utils.llms import call_model
from draft import rural_DraftState
from typing import Dict, Any
import asyncio

from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv

# 定义审稿提示模板
TEMPLATE = """你是一位专业的乡村规划报告审稿人。\
你的任务是根据给定的审稿标准审查报告初稿，并提供反馈。\
"""

class ReviewerAgent:
    def __init__(self, draft_state: rural_DraftState):
        self.draft_state = draft_state

    async def review_draft(self,draft_state) -> rural_DraftState:
        """
        审查报告初稿
        :return: 更新后的 draft_state，包含审查结果
        """
        print("审查报告...")
        # 从 draft_state 中提取参数
        draft_versions = draft_state["draft"]
        guidelines = draft_state["guidelines"]
        revision_notes = draft_state["revision_notes"]

        # 检查必要的参数是否存在
        if not draft_versions:
            raise ValueError("Draft content is missing in draft_state")
        if guidelines is None:
            raise ValueError("Guidelines are missing in draft_state")

        # 获取最新版本的报告内容
        latest_draft = draft_versions[-1]["content"]

        # 将审稿标准转换为字符串
        guidelines_str = "- ".join(guidelines)

        # 构造审稿提示
        review_prompt = f"""你被分配了审查一篇关于乡村规划的报告初稿的任务，审稿标准如下：
{guidelines_str}

请根据这些标准审查以下报告初稿，并提供反馈：
{latest_draft}

如果报告符合所有标准，请返回 "通过报告"。
如果报告不符合某些标准，请提供详细的修改意见。
"""

        if revision_notes:
            review_prompt += f"""
修订者已经根据你之前的审稿意见对草稿进行了修订，以下是反馈内容：
{revision_notes}

如果文章存在关键问题，请提供进一步的反馈，因为修订者已经根据你之前的反馈进行了修改。
如果你认为文章足够好或者只需要进行非关键性的修订，请返回 None。
"""

        prompt = [
            {"role": "system", "content": TEMPLATE},
            {"role": "user", "content": review_prompt},
        ]

        model = ChatOpenAI(model=draft_state["model"],
                           api_key=draft_state["api_key"],
                           base_url=draft_state["base_url"])
        response = await model.ainvoke(prompt)
        # print(type(response))
        # 解析模型返回的结果
        if "通过报告" in response.content:
            draft_state["review"] = "通过"
            draft_state["revision_notes"] = ""
        else:
            draft_state["review"] = "未通过"
            draft_state["revision_notes"] = response


        print(draft_state["review"])
        return draft_state

    async def run(self) -> rural_DraftState:
        """
        运行审稿流程
        :return: 更新后的 draft_state，包含审查结果
        """
        return await self.review_draft(self.draft_state)

# 测试 ReviewerAgent
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
        review="",
        revision_notes="",
        guidelines=guidelines,
        village_name="海南省沙美村",
        query="海南省沙美村的乡村发展现状分析",
        model="glm-4-flash",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    # 初始化审稿代理
    reviewer_agent = ReviewerAgent(rural_draft_state)
    # 运行审稿流程
    updated_draft_state = await reviewer_agent.run()
    # 打印审稿结果
    print(updated_draft_state["review"])
    print(updated_draft_state["revision_notes"].content)

# 运行测试
if __name__ == "__main__":
    asyncio.run(main())