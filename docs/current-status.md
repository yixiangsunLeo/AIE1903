# 当前状态

这是项目状态的单一事实来源，每个任务收尾时更新。

更新：2026-10-26 · T-20261026-01 · cursor/claude-opus-5.5

## 一句话

框架 v0.2.0 已搭好，还没有功能代码，也没有训练。下一步是 roadmap 的 **M1 数据层**。

## 赛道、数据与协议

- **赛道**：主线 cell_217；演练 cell_30；扩展 grid_273（主线完成之后）。
- **数据**：三个数据集共 13 个官方文件齐全，与官方提交 `49822d8` 逐字节一致；校验文件是 `data/checksums.sha256`；审计见 `reports/audit/A-20261026-framework/`。
- **验证协议**：expanding_289_v1（ADR-0002，暂行采用，待学生复核）。heldout 为 **untouched**。
- **指标口径**：provisional-v1（ADR-0003，暂行采用，待学生复核）。
- **数据使用规则**：一个运行只用一个数据集；任何 sample 数值都不得读取（ADR-0005）。

## 环境

- 学校环境的容器配额为 24 核、32 GiB、一张 RTX 5090；Python 3.12.3；项目 `.venv` 已建好（system-site-packages，pytest 9.1.1，ruff 0.17.2）。
- Git hooks 已启用（`core.hooksPath=.githooks`），提交模板为 `.gitmessage`。

## 已验证的命令

```bash
cd /ai/workspace/AIE1903
(cd data && sha256sum -c checksums.sha256)                       # 13/13 OK
.venv/bin/python -m pytest                                       # 19 passed
.venv/bin/ruff check . && .venv/bin/ruff format --check .        # 通过
python3 reports/audit/A-20261026-framework/audit_probe.py        # 132 PASS / 0 FAIL
.venv/bin/python reports/audit/A-20261026-framework/framework_check.py   # 框架完整性检查
```

## 写入者与授权

- 当前写入者：无（T-20261026-01 结束时已释放 `.agent-lock`）。
- GitHub 推送：2026-10-26 用户在 T-20261026-01 中明确要求推送。**没有常设推送授权**，以后每次推送都要确认。
- 仓库可见性：**公开**，与课程"每组一个私有仓库"的要求不符，由学生处理（Q3）。

## 最近的任务与运行

| task_id | 状态 | 摘要 |
|---|---|---|
| T-20261026-01 | completed | 框架重建（v0.2.0） |

- 正式运行：无。
- legacy 记录：`reports/legacy/`（cell_30 的旧协议回测，未验证）。

## 阻塞与待决事项（详见 docs/sources-and-open-questions.md）

1. **Q3 仓库可见性**：在 GitHub 的 Settings 中改为 Private，并添加课程人员与组员。
2. **`.cursorignore` 未创建**：Cursor 的权限配置禁止代理写这个文件。拟定的内容见任务卡 T-20261026-01，需要用户授权或手动创建。
3. **Q8 项目外暂存件**：`/ai/workspace/_gh_AIE1903/`、`_merge_stage/`、`AIE1903_premerge_code.tgz`、`aie1903_merged_code.tgz` 已核实与 Git 历史重复，等待学生确认是否删除。
4. **Q5 Claude Code 与 Grokbot 的运行模式**：待学生决定，推荐模式 B（environment.md §4）。
5. **Q4 sample 末行疑似含真值**：是否反馈给课程方，由学生决定。
6. **Q6 团队信息**：组员名单和分工待填（README）。
7. **待复核**：ADR-0002 与 ADR-0003 待学生确认。
8. **规则加载**：需要在新的 Cursor 会话和真实的 Claude Code 会话中各验证一次（方法见任务卡）。

## 下一步（可以直接开工）

1. 按 `docs/roadmap.md` 的 M1 建任务卡 `T-YYYYMMDD-01-data-layer`。实现 `aie1903.config`（项目根查找、配置加载与哈希）和 `aie1903.data`（`load_train`、`load_test_template`、合同校验、checksum 校验），并写 `tests/contract/` 的合同测试。验收标准：在三个数据集上复现 A-20261026-framework 的结论。
2. 之后依次做 M2（指标）→ M3（切分与守卫）→ M4（运行记录）→ M5（基线回测：先 cell_30，再 cell_217）。
