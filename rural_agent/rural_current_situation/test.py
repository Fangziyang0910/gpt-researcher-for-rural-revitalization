import asyncio
from rural_analysis_agent import RuralAnalysisAgent

async def run_analysis():
    agent = RuralAnalysisAgent()
    config = {
        "village_name": "海南省沙美村",
        "query": "海南省沙美村的乡村发展现状分析",
        "report_format": "word",
        "report_source": "web"
    }
    report_path = await agent.analyze(config)
    print(f"报告已生成: {report_path}")

if __name__ == "__main__":
    asyncio.run(run_analysis())