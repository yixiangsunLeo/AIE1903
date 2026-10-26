# ADR-0001 单一包 `aie1903` 与九个功能区

- 状态：accepted
- 日期：2026-10-26
- 提出与执行：cursor/claude-opus-5.5（T-20261026-01），依据用户要求"重新搭建、规定所有代码功能区"
- 学生复核：pending

## 背景

重建前，仓库里同时存在两个包：

- `src/aie1903_project/`：来自 GitHub 骨架，由合并时的代码充实；
- `src/aie1903/`：只是一个 re-export。

此外还有 7 个高度重复的 scripts 入口。`evaluation.py` 与 `metrics.py` 功能重复；路径被硬编码为 `/ai/workspace/AIE1903`；指标在空 mask 时返回 NaN，也不报告计数；验证折互相重叠。

用户要求先搭好框架、暂不写功能代码，并"把不需要的去掉"。

## 决策

1. 只保留一个包 `src/aie1903/`。它的名字与项目名和交接文档中的 CLI 示例 `python -m aie1903.cli` 一致。
2. 划分九个功能区：config、data、splits、features、models、evaluation、tracking、pipelines、viz，另计划一个 `cli.py`。每个功能区的职责、依赖方向、接口草案和不变量写在 `docs/architecture.md`。
3. 旧代码从工作树中移除，完整保存在标签 `archive/legacy-scaffold`（指向提交 203a73b）。architecture.md §8 给出旧模块到新功能区的映射，并列出已知缺陷，供重新实现时参考。
4. 发行名改为 `aie1903`，版本 0.2.0，Python 要求不低于 3.11（与 starter 保持一致）。

## 备选方案

- **保留 `aie1903_project` 包名，原地整理。** 它是原骨架的名字，但旧代码不成熟，按交接文档的说法，不属于"必须保持兼容的成熟代码"；两个包名并存会持续造成混乱。
- **保留旧代码，只做目录迁移。** 那样新框架里就会带着不符合新规范的实现，后续代理可能直接沿用它们的缺陷。

## 后果

- 当前没有可运行的基线代码，需要按 roadmap 的 M1–M7 重新实现。这是用户明确选择的顺序：先框架，后代码。
- 旧的 `reports/backtest_metrics_cell30.json` 移到 `reports/legacy/`，并标注为 legacy_unverified。

## 证据

- `git show archive/legacy-scaffold --stat`
- `docs/architecture.md` §8
