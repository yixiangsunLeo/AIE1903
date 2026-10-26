# data/

| 路径 | 内容 | 进 Git |
|---|---|---|
| `raw/<dataset_id>/` | 官方原始文件，**只读** | 否 |
| `checksums.sha256` | 全部原始文件的 sha256 | 是 |
| `interim/`、`processed/` | 可以重新生成的中间数据，必须能由代码与配置重建 | 否 |

数据合同（结构、时段、取值、指标）见 `docs/project-context.md` §4 和 `configs/datasets.yaml`。

## 当前状态（2026-10-26，审计 A-20261026-framework）

| dataset_id | 角色 | 文件 | 与官方提交 49822d8 的一致性 |
|---|---|---|---|
| cell_217 | 主线 | train、test、sample、PDF | 4/4 逐字节一致 |
| cell_30 | 演练 | train、test、sample、PDF | 4/4 逐字节一致 |
| grid_273 | 扩展（主线完成后） | train、test、sample、membership、PDF | 5/5 逐字节一致（2026-10-26 补齐） |

## 校验

```bash
cd /ai/workspace/AIE1903/data && sha256sum -c checksums.sha256
```

## 重新获取（例如在新机器上）

从固定的官方提交获取；先下载到临时目录，校验后再放进来；**不覆盖已有文件**。

```bash
tmp=$(mktemp -d)
git clone -q --filter=blob:none --no-checkout https://github.com/AIE1903-DataCompetition-26AY/competition-data.git "$tmp/cd"
git -C "$tmp/cd" checkout -q 49822d82552c980bb83eb445548268f3565882ef -- cell_217 cell_30 grid_273
mkdir -p raw && cp -rn "$tmp/cd/cell_217" "$tmp/cd/cell_30" "$tmp/cd/grid_273" raw/
sha256sum -c checksums.sha256
```

## 恢复（checksum 报告缺失或不一致时）

两份 PDF 在 Git 历史中保存有官方原件，可以直接恢复：

```bash
cd /ai/workspace/AIE1903
git show archive/legacy-scaffold:data/raw/cell_217/data_description_for_cell_217.pdf > data/raw/cell_217/data_description_for_cell_217.pdf
git show archive/legacy-scaffold:data/raw/cell_30/data_description_for_cell_grid.pdf > data/raw/cell_30/data_description_for_cell_grid.pdf
```

其他文件按上一节"重新获取"的方法从官方提交下载。恢复后再执行一次 `sha256sum -c checksums.sha256`，并在 worklog 中记录。

## 规则

- 不编辑、不重命名、不覆盖 `raw/` 中的文件。发现文件与 checksum 不一致时，停下来报告。
- 一个运行只读一个数据集（ADR-0005）；任何 `*_sample_submission.csv` 的数值都不得读取。
- test.csv 中流量列为空是规定的格式，不要试图补全。
