# 来源与未决问题

## 1. 已核实的来源

| 来源 | 版本 | 用途 |
|---|---|---|
| 官方数据仓库 <https://github.com/AIE1903-DataCompetition-26AY/competition-data> | 提交 `49822d82552c980bb83eb445548268f3565882ef`（2026-09-20，公开） | 原始数据、PDF 说明；本地 13 个文件已与之逐字节核对 |
| 官方 starter <https://github.com/AIE1903-DataCompetition-26AY/competition-starter> | 提交 `7a73b32ed3a4a0fcb8f0de50e2552959a999c699`（2026-09-13） | 私有仓库、PR 协作、Python 3.11+、清除 notebook 输出等课程要求 |
| `data_description_for_cell_217.pdf` | blob `64b031f8` | cell_217 的数据合同与指标 |
| `data_description_for_cell_grid.pdf` | blob `8df5a693` | cell_30 与 grid_273 的数据合同与指标 |
| 交接文档 `docs/references/handoff-20261026/` | 2026-10-26 | 本轮的任务要求；课程讲义要点的转述 |
| Cursor 规则文档 <https://cursor.com/docs/rules> | 2026-10-26 查阅 | `.mdc` frontmatter；`@文件` 引用不会内联；会自动读取 AGENTS.md |
| 服务器实测（审计 A-20261026-server） | 2026-10-26 | 平台、资源、存储、网络、软件栈、训练冒烟；手册见 docs/runbooks/environment.md 和 docs/runbooks/training.md |
| Claude Code memory 文档 <https://code.claude.com/docs/en/memory> | 2026-10-26 查阅 | `@` 导入（最多 4 层，代码块和反引号内不生效）；同时存在 CLAUDE.md 和 AGENTS.md 时只读 CLAUDE.md；`.claude/rules` 只读取 `paths` 字段；可用 `/context` 验证加载情况 |

## 2. 未决问题

| # | 问题 | 影响 | 谁来决定或补充 | 状态 |
|---|---|---|---|---|
| Q1 | 项目内的分项权重、名次换分、提交网址、截止时间、提交次数、取最好还是最后一次、展示时长、个人贡献的评分方式 | 提交策略与投入分配 | 课程方（BB 通知） | 未知；不得自行补造 |
| Q2 | 官方评分代码中 Masked MAPE 的分母（217PDF 写 n，CGPDF 写 n′） | 指标口径 | 课程方 | 暂按 provisional-v1（ADR-0003） |
| Q3 | GitHub 仓库目前是**公开**的，而课程要求每组一个私有仓库，并给课程人员访问权限 | 合规；他组可能看到代码 | 学生（GitHub → Settings → Change visibility） | 待处理 |
| Q4 | cell_30 和 grid_273 的 sample 第 289 行疑似含测试期真值（ADR-0005） | 竞赛公平性 | 学生决定是否反馈给课程方 | 待决定；本项目已禁止读取 sample 数值 |
| Q5 | Claude Code 与 Grokbot 的运行模式：box 克隆加远程执行，还是在学校环境直接运行（environment.md §8） | 指令能否加载；是否只有单一工作树 | 学生 | 待决定；推荐模式 B |
| Q6 | 组员名单、GitHub 用户名与分工 | 贡献记录；仓库权限 | 学生 | README 的"团队"一节待填 |
| Q7 | 镜像名是 `jr1903:0.0.1` 还是 `jr/jr1903`（旧文档写法不一致） | 环境重建 | 学生在平台上确认 | 待确认 |
| Q9 | 平台的计费方式、机时上限、GPU 是否独占、空闲时是否自动回收（容器内无法确认） | 长任务规划、释放时机 | 学生查看平台页面或课程通知 | 待确认 |
| Q10 | 是否把 `/ai/workspace/.ssh/config` 的 `HostName` 改为 FQDN（`github.com.`，配合 `HostKeyAlias github.com`），以规避 DNS 偶发失败 | 推送稳定性 | 学生授权（项目外文件） | 待决定；目前用重试应对 |

## 3. 已关闭的问题

| 问题 | 结论 | 证据 |
|---|---|---|
| Q8 项目外的暂存件（`_gh_AIE1903/`、`_merge_stage/`、两个 tgz） | 已核实被 Git 历史完全覆盖；2026-10-26 经学生授权删除 | worklog 2026-10-26；任务卡 T-20261026-01 |
| `.cursorignore` 无法由代理直接写入 | Cursor 的权限配置禁止代理写这个文件；经学生授权，改由终端创建，语义已在临时仓库中测试 | 任务卡 T-20261026-01 |
| 数据集是否齐全 | 三个数据集共 13 个官方文件齐全，并与官方提交逐字节一致 | A-20261026-framework |
| GitHub SSH 密钥是否已注册 | 已注册，可以 yixiangsunLeo 身份认证 | 2026-10-26 执行 `ssh -T git@github.com` |
| `data_description_for_cell_217.pdf.fixed` 是什么 | 与原 PDF 的 sha256 相同，是冗余副本，已删除 | `sha256sum` 比对 |
| `cell_217_data.tgz` 是什么 | 内容与 `data/raw/cell_217` 完全相同，已删除（它曾出现在历史提交 80122a8 中） | 逐个文件比对 sha256 |
