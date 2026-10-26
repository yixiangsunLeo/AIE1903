# 编码规范

适用于 `src/`、`tests/`、`scripts/` 和 `notebooks/`。功能区的边界与依赖规则在 `docs/architecture.md`，本文件只讲写法。

## 1. 语言与工具

- Python ≥ 3.11（学校镜像为 3.12.3），使用项目 `.venv`（见 `docs/runbooks/environment.md`）。
- 用 **ruff** 做检查和格式化，配置在 `pyproject.toml`。提交前运行 `.venv/bin/ruff check .` 和 `.venv/bin/ruff format --check .`。
- 测试用 **pytest**：`.venv/bin/python -m pytest`。
- 镜像里的 pandas 是 **3.x**，Copy-on-Write 语义，默认字符串类型为 `str`；写代码要按 pandas 3 的行为处理，不依赖链式赋值。

## 2. 写法

- 公开函数和类必须有类型标注和英文 docstring，docstring 要说明形状、单位和时间语义。
- 数值数组一律用 `float64`，形状约定为 `[T, N]`（时间 × 序列）。时间戳保持 naive，不做时区转换。
- 函数尽量写成纯函数。IO 只集中在 `data`、`tracking`、`pipelines`（以及 `viz` 保存图片）。
- 不硬编码路径、数据集名、阈值、步长、设备、线程数或种子，这些都从配置读取。代码里出现 288、289、1728 时，要么从配置取值，要么在常量处注明出处。
- 随机性只来自配置中的 seed，并传给 numpy 的 `default_rng` 和 torch。
- 出错时抛出明确的异常，说明哪个合同被违反。不要静默修补数据，比如自动补值或自动截断。
- 日志用 `logging`，不用裸 `print`（CLI 的最终输出除外）。

## 3. 命名

- 模块和函数用 `snake_case`，类用 `PascalCase`，常量用 `UPPER_SNAKE_CASE`。
- 时间相关的命名要明确：`origin`（预测起点的绝对行号）、`horizon`（步数）、`fit_end`（左闭右开区间的结束位置）。不要用含糊的 `idx`、`n`。
- 实验配置的文件名：`configs/experiments/<dataset>__<model>__<variant>.yaml`。

## 4. 测试

- 每个功能实现都要配套测试，放在 `tests/<area>/`。时间边界和泄漏测试放在 `tests/leakage/`，从 M3 开始必须有。
- 依赖真实数据的测试放在 `tests/contract/`；数据缺失时用 `pytest.skip`，不能伪造数据让测试通过。
- 测试数据用小的合成数组，在测试里直接构造，不要读取 sample 文件。

## 5. 依赖

- 依赖以 `pyproject.toml` 为准，实际验证过的版本记在 `requirements.lock`。
- 第一个需要某个新依赖的任务负责把它加进来，并在任务卡里说明原因；不要预先装一堆"以后可能用到"的框架。
- torch、CUDA 由镜像提供，不在项目里重新安装或固定版本。

## 6. Notebook

- Notebook 只做探索和展示，必须从 `aie1903` 导入功能，不能承载唯一的业务逻辑。
- 命名：`notebooks/NN_<topic>.ipynb`。
- 提交前清空输出（避免泄露受限信息，也让 diff 保持干净），也不要依赖未记录的执行顺序。
