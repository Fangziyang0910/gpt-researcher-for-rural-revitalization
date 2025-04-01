import argparse
import asyncio
import json
import os
from rural_analysis_agent import RuralAnalysisAgent

async def main():
    # 设置默认配置文件路径
    default_config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "task.json"
    )
    
    parser = argparse.ArgumentParser(description="乡村现状分析智能体")
    
    # 配置文件参数
    parser.add_argument("--config", "-c", type=str, 
                      default=default_config_path,
                      help=f"JSON格式配置文件路径 (默认: {default_config_path})")
    
    # 命令行覆盖参数
    parser.add_argument("--village", "-v", type=str, help="乡村名称")
    parser.add_argument("--query", "-q", type=str, help="具体查询内容")
    parser.add_argument("--source", "-s", choices=["web", "docs", "hybrid"], 
                       help="数据源类型: web(网络), docs(文档), hybrid(混合)")
    parser.add_argument("--format", "-f", choices=["markdown", "docx", "pdf"], 
                       help="输出格式")
    parser.add_argument("--output", "-o", type=str, help="输出目录路径")
    parser.add_argument("--urls", "-u", type=str, nargs="*", help="特定网页URL列表")
    parser.add_argument("--docs", "-d", type=str, nargs="*", help="本地文档路径列表")
    
    args = parser.parse_args()
    
    # 初始化智能体
    agent = RuralAnalysisAgent()
    
    # 加载配置文件
    config_path = args.config
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                query_config = json.load(f)
            print(f"已加载配置文件: {config_path}")
        except Exception as e:
            print(f"配置文件加载错误: {e}")
            return
    else:
        print(f"配置文件不存在: {config_path}")
        return
    
    # 命令行参数覆盖配置文件
    if args.village:
        query_config["village_name"] = args.village
    if args.query:
        query_config["query"] = args.query
    if args.source:
        query_config["report_source"] = args.source
    if args.format:
        query_config["report_format"] = args.format
    if args.output:
        query_config["output_path"] = args.output
    if args.urls:
        query_config["source_urls"] = args.urls
    if args.docs:
        query_config["document_urls"] = args.docs
    
    # 检查必要参数
    if "village_name" not in query_config or not query_config["village_name"]:
        print("错误: 配置中未指定村庄名称")
        return
    
    # 构建查询内容（如果未指定）
    if "query" not in query_config or not query_config["query"]:
        query_config["query"] = f"{query_config['village_name']}乡村现状分析"
    
    # 确保其他参数存在默认值
    query_config.setdefault("report_source", "web")
    query_config.setdefault("report_format", "markdown")
    query_config.setdefault("source_urls", [])
    query_config.setdefault("document_urls", [])
    query_config.setdefault("complement_source_urls", True)
    
    # 打印分析参数
    print(f"开始分析村庄: {query_config['village_name']}")
    print(f"分析查询: {query_config['query']}")
    print(f"数据源: {query_config['report_source']}")
    print(f"输出格式: {query_config['report_format']}")
    
    # 执行分析
    try:
        result_path = await agent.analyze(query_config)
        print(f"分析报告已生成: {result_path}")
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())