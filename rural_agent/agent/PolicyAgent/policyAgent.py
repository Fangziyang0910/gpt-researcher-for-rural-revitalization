from gpt_researcher import GPTResearcher
from multi_agents import WriterAgent, EditorAgent, PublisherAgent
from datetime import datetime
import asyncio
from typing import Dict, List, Optional
from langgraph.graph import StateGraph, END
from .utils.views import print_agent_output
from .utils.llms import call_model
from . import ResearchAgent, ReviewerAgent, ReviserAgent, HumanAgent
import json
from ..memory.research import ResearchState
from .utils.utils import sanitize_filename
import os

#调用顺序
# research（生成report）->subtopic_research（生成subtopic：report）->depth_research   researcher部分   生成{draft:research_draft}
# research->initial_research   browser部分   生成{task:***   initial_research:report(research)}
#最终生成文案
#---------------------------------------------------researcher的部分
class PolicyAgent:
    def __init__(self,task:dict,websocket=None, stream_output=None, tone=None, headers=None):
        self.websocket = websocket
        self.stream_output = stream_output
        self.headers = headers or {}
        self.tone = tone
        self.task = task
        self.output_dir = self._create_output_directory()

    def _create_output_directory(self):
        output_dir = "./outputs/" + \
            sanitize_filename(
                f"run_policy_{self.task.get('query')[0:40]}")

        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    async def research(self, query: str, research_report: str = "research_report",
                       parent_query: str = "", verbose=True, source="web", tone=None, headers=None):
        # Initialize the researcher
        researcher = GPTResearcher(query=query, report_type=research_report, parent_query=parent_query,
                                   verbose=verbose, report_source=source, tone=tone, websocket=self.websocket, headers=self.headers)
        # Conduct research on the given query
        await researcher.conduct_research()
        # Write the report
        report = await researcher.write_report()

        return report

    async def run_initial_research(self, research_state: dict):
        task = research_state.get("task")
        query = task.get("query")
        source = task.get("source", "web")

        if self.websocket and self.stream_output:
            await self.stream_output("logs", "initial_research", f"Running initial research on the following query: {query}", self.websocket)
        else:
            print_agent_output(f"Running initial research on the following query: {query}", agent="RESEARCHER")
        result=await self.research(query=query, verbose=task.get("verbose"),
                                                                      source=source, tone=self.tone, headers=self.headers)
        result=result+"""\n\n（政策研究包含三方面，每个方面的具体内容如下：1️⃣ **各级政策（Policies at Different Administrative Levels）**
                    - 国家级政策（National Policies）
                    - 省级政策（Provincial Policies）
                    - 市级政策（City-Level Policies）
                    - 县区级政策（County-Level Policies）
                    - 乡镇政策（Township-Level Policies）
                    - 村级政策（Village Policies）
                    
                    2️⃣ **有力政策（Favorable Policies）**
                    - 主要支持农业、乡村发展的政策
                    - 重点扶持产业政策
                    - 资金支持和补贴政策
                    - 绿色发展与环境保护政策
                    - 其他相关优惠政策

                    3️⃣ **上位规划（Higher-Level Planning）**
                    - 省级规划（Provincial Planning）
                    - 市级规划（City-Level Planning）
                    - 县区级规划（County-Level Planning）
                    - 乡镇规划（Township Planning））"""+\
                    """
                    \n\n
                    [Policies at all levels] refer to policies compiled according to the administrative hierarchy of the country, province, city, county, town, and village; 
                    [upper-level planning] refers to plans compiled according to the administrative hierarchy of province, city, county, and town. Finding the superior planning can help us understand the planning direction of the village and thus follow the planning ideas.
                    """
        return {"task": task, "initial_research":result }


#---------------------------------------------------editor的部分
    async def plan_research(self, research_state: Dict[str, any]) -> Dict[str, any]:
        """
        Plan the research outline based on initial research and task parameters.

        :param research_state: Dictionary containing research state information
        :return: Dictionary with title, date, and planned sections
        """
        initial_research = research_state.get("initial_research")
        task = research_state.get("task")
        include_human_feedback = task.get("include_human_feedback")
        human_feedback = research_state.get("human_feedback")
        max_sections = task.get("max_sections")

        prompt = self._create_planning_prompt(
            initial_research, include_human_feedback, human_feedback, max_sections)

        print_agent_output(
            "Planning an outline layout based on initial research...", agent="EDITOR")
        plan = await call_model(
            prompt=prompt,
            model=task.get("model"),
            response_format="json",
        )
        return {
            "title": plan.get("title"),
            "date": plan.get("date"),
            "sections": plan.get("sections"),
        }

    async def run_parallel_research(self, research_state: Dict[str, any]) -> Dict[str, List[str]]:
        """
        Execute parallel research tasks for each section.

        :param research_state: Dictionary containing research state information
        :return: Dictionary with research results
        """
        agents = self._initialize_agents()
        workflow = self._create_workflow()
        chain = workflow.compile()

        queries = research_state.get("sections")
        title = research_state.get("title")

        #这里是搜索的subtopic
        self._log_parallel_research(queries)

        final_drafts = [
            chain.ainvoke(self._create_task_input(
                research_state, query, title))
            for query in queries
        ]
        research_results = [
            result["draft"] for result in await asyncio.gather(*final_drafts)
        ]

        return {"research_data": research_results}




    def _create_planning_prompt(self, initial_research: str, include_human_feedback: bool,
                                human_feedback: Optional[str], max_sections: int) -> List[Dict[str, str]]:
        """Create the prompt for research planning."""
        return [
            {
                "role": "system",
                "content": "You are a research editor. Your goal is to oversee the research project "
                           "from inception to completion. Your main task is to plan the article section "
                           "layout based on an initial research summary.\n ",
            },
            {
                "role": "user",
                "content": self._format_planning_instructions(initial_research, include_human_feedback,
                                                              human_feedback, max_sections),
            },
        ]




    def _format_planning_instructions(self, initial_research: str, include_human_feedback: bool,
                                      human_feedback: Optional[str], max_sections: int) -> str:
        """Format the instructions for research planning."""
        today = datetime.now().strftime('%d/%m/%Y')
        feedback_instruction = (
            f"Human feedback: {human_feedback}. You must plan the sections based on the human feedback."
            if include_human_feedback and human_feedback and human_feedback != 'no'
            else ''
        )

        return f"""Today's date is {today}
                   Research summary report: '{initial_research}'
                   {feedback_instruction}
                   \nYour task is to generate an outline of sections headers for the research project
                   based on the research summary report above.
                   The section headers are already predefined as follows:
                   1️⃣ **各级政策（Policies at Different Administrative Levels）**
                    - 国家级政策（National Policies）
                    - 省级政策（Provincial Policies）
                    - 市级政策（City-Level Policies）
                    - 县区级政策（County-Level Policies）
                    - 乡镇政策（Township-Level Policies）
                    - 村级政策（Village Policies）
                    
                    2️⃣ **有力政策（Favorable Policies）**
                    - 主要支持农业、乡村发展的政策
                    - 重点扶持产业政策
                    - 资金支持和补贴政策
                    - 绿色发展与环境保护政策
                    - 其他相关优惠政策

                    3️⃣ **上位规划（upper-level Planning）**
                    - 省级规划（Provincial Planning）
                    - 市级规划（City-Level Planning）
                    - 县区级规划（County-Level Planning）
                    - 乡镇规划（Township Planning）
                    
                   You must focus ONLY on related research topics for subheaders and do NOT include introduction, conclusion and references.
                   You must return nothing but a JSON with the fields 'title' (str) and 
                   'sections' with the following structure:
                   '{{title: string research title, date: today's date, 
                   sections: ['section header 1', 'section header 2', 'section header 3' ...]}}'."""


    def _initialize_agents(self) -> Dict[str, any]:
        """Initialize the research, reviewer, and reviser skills."""
        return {
            "reviewer": ReviewerAgent(self.websocket, self.stream_output, self.headers),
            "reviser": ReviserAgent(self.websocket, self.stream_output, self.headers),
            "writer": WriterAgent(self.websocket, self.stream_output, self.headers),
            "editor": EditorAgent(self.websocket, self.stream_output, self.headers),
            "research": ResearchAgent(self.websocket, self.stream_output, self.tone, self.headers),
            "publisher": PublisherAgent(self.output_dir, self.websocket, self.stream_output, self.headers),
            "human": HumanAgent(self.websocket, self.stream_output, self.headers)
        }

    def _create_workflow(self, agents):
        workflow = StateGraph(ResearchState)

        # Add nodes for each agent
        workflow.add_node("browser", self.run_initial_research)
        workflow.add_node("planner", agents["editor"].plan_research)
        workflow.add_node("researcher", agents["editor"].run_parallel_research)
        workflow.add_node("writer", agents["writer"].run)
        workflow.add_node("publisher", agents["publisher"].run)
        workflow.add_node("human", agents["human"].review_plan)

        # Add edges
        self._add_workflow_edges(workflow)

        return workflow

    def _add_workflow_edges(self, workflow):
        workflow.add_edge('browser', 'planner')
        workflow.add_edge('planner', 'human')
        workflow.add_edge('researcher', 'writer')
        workflow.add_edge('writer', 'publisher')
        workflow.set_entry_point("browser")
        workflow.add_edge('publisher', END)

        # Add human in the loop
        workflow.add_conditional_edges(
            'human',
            lambda review: "accept" if review['human_feedback'] is None else "revise",
            {"accept": "researcher", "revise": "planner"}
        )

    def _log_parallel_research(self, queries: List[str]) -> None:
        """Log the start of parallel research tasks."""
        if self.websocket and self.stream_output:
            asyncio.create_task(self.stream_output(
                "logs",
                "parallel_research",
                f"Running parallel research for the following queries: {queries}",
                self.websocket,
            ))
        else:
            print_agent_output(
                f"Running the following  research tasks in parallel: {queries}...",
                agent="EDITOR",
            )

    def _create_task_input(self, research_state: Dict[str, any], query: str, title: str) -> Dict[str, any]:
        """Create the input for a single research task."""
        return {
            "task": research_state.get("task"),
            "topic": query,
            "title": title,
            "headers": self.headers,
        }


#---------------------------------------运行部分
    async def run(self):
        agents = self._initialize_agents()
        research_team=self._create_workflow(agents)
        chain = research_team.compile()
        result = await chain.ainvoke({"task": self.task})
        return result


#报告需要去掉conclusion部分
#需要添加review revise部分


""" #-----------------------------------------新建test.py测试
import asyncio
import json
from dotenv import load_dotenv
from multi_agents.agents.policy import PolicyAgent
import os
# Run with LangSmith if API key is set
if os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
load_dotenv()

def open_task():
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the absolute path to task.json
        task_json_path = os.path.join(current_dir, 'task.json')

        with open(task_json_path, 'r',encoding="utf-8") as f:
                task = json.load(f)

        if not task:
                raise Exception(
                        "No task found. Please ensure a valid task.json file is present in the multi_agents directory and contains the necessary task information.")

        # Override model with STRATEGIC_LLM if defined in environment
        strategic_llm = os.environ.get("STRATEGIC_LLM")
        if strategic_llm and ":" in strategic_llm:
                # Extract the model name (part after the colon)
                model_name = strategic_llm.split(":")[-1]
                task["model"] = model_name
        elif strategic_llm:
                task["model"] = model_name

        return task

async def main():
        task = open_task()
        policy_agent = PolicyAgent(task)
        research_report = await policy_agent.run()
        print(research_report)
        return research_report

if __name__ == "__main__":
    asyncio.run(main()) """


