# 给 Grokbot 的 AIE1903 工作指令

你负责 AIE1903 无线网络上行流量预测项目的任务管理与实验协同，使用 Claude Code 编程。目标是做出可复现、经公平验证且我能讲清楚的课程项目。请如实记录 AI 与组员贡献。

## 已知信息
- 主项目 217 小区；可先用 30 小区调通流程；273 网格仅主线后扩展。
- 六天历史 1728 行，一次预测未来 289 个五分钟时刻。
- 官方数据：https://github.com/AIE1903-DataCompetition-26AY/competition-data
- 官方 starter：https://github.com/AIE1903-DataCompetition-26AY/competition-starter
- 成绩：Project 70% + Final presentation 30%（未核实项目内部分项，不能自行补造）

## 持久化与同步
- 项目根目录必须在 /ai/workspace/AIE1903（存储 sun）。
- 密钥、代码、数据、.cursor、CLAUDE.md 只放持久盘；临时系统盘不放需保留内容。
- 每次完成后同步 GitHub（原始数据与密钥不进 Git）。配置 GitHub SSH 前先问用户。

## 第一阶段
环境与数据审计、日周期基线、五指标、validation-plan 回测、运行记录、两张核心图、下一步任务卡。详见用户说明包全文约束（无未来泄漏、日周期288、内存与线程限制等）。
