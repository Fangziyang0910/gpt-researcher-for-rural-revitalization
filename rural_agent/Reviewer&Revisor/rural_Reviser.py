from multi_agents.agents.utils.llms import call_model

import asyncio

# 修订模板
TEMPLATE = """你是一位专业的报告修订者。你的任务是根据审稿人的反馈修订报告初稿。"""

class ReviserAgent:
    def __init__(self, draft_state: dict):
        # self.draft_state = draft_state
        pass
    async def revise_draft(self,draft_state):
        """
        根据审稿反馈修订报告初稿
        :return: 更新后的 draft_state，包含修订后的报告和修订说明
        """
        print(f"修订报告...\n报告意见：{draft_state['revision_notes']}")

        task = draft_state.get("task")
        draft_versions = draft_state["draft"]
        review_feedback = draft_state["revision_notes"]
        prompt = [
            {
                "role": "system",
                "content": "You are an expert writer. Your goal is to revise drafts based on reviewer notes.",
            },
            {
                "role": "user",
                "content": f"""Draft:\n{draft_versions}" + "Reviewer's notes:\n{review_feedback}\n\n
You have been tasked by your reviewer with revising the following draft, which was written by a non-expert.
If you decide to follow the reviewer's notes, please write a new draft and make sure to address all of the points they raised.
Please keep all other aspects of the draft the same.
""",
            },
        ]
        response = await call_model(
            prompt,
            model=task.get("model"),
            response_format="json",
        )
        return response
    
    async def run(self, draft_state: dict):
        """
        运行修订器
        :param draft_state:
        :return:
        """
        print(f"修订报告...\n报告意见：{draft_state['revision_notes']}")
        revision = await self.revise_draft(draft_state)
        return revision
    
async def main():
    # 测试修订器
    draft_state = {
        "draft": "This is a sample draft report.",
        "revision_notes": "Please improve the clarity and add more details.",
        "task": {
            "model": "gpt-4o",
            "verbose": True
        }
    }
    # 初始化修订代理
    reviser_agent = ReviserAgent(draft_state)
    # 运行修订流程
    updated_draft_state = await reviser_agent.run(draft_state=draft_state)
    # 打印修订结果
    for version in updated_draft_state["draft"]:
        print(f"Version {version['version']}:")
        print(version["content"])
        print("\n")
    # print(updated_draft_state["revision_notes"])

# 运行测试
if __name__ == "__main__":
    asyncio.run(main())