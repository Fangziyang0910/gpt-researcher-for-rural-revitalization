from multi_agents.agents.utils.views import print_agent_output
from multi_agents.agents.utils.llms import call_model

TEMPLATE = """你是一位专业的乡村规划报告审稿人。\
你的任务是根据给定的审稿标准审查报告初稿，并提供反馈。\
"""

class ReviewerAgent:
    def __init__(self):
        pass

    async def review_draft(self, draft_state: dict):
        """
        审查报告初稿
        :param draft_state: 包含报告初稿和审稿标准的字典
        :return: 审查结果，包括是否通过以及修改意见（如果需要）
        """
        # 从 draft_state 中提取参数
        draft = draft_state.get("draft")
        guidelines = draft_state.get("guidelines")
        revision_notes = draft_state.get("revision_notes")

        # 检查必要的参数是否存在
        if draft is None:
            raise ValueError("Draft is missing in draft_state")
        if guidelines is None:
            raise ValueError("Guidelines are missing in draft_state")

        # 将审稿标准转换为字符串
        guidelines_str = "- ".join(guideline for guideline in guidelines)

        # 构造审稿提示
        review_prompt = f"""你被分配了审查一篇关于乡村规划的报告初稿的任务，审稿标准如下：
{guidelines_str}

请根据这些标准审查以下报告初稿，并提供反馈：
{draft}

如果报告符合所有标准，请返回 "通过"。
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

        # 调用模型进行审稿
        response = await call_model(prompt,model=draft_state.get("model_name"))

        # 解析模型返回的结果
        if "通过" in response:
            return {"passed": True, "feedback": None}
        else:
            return {"passed": False, "feedback": response}

    async def run(self, draft_state: dict):
        """
        运行审稿流程
        :param draft_state: 包含报告初稿和审稿标准的字典
        :return: 审查结果
        """
        review_result = await self.review_draft(draft_state)
        return review_result
