# AIE1903 Group Project

本仓库是 AIE1903 小组最终项目的通用工程骨架。当前不预设最终研究题目、数据列、模型或评价指标，待选题确定后再在此基础上扩展。

## 运行位置

学校开发环境是可回收的临时算力，项目必须放在长期存储中：

```text
/ai/workspace/aie1903-group-project
```

不要把项目放在 `/workspace`、`/root` 或 `/tmp`。释放开发环境前，应确认代码、数据处理结果、模型和报告均已写入 `/ai/workspace`。

## 目录结构

```text
aie1903-group-project/
├── configs/                 # 可复现的实验配置
├── data/
│   ├── raw/                 # 原始数据，只读使用
│   ├── interim/             # 清洗或转换中的中间数据
│   └── processed/           # 可直接供模型使用的数据
├── notebooks/               # 探索、验证想法和展示结果
├── src/aie1903_project/     # 可复用的正式 Python 代码
├── scripts/                 # 训练、评估和预测入口
├── artifacts/
│   ├── models/              # 模型权重和序列化对象
│   └── outputs/             # 预测、导出结果和运行产物
├── reports/
│   ├── figures/             # 报告使用的图
│   └── tables/              # 报告使用的表
├── tests/                   # 小型、确定性的自动化检查
└── docs/                    # 设计决策、实验约定和补充说明
```

## 推荐工作流

1. 将拿到的原始资料放进 `data/raw/`，后续代码不直接改写原始文件。
2. 在 `notebooks/` 中快速理解数据和验证思路。
3. 将反复使用或影响最终结果的逻辑下沉到 `src/aie1903_project/`。
4. 将参数写入 `configs/`，不要散落在多个 Notebook 中。
5. 通过 `scripts/` 运行正式训练、评估和预测流程。
6. 模型与机器生成结果写入 `artifacts/`，报告图表写入 `reports/`。
7. 给核心数据契约和评价逻辑补充 `tests/`，确保组员修改后结果仍然一致。

## Notebook 约定

Notebook 适合探索和沟通，不应成为唯一可运行的最终实现。Notebook 中一旦出现第二次使用的函数，或一段逻辑会影响最终结论，应移入 `src/`，Notebook 只调用它。

建议命名：

```text
00_topic_exploration.ipynb
10_data_understanding.ipynb
20_feature_experiments.ipynb
30_model_experiments.ipynb
90_final_figures.ipynb
```

## 环境

学校镜像已提供与 GPU 匹配的 PyTorch/CUDA，因此本项目不在 `requirements.txt` 中重新固定 `torch`，避免覆盖平台提供的 GPU 版本。其余通用依赖可在确定需要时安装：

```bash
python -m pip install -r requirements.txt
```

建议在每次正式实验中记录 Python、PyTorch、CUDA、配置文件和随机种子。API 密钥、密码和个人令牌不得写入代码或 Notebook；本地环境变量可参考 `.env.example`。

## 选题确定后的第一轮改造

选题确定后，小组应共同补充：

- 问题定义和最终交付物；
- 原始数据来源、授权和字段契约；
- 数据切分方式，尤其是时空泄漏边界；
- 基线方法、主要模型和评价指标；
- 训练预算和复现实验所需的随机种子；
- 最终报告、演示和代码责任人。
