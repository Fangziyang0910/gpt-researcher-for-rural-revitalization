import os
import asyncio
from typing import TypedDict, List, Dict, Any, Callable
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from multi_agents.agents.utils.views import print_agent_output
from multi_agents.agents.utils.llms import call_model
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from draft import rural_DraftState
from rural_AnalysisAgent import RuralAnalysisAgent
from rural_Reviewer import ReviewerAgent
from rural_Reviser import ReviserAgent

# 加载环境变量
load_dotenv()


# 定义工作流管理器
class RuralReportWorkflow:
    def __init__(self, draft_state: rural_DraftState):
        self.draft_state = draft_state

    def _initialize_agents(self):
        """
        初始化各个子代理。
        每个子代理负责任务的不同阶段。

        返回值:
            dict: 包含所有初始化子代理的字典。
        """
        # 初始化并返回一个包含所有子代理的字典
        return {
            "analyser": RuralAnalysisAgent(self.draft_state),  # 撰写内容的代理
            "reviewer": ReviewerAgent(self.draft_state),  # 审稿人代理
            "reviser": ReviserAgent(self.draft_state),  # 修订代理
        }

    def _create_workflow(self, agents: Dict[str, Callable[[rural_DraftState], rural_DraftState]]):
            workflow = StateGraph(rural_DraftState)
            workflow.add_node("analysis", agents["analyser"].generate_analysis)
            workflow.add_node("review_draft", agents["reviewer"].review_draft)
            workflow.add_node("revise_draft", agents["reviser"].revise_draft)

            workflow.add_edge("analysis", "review_draft")
            workflow.add_edge("revise_draft", "review_draft")  # 修订后重新审查

            # 添加条件边
            workflow.add_conditional_edges(
                "review_draft",
                lambda result: "pass" if result["review"]=="通过" else "fail",
                {"pass": END, "fail": "revise_draft"}
            )

            workflow.set_entry_point("analysis")
            # workflow.set_finish_point(END)
            return workflow

    async def run(self):
        agents = self._initialize_agents()
        workflow = self._create_workflow(agents)
        app = workflow.compile()
        result = await app.ainvoke(self.draft_state)
        print(result)

# 测试工作流
async def main():
    rural_draft_state = rural_DraftState(
        draft=[],
        village_name="海南省沙美村",
        guidelines=[
            "报告语言是否优美流畅，符合学术规范",
            "报告是否使用英语进行撰写"
            # "报告是否包含必要的图表和数据支持",
        ],
        review="",
        revision_notes=[],
        query="海南省沙美村的乡村发展现状分析",
        model="gpt-4o",
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL")
    )

    workflow_manager = RuralReportWorkflow(rural_draft_state)
    await workflow_manager.run()

# 运行测试
if __name__ == "__main__":
    asyncio.run(main())