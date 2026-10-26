# configs/

这里是所有可变参数的**唯一来源**，代码不得硬编码这些值。每次运行时，tracking 会保存解析后的配置快照和配置哈希。

| 文件 | 内容 | 谁可以改、怎么改 |
|---|---|---|
| `datasets.yaml` | 数据集注册表与数据合同：文件、时段、取值域、指标阈值、官方来源、隔离规则 | 事实发生变化时，随审计一起更新 |
| `validation-plan.json` | 验证协议 expanding_289_v1（路径由工作区规则指定） | 需要学生批准，并新增 ADR |
| `runtime.yaml` | 设备、线程、预算、种子、输出目录 | 默认值的改动要在任务卡里说明；放宽预算需要学生批准 |
| `experiments/` | 每个实验一个配置；`_template.yaml` 是模板 | 跟随任务创建，文件名格式为 `<dataset>__<model>__<variant>.yaml` |

## 规则

- 实验配置只写与默认值不同的部分；数据合同和协议用 id 引用，不要复制一份内容。
- 已经被运行记录引用过的实验配置不要再改（否则历史无法复现）。需要改动时，新建一个 `variant`。
- `validation-plan.json` 的 `heldout_status` 一旦从 `untouched` 改为 `evaluated`，就不能再改回去。
