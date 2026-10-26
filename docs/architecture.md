# 架构：代码功能区与接口约定

> 状态：v0.2.x 框架（骨架始于 v0.2.0）。各功能区目前只有包骨架和职责说明，**还没有实现**。实现按 `docs/roadmap.md` 的里程碑推进。新增模块必须先在本文件登记，再写代码。

## 1. 设计原则

1. **由接口保证时间安全。** 模型的 `predict` 只接收预测步数，拿不到任何未来值；所有切分逻辑集中在 `splits`，并自带越界检查。
2. **评估与建模分离。** `evaluation` 不依赖 `models`，`models` 也不依赖 `evaluation`，杜绝"看着指标调模型内部"。
3. **配置驱动。** 路径、数据集、协议、设备、线程、种子全部来自 `configs/`，并由 `tracking` 做快照。
4. **每次运行可追踪。** `pipelines` 的每个入口都必须经过 `tracking`，生成 run_id 和运行记录。
5. **一个功能只有一个归属。** 新代码先找到所属功能区；不建 utils、common、helpers 这类杂物间。

## 2. 目录

```text
src/aie1903/
├── __init__.py      包版本与功能区索引
├── config/          配置加载、校验、路径解析、配置哈希
├── data/            数据注册表、官方文件读取、数据合同校验、审计、官方数据获取
├── splits/          验证协议、fold、预测起点、时间边界守卫
├── features/        按预测起点构造特征；只在训练段拟合的变换
├── models/          预测器接口、注册表、基线与各类模型
├── evaluation/      官方五指标、提交文件校验
├── tracking/        run_id、运行元数据、产物哈希、实验索引、记录校验
├── pipelines/       backtest / predict 等编排
├── viz/             标准图表
└── cli.py           （计划）统一命令行入口
```

## 3. 依赖方向

只允许下表列出的内部导入；禁止反向依赖和循环导入。

| 功能区 | 允许导入的内部功能区 | 明确禁止 |
|---|---|---|
| config | 无 | 任何内部功能区 |
| data | config | features、models、pipelines |
| splits | config | data 的 IO 函数（只用类型）、models |
| features | config、data（类型）、splits | models、evaluation、pipelines |
| models | config、data（类型）、features | **evaluation**、pipelines、tracking |
| evaluation | config、data（合同与类型） | **models**、features、pipelines |
| tracking | config | models、features、pipelines |
| pipelines | 以上全部 | cli |
| viz | config、data（类型）、evaluation（结果类型） | models、pipelines |
| cli（计划） | pipelines、data、evaluation、tracking | — |

```text
config ◄─ data ◄─ features ◄─ models
  ▲         ▲        ▲          ▲
  ├── splits ────────┘          │
  ├── evaluation (+data)        │
  ├── tracking                  │
  └──────── pipelines ──────────┘  ◄─ cli
viz ─► config, data, evaluation
```

## 4. 各功能区契约

下面的接口是**草案**。实现时可以细化，但不能削弱其中的不变量；如果改动了接口，必须同步更新本节。

### 4.1 config

- **职责**：加载 `configs/*.yaml|json`，校验必需键，相对项目根解析路径，生成不可变的已解析配置，并计算配置哈希（规范化 JSON 的 sha256）。
- **计划模块**：`loader.py`、`schema.py`、`paths.py`。
- **接口草案**：`find_project_root() -> Path`（向上查找同时含 AGENTS.md 和 pyproject.toml 的目录）；`load_config(path, overrides=None) -> ResolvedConfig`；`config_sha256(cfg) -> str`。
- **不变量**：不硬编码绝对路径，项目根靠查找而不是假定。环境变量 `AIE1903_PROJECT_ROOT`、`AIE1903_DATA_ROOT`、`AIE1903_RUNS_ROOT` 可以覆盖默认值，覆盖要记录在运行快照中。已解析配置必须能序列化为严格 JSON。
- **必测**：路径解析结果、环境变量覆盖、缺键报错、哈希稳定（键顺序不影响结果）。

### 4.2 data

- **职责**：数据注册表（`configs/datasets.yaml`）；按数据集读取官方文件；数据合同校验；checksum 校验；数据审计；从官方仓库获取缺失文件（固定提交，先校验后放置，不覆盖已有文件）。
- **计划模块**：`registry.py`、`io.py`、`contract.py`、`checksums.py`、`audit.py`、`fetch.py`。
- **核心类型**：`Panel`，字段如下：
  - `dataset_id`
  - `timestamps`：naive DatetimeIndex
  - `columns`：tuple[str]
  - `values`：float64 数组，形状 [T, N]
  - `start_index`：首行在官方 2017 点时间轴上的绝对行号；切片后保留绝对位置，供 splits 做越界检查
- **接口草案**：
  - `load_train(dataset_id) -> Panel`
  - `load_test_template(dataset_id) -> TestTemplate`：只含时间戳和列，不含任何数值
  - `load_membership() -> DataFrame`：仅 grid_273
  - `validate_contract(dataset_id) -> ContractReport`
  - `verify_checksums() -> ChecksumReport`
  - `fetch_official(dataset_id, commit) -> FetchReport`
- **不变量**：
  - 对 `data/raw/` 只读。
  - 不做时区转换。
  - 一次调用只读取一个数据集的文件；不提供任何跨数据集的对齐函数。
  - **不提供读取 sample 数值的函数**；sample 只在 evaluation 的格式校验中按列名与时间戳比对。
- **必测**：合同校验能抓住列顺序、时间轴、行数、取值域、测试集非空等错误；checksum 不一致时报错；跨数据集读取被拒绝。

### 4.3 splits

- **职责**：加载验证协议（`configs/validation-plan.json`），产出 fold，并守卫时间边界。
- **计划模块**：`protocol.py`、`guards.py`。
- **接口草案**：
  - `Fold(id, role, fit=slice, forecast=slice)`，role 取 dev、heldout、final 之一
  - `load_protocol(path) -> Protocol`
  - `iter_folds(protocol, include_heldout=False) -> Iterator[Fold]`
  - `check_supervised_windows(target_max_index, fit_end)`
  - `check_feature_sources(source_indices, origin)`
- **不变量**：
  - 索引从 0 开始，区间左闭右开。
  - heldout 默认不可见，必须显式开启，并记录在运行元数据中。
  - 监督样本的全部目标都必须小于 fit_end。
  - 任何特征的源索引都必须小于起点（origin）。
- **必测**：目标窗口跨界时报错；heldout 默认不出现；第 289 步的 lag-288 越界被拒绝；各 fold 的预测窗口互不重叠。

### 4.4 features

- **职责**：按预测起点构造特征，包括日内位置、星期、滞后、滚动统计和跨序列聚合；需要拟合的变换（缩放、log1p 等）只在当前 fold 的训练段拟合，并能把预测逆变换回原始尺度。
- **计划模块**：`calendar.py`、`lags.py`、`cross_series.py`、`transforms.py`。
- **接口草案**：
  - `FeatureSpec(name, source_offsets)`：每个特征声明相对起点的源偏移
  - 变换接口：`Transform.fit(panel) -> state`、`transform`、`inverse`
- **不变量**：
  - 测试或预测窗口的时间戳可以用来构造日历特征（时间戳本身是公开的），但对应的数值不可用。
  - 所有统计量只来自 fold 训练段。
  - 不使用包含 heldout 或测试段的全量统计。
- **必测**：修改训练段之后的真实值，不会改变任何特征；逆变换往返后误差在容差之内。

### 4.5 models

- **职责**：统一的预测器接口与注册表；季节朴素等基线；之后的统计、机器学习、深度学习与 GP 模型。
- **计划模块**：`base.py`（接口与 `FitContext`）、`registry.py`、`baselines.py`，之后按模型族加文件。
- **接口草案**：

```python
class Forecaster(Protocol):
    name: str

    def fit(self, history: Panel, *, context: FitContext) -> "Forecaster": ...
    def predict(self, horizon: int) -> np.ndarray: ...  # 形状 (horizon, n_series)，原始尺度，有限值
```

- `FitContext` 包含 seed、device、threads、预算和 fold_id，全部来自 runtime 配置。
- 季节朴素基线的定义：`pred[h] = history[-288 + (h % 288)]`。
- **不变量**：
  - `predict` 不接收任何未来数据。
  - 输出为原始计数尺度，必须是有限值；推荐非负，是否截断由配置决定，并记录在运行中。
  - 随机性只来自 `FitContext.seed`。
- **必测**：输出形状与有限性；固定种子下结果可复现；改动未来值不影响预测；第 289 步不读取越界数据。

### 4.6 evaluation

- **职责**：在原始尺度上计算官方五指标，并校验提交文件。
- **计划模块**：`metrics.py`、`submission.py`。
- **接口草案**：
  - `score(y_true, y_pred, *, track) -> MetricReport`：每项给出 `{value, count}`，masked 项另加 `threshold`，并附 `definition_version`
  - `validate_submission(csv_path, dataset_id) -> SubmissionReport`
- **不变量**：
  - 都是纯函数。
  - mask 只看真实值；在全部保留位置上整体平均，不先按序列平均。
  - 空 mask 时 `value=None`、`count=0`。
  - 不加 epsilon。
  - grid 的 MAPE 只计 y>0 的位置。
  - 提交校验区分"无效"（缺失、非数值、行列不符）和"警告"（负值）。
- **必测**：手算用例；不同有效数量时的整体平均；grid 的 0 值被排除；空 mask；格式错误能被发现。

### 4.7 tracking

- **职责**：生成 run_id；运行**开始时**写下元数据，结束时补全；做环境与数据快照；计算产物哈希；维护实验索引；校验记录完整性（verify-records）。
- **计划模块**：`run.py`、`snapshot.py`、`index.py`、`verify.py`。
- **接口草案**：
  - `start_run(kind, dataset_id, config, task_id, actor) -> RunHandle`：用作上下文管理器，异常时自动写 `status=failed`
  - `RunHandle.add_artifact(path)`
  - `RunHandle.finish(status, metrics)`
  - `verify_records() -> Report`
- **不变量**：
  - 输出严格 JSON（不出现 NaN 或 Infinity，缺失值写 null）。
  - 失败不会被标成成功。
  - 代码未提交时标记 `git_dirty=true`，并保存 diff 的哈希。
  - 记录字段见 `docs/standards/records.md` 与 `docs/templates/run-record.json`。
- **必测**：中断或异常时的状态；严格 JSON；索引行与摘要文件一致。

### 4.8 pipelines

- **职责**：编排流程。
  - `backtest`：对每个 fold 依次切出历史、拟合、预测、评分、记录。
  - `predict`：用全部 1728 行拟合，预测 289 步，写出提交 CSV 与元数据，再做格式校验。
- **计划模块**：`backtest.py`、`predict.py`。
- **不变量**：
  - 默认只跑 dev fold。
  - 最终预测的时间戳和列取自该数据集的 test 模板。
  - 每个入口都包在 `tracking.start_run` 里。
- **必测**：端到端的小规模运行（cell_30 演练）；失败运行的状态记录。

### 4.9 viz

- **职责**：生成标准图表，包括序列概览、日周期叠加、各 fold 的预测与真值对比、按步长和按日内时刻的误差。
- **不变量**：
  - 图只从已记录的产物生成，保存在 `runs/<run_id>/figures/`；选入报告的再复制到 `reports/figures/`。
  - 坐标轴标注为匿名计数单位。

### 4.10 cli（计划）

| 命令 | 调用的功能区 | 里程碑 |
|---|---|---|
| `doctor` | config、tracking | M7 |
| `audit-data --dataset` | data | M1 |
| `fetch-data --dataset` | data | M1 |
| `backtest --config` | pipelines | M5 |
| `predict --config` | pipelines | M6 |
| `validate-submission --dataset --input` | evaluation | M6 |
| `verify-records` | tracking | M7 |

统一入口为 `python -m aie1903.cli <command>`。在这些命令真正实现并验证之前，README 里不得把它们写成可用命令。

## 5. 数据流

```text
backtest：configs → data.load_train(ds) → splits.iter_folds
          → 对每个 fold：features(fit 段) → models.fit → models.predict(289)
          → evaluation.score(forecast 段真值, 预测) → tracking 记录 → viz 出图
predict： configs → data.load_train(ds)（全部 1728 行）→ models.fit → predict(289)
          → 按 data.load_test_template 写出 CSV → evaluation.validate_submission → tracking
```

## 6. 存储布局

| 路径 | 内容 | 进 Git |
|---|---|---|
| `data/raw/<dataset_id>/` | 官方原始文件，只读 | 否（用 `data/checksums.sha256` 校验） |
| `data/interim/`、`data/processed/` | 可重新生成的中间数据 | 否 |
| `runs/<run_id>/` | 运行的完整产物：run.json、配置快照、日志、预测、图 | 否（只在持久盘） |
| `reports/runs/<run_id>.json` | 运行摘要（小、脱敏） | 是 |
| `reports/experiments.csv` | 实验索引 | 是 |
| `reports/audit/<audit_id>/` | 审计报告与证据 | 是 |
| `reports/figures/`、`reports/tables/` | 选入报告的图表 | 是 |
| `submissions/<dataset_id>/` | 提交 CSV（不进 Git）与元数据（进 Git） | 部分 |
| `artifacts/models/` | 大模型权重 | 否 |
| `logs/` | 长任务日志、代理会话备份 | 否 |

## 7. 测试布局

```text
tests/
├── test_layout.py        框架结构冒烟测试（已有）
├── <area>/test_*.py      各功能区单元测试，随实现补充
├── leakage/              时间边界与泄漏测试（M3 起，必须有）
└── contract/             基于真实数据的合同测试（数据缺失时 skip，不算失败）
```

## 8. 旧代码映射（标签 `archive/legacy-scaffold`）

| 旧模块 | 新归属 | 结论 |
|---|---|---|
| `aie1903_project/metrics.py` | evaluation | 需要重写：空 mask 返回 NaN、没有计数、阈值写死且只支持 cell |
| `aie1903_project/baseline.py` | models（seasonal_naive） | 周期延拓的逻辑正确，可作参考；需要接入 Forecaster 接口 |
| `aie1903_project/backtest.py` | pipelines + splits | 旧 fold 互相重叠，还有一个截断成 288 步的 fold；按 expanding_289_v1 重写并接入 tracking |
| `aie1903_project/data.py`、`paths.py` | data、config | 硬编码 `/ai/workspace/AIE1903`，不校验数据合同；需要重写 |
| `aie1903_project/predict.py` | pipelines | 只往 runs/ 写 CSV，没有元数据和格式校验；需要重写 |
| `aie1903_project/evaluation.py` | — | 与 metrics 重复，删除 |
| `aie1903_project/features.py` | features | 通用日历特征，不按预测起点构造；需要重写 |
| `models.py`、`pipeline.py`、`visualization.py` | models、config、viz | 通用模板代码，没有可复用的逻辑 |
| `scripts/*.py`（7 个） | cli.py | 7 个入口高度重复，合并为一个统一入口 |

查看旧代码的方法，例如：`git show archive/legacy-scaffold:src/aie1903_project/baseline.py`。
