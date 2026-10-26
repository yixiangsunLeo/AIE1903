# 审计 A-20261026-framework

- 任务：T-20261026-01
- 执行者：cursor/claude-opus-5.5
- 时间：2026-10-26 21:20–22:30 +08:00
- 范围：项目目录、Git、学校环境、三个官方数据集，以及重建后框架的完整性

## 文件

| 文件 | 内容 | 如何复现 |
|---|---|---|
| `audit_probe.py` | 数据合同审计与环境快照（只读） | `python3 reports/audit/A-20261026-framework/audit_probe.py` |
| `data-audit.json` | 三个数据集的逐项检查、统计信息、sample 与周期延拓的比对、跨数据集对齐分析 | 由 `audit_probe.py` 生成 |
| `environment.json` | OS、Python、包版本、CPU 与内存配额、GPU、磁盘、Git 状态 | 由 `audit_probe.py` 生成 |
| `pip-freeze-venv.txt` | `.venv` 中完整的 `pip freeze`，含镜像包，不含凭据 | `.venv/bin/python -m pip freeze` |
| `framework_check.py` | 框架完整性检查：必需文件、规则、导入、引用路径、配置一致性、hooks、忽略规则 | `.venv/bin/python reports/audit/A-20261026-framework/framework_check.py` |
| `framework-check.json` | 上面检查的结果 | 由 `framework_check.py` 生成 |

两个脚本都是**一次性证据**。它们的可复用版本分别属于 `aie1903.data`（M1）和 `verify-records`（M7）。

> **补充（2026-10-26，T-20261026-02）**：规则改为以 `rules/` 为唯一源之后，`framework_check.py` 按旧结构检查，已经不再适用。它和 `framework-check.json` 作为本审计当时的证据保留，不再更新。日常使用的框架检查改为 `scripts/check-framework.py`。

## 初始审计（改动之前，21:20–21:45）

| 项 | 状态 |
|---|---|
| 项目根与持久化 | `/ai/workspace/AIE1903` 位于 NFS 存储卷 sun（248T），可用 |
| Git | main 等于 origin/main，都在 203a73b，工作树干净；SSH 认证通过；仓库是**公开**的 |
| 已有代码 | 两个包并存，7 个重复入口；指标在空 mask 时返回 NaN 且不报计数；路径写死；验证折互相重叠 → 归档并移除（ADR-0001） |
| 已有运行 | 一份 cell_30 的 legacy 回测，没有元数据 → 保留到 `reports/legacy/` |
| 数据：cell_217、cell_30 | 8/8 齐全，与官方提交 49822d8 逐字节一致 |
| 数据：grid_273 | 缺失（属于可选扩展）→ 本轮已补齐，5/5 校验通过 |
| 冗余数据 | `.pdf.fixed` 与原 PDF 相同；根目录 tgz 与 raw 相同 → 已删除 |
| 环境 | 容器配额 24 核、32 GiB、一张 RTX 5090；Python 3.12.3；缺少 pytest 和 ruff；没有 node 和 claude |
| 运行中的作业 | 没有（只有平台自带的 jupyter 和 Cursor server） |
| 指令文件 | 一条旧规则 `aie1903.mdc`，一份 CLAUDE.md（访问信息），一份 WORK_INSTRUCTIONS.md；没有 AGENTS.md 和 SOUL.md |

## 数据审计结论（`data-audit.json`）

- 三个数据集共 136 项检查：**132 PASS、0 FAIL、0 WARN、4 INFO**。逐项覆盖的内容有：列与顺序、行数、时间格式与时间轴、时段边界、训练与测试的衔接、训练值（数值、有限、整数、非负、合同最小值、cell 无 0）、测试集为空、sample 的格式与有限性，以及 grid 的 membership（273 行；27×10 + 3×1；父 id 属于 Cell_001–030）。
- **跨数据集**：cell_30 与 cell_217 按行号对齐时 30/30 列匹配，按相同时钟对齐时 0/30。说明两者是同一批测量，cell_30 的时间标签晚 50 分钟 → ADR-0005。
- **sample**：cell_217 的 sample 是严格的周期延拓；cell_30 和 grid_273 的第 289 行不来自训练数据，疑似是测试期首个时刻的真值 → ADR-0005，以及未决问题 Q4。

## 最终审计（改动之后）

框架完整性检查的结果见 `framework-check.json`，汇总写在任务卡 T-20261026-01 的"真实验证"一节。还没有在新会话中验证规则的实际加载，原因与验证方法见任务卡。
