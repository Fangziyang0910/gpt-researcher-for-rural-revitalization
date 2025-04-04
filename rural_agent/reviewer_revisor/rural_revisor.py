from multi_agents.agents.utils.llms import call_model

import json
import asyncio

# 示例修订说明的 JSON 格式
sample_revision_notes = """
{
  "draft": { 
    "draft_title": "修订后的报告标题"
  },
  "revision_notes": "根据审稿人反馈对报告所做的修改说明"
}
"""

class ReviserAgent:
    def __init__(self):
        pass

    async def revise_draft(self, draft_state: dict):
        """
        根据审稿反馈修订报告初稿
        :param draft_state: 包含报告初稿和审稿反馈的字典
        :return: 修订后的报告和修订说明
        """
        # 从 draft_state 中提取参数
        draft = draft_state.get("draft")
        review_feedback = draft_state.get("review_feedback")
        task = draft_state.get("task")

        # 检查必要的参数是否存在
        if draft is None:
            raise ValueError("Draft is missing in draft_state")
        if review_feedback is None:
            raise ValueError("Review feedback is missing in draft_state")
        if task is None:
            raise ValueError("Task is missing in draft_state")

        # 构造修订提示
        prompt = [
            {
                "role": "system",
                "content": "你是一位专业的报告修订者。你的任务是根据审稿人的反馈修订报告初稿。",
            },
            {
                "role": "user",
                "content": f"""报告初稿：
{draft}

审稿人反馈：
{review_feedback}

请根据审稿人的反馈对报告初稿进行修订，并确保涵盖所有提出的要点。其他方面保持不变。
你必须返回以下格式的 JSON：
{sample_revision_notes}
""",
            },
        ]

        # 调用模型进行修订
        response = await call_model(prompt, model=task.get("model"), response_format="json")

        # # 解析模型返回的结果
        # try:
        #     revision = json.loads(response)
        # except json.JSONDecodeError:
        #     raise ValueError("Model response is not a valid JSON")

        return response

    async def run(self, draft_state: dict):
        """
        运行修订流程
        :param draft_state: 包含报告初稿和审稿反馈的字典
        :return: 修订后的报告和修订说明
        """
        print("根据审稿反馈修订报告...")
        revision = await self.revise_draft(draft_state)

        if draft_state.get("task").get("verbose"):
            print(f"修订说明：{revision.get('revision_notes')}")

        return {
            "draft": revision.get("draft"),
            "revision_notes": revision.get("revision_notes"),
        }
    
if __name__=="__main__":
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

    # 审稿反馈
    review_feedback = "报告内容基本符合要求，但建议在第三部分补充更多关于可持续发展的具体措施。"

    # 将所有参数统一封装到 draft_state 中
    draft_state = {
        "draft": draft,
        "guidelines": guidelines,
        "review_feedback": review_feedback,
        "task": {
            "model": "deepseek-chat",
            "verbose": True
        }
    }

    # 创建 ReviserAgent 实例
    reviser_agent = ReviserAgent()

    # 运行修订流程
    revision_result = asyncio.run(reviser_agent.run(draft_state))

    # 输出修订结果
    print("修订后的报告：")
    print(revision_result["draft"])
    print("修订说明：")
    print(revision_result["revision_notes"])