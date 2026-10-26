# 运行手册：在学校服务器上训练与运行实验

适用于回测、训练、最终预测，以及任何超过一分钟的运行。

- 服务器事实见 `docs/runbooks/environment.md`；强制要点见 `rules/35-training.md`；记录格式见 `docs/standards/records.md`。
- 文中依据的实测结果来自审计 `reports/audit/A-20261026-server/`。
- 统一入口 `python -m aie1903.cli ...` 要到 roadmap M4–M7 才实现，下文标注了"计划"的命令目前**还不能运行**。

## 1. 开跑前检查（每次都做）

1. **任务卡**：已经写明预算（时长、内存、是否用 GPU、运行次数），以及要用的 fold。动用 heldout 必须有学生的批准记录。
2. **没有冲突**：
   - `nvidia-smi --query-compute-apps=pid,used_memory --format=csv` 为空，或者里面列出的进程都是自己记录过的；
   - `ps -eo pid,etime,cmd | grep -v grep | grep python` 里没有重复的作业；
   - `runs/*/run.json` 中没有 `"status": "running"` 的同类运行。
3. **代码与数据**：
   - 代码已提交。如果 `git status` 不干净，run.json 必须标记 `git_dirty=true`，并记录 diff 的哈希；
   - `(cd data && sha256sum -c --quiet checksums.sha256)` 通过。
4. **空间**：`df -h /ai/workspace`，预计的产物大小要写进任务卡。

## 2. 运行环境（必须显式设置）

下面这些值来自 `configs/runtime.yaml`，以后由 `aie1903.config` 和 `aie1903.tracking` 读取并写入 run.json。在此之前，手工运行时按下表设置：

| 设置 | 默认值 | 原因（实测） |
|---|---|---|
| `OMP_NUM_THREADS`、`OPENBLAS_NUM_THREADS`、`MKL_NUM_THREADS`、`NUMEXPR_NUM_THREADS` | 8（**不超过 24**） | 容器配额只有 24 核。torch 默认开 128 线程，矩阵乘只有 24 线程时的 1/3，并被节流 52 秒 |
| 代码中的 `torch.set_num_threads` | 同上 | 环境变量不一定覆盖 torch 已经创建的线程池 |
| `PYTHONUNBUFFERED=1` | 开启 | 日志立即落盘，断线后也能看到进度 |
| `WANDB_MODE=disabled` | 开启 | wandb 已安装；没有授权时不得把数据或指标传到外部 |
| `CUBLAS_WORKSPACE_CONFIG=:4096:8` | 开启 | 配合确定性算法，GPU 结果可复现（实测逐位一致） |
| `CUDA_VISIBLE_DEVICES` | CPU 运行设为 `""`；GPU 运行设为 `0` | CPU 运行时不初始化 GPU；明确运行用了哪个设备 |

## 3. 精度与可复现性

- **默认精度为 `fp32_strict`**。代码中执行 `torch.set_float32_matmul_precision("highest")` 和 `torch.backends.cudnn.allow_tf32 = False`。
  - 原因：NGC 镜像**默认开启 TF32**，GPU 上 FP32 矩阵乘的相对误差会从 3.7e-7 变成 2.9e-4，训练出的参数也会不一样；而本项目的小模型用 TF32 几乎没有提速（2.38 ms 对 2.41 ms 每步）。
- **`bf16_autocast`** 能快约 17%，显存省约 40%，但精度更低。只有在任务卡中说明理由后才使用，并记录在 run.json。
- **指标**一律在 CPU 上、用 float64、在原始计数尺度上计算（ADR-0003），与训练精度无关。
- **确定性**：
  - 设置种子：`random.seed`、`numpy.random.default_rng(seed)`、`torch.manual_seed`、`torch.cuda.manual_seed_all`；
  - 打开确定性：`torch.use_deterministic_algorithms(True)`，`torch.backends.cudnn.benchmark = False`；
  - 如果某个算子不支持确定性实现，运行会报错。此时在任务卡里写明，经批准后才能关闭确定性，并在 run.json 中记录 `deterministic=false`。
- **`torch.compile`** 在 sm_120 上可用，首次编译约 3 秒。默认不开；需要提速时在任务卡里说明。

## 4. 启动模板（脱离终端，可以活过 Cursor 或 SSH 断线）

```bash
cd /ai/workspace/AIE1903
RUN_ID="R-$(date +%Y%m%d-%H%M%S)-cell_217-backtest-snaive"      # 格式见 records.md
mkdir -p "runs/$RUN_ID"
# 在 M4 实现之前：先按 docs/templates/run-record.json 手工写好 runs/$RUN_ID/run.json（status=running）
setsid nohup env \
  OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8 \
  PYTHONUNBUFFERED=1 WANDB_MODE=disabled CUBLAS_WORKSPACE_CONFIG=:4096:8 CUDA_VISIBLE_DEVICES="" \
  timeout --signal=TERM --kill-after=60 30m \
  .venv/bin/python -m aie1903.cli backtest --config configs/experiments/<dataset>__<model>__<variant>.yaml --run-id "$RUN_ID" \
  > "runs/$RUN_ID/stdout.log" 2>&1 < /dev/null &
echo $! > "runs/$RUN_ID/pid"                 # 同时写进 run.json 的 pid 字段
```

- 上面的 `python -m aie1903.cli backtest ...` 是**计划中的命令**。实验配置按 `configs/experiments/_template.yaml` 创建，例如 M5 的 `cell_217__snaive__v1.yaml`。
- `timeout 30m` 用来强制执行 `runtime.yaml` 中的时长预算。退出码 124 表示超时，run.json 的状态要记为 `timeout`。
- GPU 运行：把 `CUDA_VISIBLE_DEVICES` 改为 `0`，在任务卡中写明显存预算；同一时间只跑一个 GPU 作业。
- **不要**直接在终端前台，或用普通 `&` 跑长任务。实测这样启动的进程可能随 Cursor 服务端自动关闭（断开 300 秒后）而被结束。

## 5. 监控

```bash
tail -n 50 -f "runs/$RUN_ID/stdout.log"
ps -o pid,etime,pcpu,rss,cmd -p "$(cat runs/$RUN_ID/pid)"
nvidia-smi dmon -s pucm -d 5                       # GPU 功耗、利用率、显存；Ctrl-C 退出
grep -E 'throttled_usec' /sys/fs/cgroup/cpu.stat   # 增长很快说明线程开多了
```

TensorBoard 已安装，但端口 6006 没有对外暴露。需要时把日志写到 `runs/<run_id>/tb/`，再通过 SSH 端口转发查看（`ssh -L 6006:127.0.0.1:6006 …`）。不要为此修改平台配置。

## 6. 中断、恢复与停止

- **断线重连后**：先查 `ps -p $(cat runs/$RUN_ID/pid)` 和 run.json 的状态，**不要直接重新启动**。
- **主动停止**：`kill $(cat runs/$RUN_ID/pid)`，等待 30 秒；如果仍然存在，再 `kill -9`。run.json 的状态记为 `cancelled`，并写明原因。
- **进程消失但 run.json 仍是 `running`**：检查 `memory.events` 中的 oom 计数和日志末尾，按真实原因记为 `failed` 或 `timeout`。**不能改成成功。**
- 需要断点续训时，checkpoint 存放在 `runs/<run_id>/checkpoints/`，只保留最新和最好的少数几个（NFS 不适合大量小文件）。续训视为新的 run_id，并引用原来的 run_id。

## 7. GPU 使用原则

- 数据量很小（1728×217）。季节朴素、统计模型和树模型**用 CPU**；神经网络（LSTM、GRU、Transformer）**用 GPU**。冒烟测试中，小 LSTM 在 GPU 上每步 2.4 ms，CPU 8 线程上每步 112 ms。
- 用 GPU 必须在任务卡中写明预算：分钟数、显存上限、配置个数。同一时间只跑一个 GPU 作业，跑完确认显存已经释放。
- 环境计费与 GPU 是否在用无关。所以训练完要及时收尾，不用时按流程释放环境，不要让环境空转。

## 8. 资源与结果记录（写进 run.json）

- 墙钟时间；峰值 RSS（`resource.getrusage(RUSAGE_SELF).ru_maxrss`，单位 KiB）；峰值显存（`torch.cuda.max_memory_allocated()`）。测不到的写 null 并说明原因。
- 线程数、设备、精度模式、是否确定性、种子；这一次启动实际设置的环境变量。
- 各 fold 的五项指标及计数（原始尺度）；训练损失要注明尺度。
- 产物（预测、图、checkpoint）的路径和 sha256。

## 9. 收尾

1. run.json 补全状态和结论；摘要写入 `reports/runs/<run_id>.json`，并在 `reports/experiments.csv` 中加一行。
2. 确认进程已经退出、显存已经释放（`nvidia-smi`）。
3. 更新任务卡、worklog、current-status，然后提交。推送需要授权。
4. 如果准备释放环境，按 `docs/runbooks/sync-backup-release.md` 执行。
