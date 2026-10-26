# 审计 A-20261026-server：学校服务器摸底

- 任务：T-20261026-02
- 执行者：cursor/claude-opus-5.5
- 时间：2026-10-26 22:22–22:35 +08:00
- 范围：本机（hostname `ai`）的平台、容器资源、存储、网络、进程、GPU 与训练栈。只读，外加有上限的小基准和随机数据训练冒烟。

## 证据文件

| 文件 | 内容 | 复现命令 |
|---|---|---|
| `server_probe.py` → `server-facts.json` | 平台、cgroup、CPU/内存、存储、进程与工具、网络、GPU、Python 与 torch 的事实（环境变量只记录白名单中的值，不读取任何令牌或密码） | `.venv/bin/python reports/audit/A-20261026-server/server_probe.py` |
| `perf_probe.py` → `perf.json` | CPU 矩阵乘随线程数的变化、cgroup 节流、NFS / overlay / shm 的读写与小文件延迟（约 15 秒） | `.venv/bin/python reports/audit/A-20261026-server/perf_probe.py` |
| `train_smoke.py` → `train-smoke.json` | 用随机数据训练极小的 LSTM：CPU、GPU FP32、TF32、bf16 各跑几步；确定性；`torch.compile`；峰值显存与内存（约 11 秒，显存不超过 0.4 GiB） | `.venv/bin/python reports/audit/A-20261026-server/train_smoke.py` |

三个脚本都只是证据，不属于项目代码。训练相关的可复用实现属于 `aie1903.models`、`aie1903.pipelines` 和 `aie1903.tracking`（roadmap M4、M5）。

## 结论

### 1. 平台是怎么运作的

- 本机是学校 AI 平台上的一个 **Kubernetes Pod**（有 `KUBERNETES_*` 环境变量和 service account 挂载）。镜像基于 **NVIDIA NGC PyTorch 26.05**，系统是 Ubuntu 24.04.4，内核 5.15。
- **入口脚本** `/usr/local/bin/run.sh` 依次做这些事：
  1. 把 PID 1 的环境变量写进 `/etc/profile`，这样 SSH 登录后也能拿到同样的环境；
  2. 启动 sshd（端口 22，允许 root 登录）；
  3. 设置 root 密码（由平台注入；本审计没有打印）；
  4. 启动 Jupyter（端口 8888，工作目录 `/ai`）；
  5. 只有在容器创建时设置了 `TENSORBOARD_LOG_DIR`，才启动 TensorBoard（端口 6006）；
  6. 最后 `sleep infinity`。
- **平台对外暴露的端口只有 22 和 8888**（k8s Service resource-master）。TensorBoard 的 6006 没有对外暴露；Jupyter 也没装 server-proxy。
- **没有作业调度器**（没有 sbatch、qsub、kubectl）。训练就是在这个开发容器里直接运行进程。
- **Cursor 服务端**装在 `/root/.cursor-server`，属于临时盘。它带有 `--enable-remote-auto-shutdown` 参数，客户端断开 **300 秒**后自动关闭（`VSCODE_SERVER_SHUTDOWN_TIMEOUT=300`）。

### 2. 资源

| 项 | 实测 | 对训练的影响 |
|---|---|---|
| CPU | 宿主机为 2 颗 AMD EPYC 9534（256 个逻辑核可见）；**cgroup 配额 24 核**；cpuset 没有限制 | 进程能"看到" 256 核，但每秒最多只能用 24 核的算力 |
| 默认线程数 | **torch 默认 128 线程，OpenBLAS 默认 64 线程** | 不设置就会严重过度订阅 |
| 线程实测（3000×3000 float64 矩阵乘） | numpy：1 线程 57、8 线程 398、24 线程 **995**、默认 711 GFLOPS（被节流 10.6 秒）；torch：8 线程 391、24 线程 **993**、默认（128 线程）**330** GFLOPS（被节流 51.8 秒） | **线程数必须显式设置，不超过 24**；默认值会慢 30% 到 3 倍 |
| 内存 | cgroup 上限 32 GiB，**没有 swap**（`/proc/meminfo` 经 lxcfs 虚拟化，显示的就是 32 GiB）；目前没有发生过 OOM | 超过上限会直接被 OOM kill |
| `/dev/shm` | tmpfs，显示 252G，但占用的内存**计入 32 GiB 上限** | DataLoader 的共享内存不会不够，但同样计入内存 |
| GPU | 1 张 **RTX 5090**：32607 MiB（可用 31.4 GiB），sm_120，170 个 SM，功耗上限 575 W，持久模式开启，Default 计算模式；GPU 位于 NUMA 0（CPU 0-63、128-191）；当前没有其他进程占用 | 显存对本项目绰绰有余 |
| 进程数与文件句柄 | pids.max 618131；open files 1048576；memlock 64 KB | 单卡训练不受影响 |

### 3. 存储

| 位置 | 类型 | 是否持久 | 实测性能 |
|---|---|---|---|
| `/ai/workspace` | NFSv3（hard 挂载，rsize/wsize 1 MiB），可用 214T | **持久** | 写 1019 MiB/s（含 fsync），读 1.1 GB/s；**小文件创建约 1.15 ms/个**（是 overlay 的 23 倍） |
| `/`、`/tmp`、`/root` | 容器 overlay（3.5T，与节点共享） | **临时**（随环境释放而消失，除非保存镜像） | 写 939 MiB/s，读 5.8 GB/s，小文件 0.05 ms |
| `/dev/shm` | tmpfs | 临时 | 写 3.2 GB/s |

- 已经落在临时盘上的：Cursor 服务端和会话记录、`/root/.cache/pip`。如果以后下载预训练权重，torch、huggingface 的缓存默认也会写到 `/root/.cache`。
- NFS 是 hard 挂载：存储服务卡住时，进程会一直阻塞等待，不会报错退出。

### 4. 网络

- **DNS**：使用 NodeLocal DNSCache（169.254.20.10），配置为 `ndots:5`，有 3 个 search 域。`github.com` **偶尔解析失败**，失败成簇出现：一次 50 次查询中失败 3 次，另一次 400 次中失败 1 次。写成 FQDN（`github.com.`）时，400 次查询**零失败**。这解释了 git push 时偶发的 "Could not resolve hostname"。
  - **更正（22:47，同一任务内补记）**：FQDN 在 `getent` 中零失败，并**不**意味着 SSH 不会失败。把 SSH 配置改为 `HostName github.com.` 后，推送时仍然连续两次报 "Could not resolve hostname github.com."，改回原配置后的首次认证也失败了一次。所以上面"这解释了……"一句只说对了一半：失败来自解析服务本身的偶发错误，与 search 域无关。唯一有效的缓解办法是重试。
- **没有 IPv6 出网能力**，但 DNS 会对部分域名返回 IPv6 地址。curl 和 Python 会自动回退到 IPv4；个别工具失败时可以强制走 IPv4。
- **没有代理**。可以访问：GitHub（SSH 认证正常）、api.github.com、PyPI、阿里云 PyPI 镜像（最快）、download.pytorch.org、huggingface.co。清华镜像和 hf-mirror 时通时不通，kaggle 不通。

### 5. 软件栈

- **CUDA 与相关库**：CUDA 13.2.1（nvcc 13.2.78），驱动 610.43.03（支持到 CUDA 13.3），cuDNN 9.22，NCCL 2.30.4，TensorRT 10.16。
- **torch**：2.12.0a0（NV 26.05），arch 包含 sm_120，支持 bf16，Flash SDP 可用；triton 3.7、flash_attn 2.7.4、transformer_engine 2.15、apex、numba 0.64、tensorboard 2.20、wandb 0.26 也都在。
- **TF32 默认开启**：NGC 设置了 `TORCH_ALLOW_TF32_CUBLAS_OVERRIDE=1`，默认的 `float32_matmul_precision` 为 high，cuDNN 的 allow_tf32 为 True。实测 GPU 上 FP32 矩阵乘的相对误差：默认（TF32）为 **2.9e-4**；调用 `torch.set_float32_matmul_precision("highest")` 后为 **3.7e-7**（真正的 FP32）。显式设置可以覆盖环境变量。
- **numpy 的 BLAS**：scipy-openblas 0.3.27，最多 64 线程。
- **缺少的包**：scikit-learn、statsmodels、xgboost、lightgbm、lightning、optuna、polars、threadpoolctl。pip 约束文件是空的，默认索引是 PyPI。
- **Jupyter 内核**：只有 `python3`，指向系统 Python，看不到 `.venv` 里的包。

### 6. 训练冒烟（随机数据，`train-smoke.json`）

小 LSTM（2 层，隐藏维 64，批大小 128，回看 288 步，输出 289 步）的结果：

| 设备与精度 | 每步耗时 | 峰值显存 | 备注 |
|---|---|---|---|
| CPU，8 线程 | 112.5 ms | — | — |
| GPU，严格 FP32 | **2.41 ms** | 400 MiB | 约快 47 倍 |
| GPU，TF32（默认） | 2.38 ms | 400 MiB | **结果与 FP32 不同**，参数校验和 4.1593 对 4.1611 |
| GPU，bf16 autocast | 1.99 ms | 240 MiB | 精度更低 |

- **确定性**：开启 `torch.use_deterministic_algorithms(True)` 并设置 `CUBLAS_WORKSPACE_CONFIG=:4096:8` 后，同种子的两次 GPU FP32 训练**逐位一致**。
- **`torch.compile`**：在 sm_120 上可用，首次编译 3.25 秒，之后每步 1.37 ms。
- **资源**：进程结束后显存完全释放；峰值 RSS 1.85 GiB（主要是 torch 和 CUDA 的上下文）。

### 7. 进程与长任务（实测）

- 在终端里用普通 `&` 放到后台的进程，仍然属于 Cursor 会话；Cursor 服务端关闭时可能被一起结束。
- `setsid nohup … &` 会创建新会话，父进程变为 PID 1，可以活过终端和 Cursor 断线。**但活不过环境释放**，容器一回收就没了。
- 没有 tmux 和 screen；有 `nohup`、`setsid`、`timeout`、`nice`、`ionice`、`taskset`、`numactl`、`flock`、`watch`。

## 写入了哪里

- 详细手册：`docs/runbooks/environment.md`（服务器怎么运作）、`docs/runbooks/training.md`（怎么训练）。
- 强制规则：`rules/30-server.md`、`rules/35-training.md`，所有代理都可以读，生成方式见 `rules/README.md`。
- 默认配置：`configs/runtime.yaml`（线程上限、精度、确定性）。

## 无法从容器内确认的事项

计费方式、机时上限、GPU 是否被独占、平台是否会在空闲时自动回收。按课程 Quick Start 的说法是"后付费、有机时限制、用完要释放"，以平台页面为准。
