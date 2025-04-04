from rural_reviewer import ReviewerAgent
import asyncio

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

# 修订说明（可选）
revision_notes = """
根据之前的审稿意见，已经补充了更多关于环境保护的具体措施。
"""

# 将所有参数统一封装到 draft_state 中
draft_state = {
    "draft": draft,
    "guidelines": guidelines,
    "revision_notes": revision_notes,
    "model_name":"deepseek-chat"
}

# 创建 ReviewerAgent 实例
agent = ReviewerAgent()

# 运行审稿流程
review_result = asyncio.run(agent.run(draft_state))

# 输出审稿结果
if review_result["passed"]:
    print("报告通过审稿。")
else:
    print("报告未通过审稿，需要修改。修改意见如下：")
    print(review_result["feedback"])