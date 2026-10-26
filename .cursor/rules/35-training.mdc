---
description: 训练与实验运行规则：预算、线程、精度、确定性、启动、监控与记录（全局，始终加载）
alwaysApply: true
---

# 训练与运行规则

详细流程见 docs/runbooks/training.md，运行记录格式见 docs/standards/records.md，默认值见 configs/runtime.yaml。

**开跑前**
- 任务卡写明预算（时长、内存、GPU 分钟与显存上限、配置个数）和要用的 fold。使用 GPU 或 heldout，都要有学生的批准记录。
- 确认没有冲突：查看 nvidia-smi 和 ps，以及 runs/*/run.json 中是否有 running 的运行。
- 数据通过 sha256 校验；代码已提交，否则在 run.json 里记录 git_dirty。

**必须显式设置**
- **线程**：OMP、OPENBLAS、MKL、NUMEXPR 四个 `*_NUM_THREADS` 环境变量，加上代码里的 `torch.set_num_threads`。默认 8，上限 24。
- **精度**：默认 `fp32_strict`，即 `torch.set_float32_matmul_precision("highest")` 加上 `torch.backends.cudnn.allow_tf32 = False`。原因：镜像默认开启 TF32，会改变结果（矩阵乘相对误差 2.9e-4，FP32 为 3.7e-7），而对本项目的小模型几乎没有提速。用 bf16 必须在任务卡里说明理由。
- **确定性**：设置全部种子；打开 `torch.use_deterministic_algorithms(True)`；设置 `CUBLAS_WORKSPACE_CONFIG=:4096:8`；`cudnn.benchmark=False`。实测这样 GPU 结果可以逐位复现。
- **其他**：`WANDB_MODE=disabled`，`PYTHONUNBUFFERED=1`；CPU 运行设置 `CUDA_VISIBLE_DEVICES=""`。

**启动与监控**
- 启动方式：`setsid nohup env … timeout <预算> .venv/bin/python … > runs/<run_id>/stdout.log 2>&1 < /dev/null &`，并把 PID 写进 run.json。不要在前台或用普通 `&` 跑长任务。
- 断线重连后，先查 PID 和 run.json 的状态，不要重复启动。主动停止用 kill（SIGTERM），状态记为 cancelled。
- 设备选择：统计模型和树模型用 CPU；神经网络用 GPU。小 LSTM 实测：GPU 每步 2.4 ms，CPU 每步 112 ms。

**记录**
- 每次运行（包括 smoke）都有 run_id，开始时就写 run.json。
- 要记录：线程数、设备、精度、是否确定性、种子、墙钟时间、峰值 RSS、峰值显存、产物的 sha256。
- 指标一律在 CPU 上用 float64、按原始尺度计算。
- 失败、OOM、超时（退出码 124）、取消都要如实记录；绝不把失败改成成功。
- 运行结束后，确认进程已退出、显存已释放；摘要写入 reports/runs/，并在 experiments.csv 中加一行。
