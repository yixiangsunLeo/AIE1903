# 运行手册：学校服务器（怎么运作、怎么用）

事实依据是审计 `reports/audit/A-20261026-server/`（2026-10-26 实测）。训练的具体做法见 `docs/runbooks/training.md`，必须遵守的要点已写进 `rules/30-server.md` 和 `rules/35-training.md`。

数值会变化。每次开工前，用 `server_probe.py` 或第 9 节的速查命令现场确认，不要把下面的数字当成永久事实。

## 1. 平台与生命周期

```text
学校 AI 平台（Kubernetes）
  └─ 开发环境 "111" = 一个 Pod：镜像 jr1903:0.0.1（基于 NVIDIA NGC PyTorch 26.05）+ 1 张 RTX 5090
       ├─ /ai/workspace  ← 存储卷 sun（NFS，持久）
       ├─ 容器根盘 /、/root、/tmp（overlay，临时；只有"保存镜像"时才会保留）
       └─ run.sh：sshd:22 → 设置 root 密码 → Jupyter:8888（工作目录 /ai）→ [TensorBoard:6006，仅在设置了 TENSORBOARD_LOG_DIR 时] → sleep infinity
```

1. **创建**：在平台上新建环境，选择镜像，挂载存储卷 sun 到 `/ai/workspace`。
2. **使用**：通过平台 UI（Jupyter / Mlab 终端）或 SSH 进入（平台只对外暴露 22 和 8888 两个端口）。
3. **保存**：在平台上执行"保存镜像"，容器根盘上的改动（例如 `/root` 下的内容）才会保留。
4. **释放**：按 `docs/runbooks/sync-backup-release.md` 的步骤做完收尾，再在平台上释放环境以停止计费。关掉网页不等于释放。

**没有作业调度器**（没有 Slurm、qsub、kubectl）。训练就是在这个容器里直接运行进程，进程的生命周期不会超过容器。

## 2. 访问方式

以下内容原先分散在旧版的 CLAUDE.md、README 和 SYNC 清单里，现集中在这里。

| 项 | 值 |
|---|---|
| 校园 VPN（在管理端 box 上） | `~/.local/bin/cuhksz-vpn-{up,status,down}`；连接不稳定，断了先重启 VPN 再重试 SSH |
| 平台 UI 代理（在 box 上） | `http://127.0.0.1:18080/` |
| SSH | box 上的 `/home/box/.local/bin/aie1903-ssh`，目标 `root@10.27.126.1 -p <动态端口>`（平台把动态端口转发到容器的 22 端口）。密码在私有文件 `aie1903-env.env` 中，**绝不打印** |
| 禁用主机 | **10.27.126.205（研究用 SSH 主机，本课程永不使用）** |
| Cursor | 经 Remote SSH 连到容器，终端就是学校环境。服务端在 `/root/.cursor-server`（临时盘），**客户端断开 300 秒后会自动关闭** |
| Claude Code | 现行做法是跑在 box 上，经 CC Switch 调用模型：`ANTHROPIC_BASE_URL=http://127.0.0.1:15721`，`--model claude-opus-5`。学校环境没有 node 和 claude（见第 8 节） |
| Jupyter | 端口 8888，以 root 运行，工作目录 `/ai`，内核只有系统 Python（看不到 `.venv`） |
| GitHub | 密钥 `/ai/workspace/.ssh/id_ed25519_github`，配置 `/ai/workspace/.ssh/config`；已能以 yixiangsunLeo 身份认证 |

在学校环境里使用 git 时，需要加上 SSH 配置：

```bash
export GIT_SSH_COMMAND="ssh -F /ai/workspace/.ssh/config -o UserKnownHostsFile=/ai/workspace/.ssh/known_hosts"
```

## 3. 计算资源

| 项 | 实测值 | 要点 |
|---|---|---|
| CPU | **cgroup 配额 24 核**；宿主机为 2 颗 AMD EPYC 9534，容器内能看到 256 个逻辑核 | `nproc` 和 `os.cpu_count()` 返回 256，**不能当作可用核数** |
| 默认线程 | torch 128，OpenBLAS 64 | 不设置会过度订阅：torch 默认线程下的矩阵乘只有 24 线程时的 1/3，并被节流 52 秒 |
| 内存 | 上限 32 GiB，没有 swap | 超出会被直接 OOM kill；用 `cat /sys/fs/cgroup/memory.events` 查看 oom 次数 |
| `/dev/shm` | 显示 252G | 占用的内存计入 32 GiB 上限 |
| GPU | 1 张 RTX 5090，32 GiB（可用 31.4 GiB），sm_120，570 W 级别，持久模式开启，Default 计算模式 | GPU 在 NUMA 0；需要绑核时用 `numactl --cpunodebind=0`，而且只在确实有收益时才用 |

查看 CPU 是否被节流：`grep throttled /sys/fs/cgroup/cpu.stat`。`throttled_usec` 增长很快，说明线程开得太多。

## 4. 存储与持久化

| 位置 | 是否持久 | 性能（实测） | 用途 |
|---|---|---|---|
| `/ai/workspace/AIE1903` | **持久**（NFSv3，hard 挂载） | 大文件读写约 1 GB/s；**小文件创建约 1.15 ms/个** | 代码、数据、记录、运行产物、日志、venv |
| `/tmp`、`/root`、`/` | **临时** | 读 5.8 GB/s，小文件 0.05 ms | 只放可以丢的中间文件 |
| `/dev/shm` | 临时（内存） | 写 3.2 GB/s | DataLoader 的共享内存 |

- **不要在 NFS 上写大量小文件**，比如每步一个文件、每样本一个文件。日志要聚合写入；checkpoint 只保留少数几个。
- 以下默认缓存位于临时盘：`/root/.cache/pip`、torch hub、huggingface。本项目暂时不下载预训练权重；以后如果需要，任务卡里要写明缓存位置，例如 `TORCH_HOME` 或 `HF_HOME` 指向 `/ai/workspace/AIE1903/artifacts/cache/`（该目录不进 Git）。
- NFS 是 hard 挂载：存储服务卡住时，进程会一直等待而不是报错。遇到"卡死"时，先用 `stat /ai/workspace` 判断是不是存储的问题，再决定是否结束进程。
- 存储层会在新建的目录里自动生成 `.!!!*` 文件（8 KB 左右，扩展名随机）。忽略它们（`.gitignore` 和 `.cursorignore` 都已写入），**不要单独删除、移动或修改**。删除一个确实不再需要的目录时，它们会随目录一起移除，这是正常的；但不要批量清扫这类文件，也不要清空整块盘。
- 代码、数据、`.git`、`.cursor`、`.claude`、密钥、有价值的运行产物，**只能**放在 `/ai/workspace` 下。

## 5. 网络

- **DNS 偶发失败**：使用 NodeLocal DNSCache，配置 `ndots:5` 并带有 search 域。普通写法 `github.com` 偶尔会解析失败，失败成簇出现，实测失败率在 0% 到 6% 之间；写成 FQDN（`github.com.`）后，400 次查询零失败。
  - 一般处理：**重试**即可。`git push` 和 `ls-remote` 循环 3–4 次，每次间隔 3 秒。
  - 可选的根治办法（需要用户同意后修改 `/ai/workspace/.ssh/config`）：在 `Host github.com` 下设置 `HostName github.com.` 和 `HostKeyAlias github.com`。
  - 不要修改系统 DNS 或网络配置。
- **没有 IPv6 出网能力**。DNS 会对部分域名返回 IPv6 地址，curl 和 Python 会自动回退到 IPv4；个别工具失败时可以加 `-4` 或设置 `AddressFamily inet`。
- **没有代理**。可以访问：GitHub（SSH 和 HTTPS）、api.github.com、PyPI、阿里云镜像 `https://mirrors.aliyun.com/pypi/simple/`（实测最快）、download.pytorch.org、huggingface.co。清华镜像和 hf-mirror 不稳定，kaggle 不通。
- **数据外发规则**：不把原始数据发给外部模型或服务。**wandb 已安装，但不得在线使用**：没有用户授权时，只允许 `WANDB_MODE=disabled` 或 `offline`。

## 6. 软件栈与项目 venv

| 组件 | 版本（实测） |
|---|---|
| 系统 | Ubuntu 24.04.4，内核 5.15，glibc 环境，`LANG=C.UTF-8` |
| CUDA | 13.2.1（nvcc 13.2.78）；驱动 610.43.03（支持 CUDA 13.3）；cuDNN 9.22；NCCL 2.30.4；TensorRT 10.16 |
| Python | 3.12.3（`/usr/bin/python3`） |
| 镜像自带 | torch 2.12.0a0（NV 26.05，支持 sm_120 和 bf16）、torchvision、triton 3.7、flash_attn、transformer_engine、apex、numpy 2.1.0（OpenBLAS）、pandas 3.0.2、scipy 1.17.1、matplotlib 3.10.9、numba 0.64、pyarrow、tensorboard 2.20、wandb 0.26、jupyterlab、psutil、tqdm |
| 缺少 | scikit-learn、statsmodels、xgboost、lightgbm、lightning、optuna、polars、threadpoolctl |
| 工具 | 有：git、curl、wget、jq、unzip、make、gcc、cmake、nvcc、`nohup`、`setsid`、`timeout`、`nice`、`ionice`、`taskset`、`numactl`、`flock`、`watch`、`top`。没有：tmux、screen、htop、nvtop、rsync、zip、lsof、ss、git-lfs、sqlite3 |

**项目 venv**（ADR-0004，2026-10-26 验证）：

```bash
cd /ai/workspace/AIE1903
python3 -m venv --system-site-packages .venv          # 换了镜像或 Python 版本后需要重建
.venv/bin/python -m pip install -e '.[dev]'           # 以可编辑方式安装 aie1903，并安装 pytest 和 ruff
.venv/bin/python -m pytest && .venv/bin/ruff check . && .venv/bin/ruff format --check .
```

**新增依赖的规则**：

- **pip 绝不能替换镜像自带的 torch、torchvision、triton、numpy**。pip 从 PyPI 下载的 torch 可能不支持 sm_120，或与 NGC 的 CUDA 栈不一致。
- 先执行 `.venv/bin/python -m pip install --dry-run <包>`。如果 "Would install" 里出现 torch、torchvision、triton、numpy 等，就停下来，在任务卡里说明并请示。
- 没问题再正式安装，同时更新 `pyproject.toml` 和 `requirements.lock`。可以加 `-i https://mirrors.aliyun.com/pypi/simple/` 提速。
- 不要 `pip install` 到系统 Python，不要用 `sudo`，不要升级 CUDA 或驱动。

**在 Jupyter 中使用 venv**（需要时再做）：`.venv/bin/python -m ipykernel install --user --name aie1903 --display-name "AIE1903 (.venv)"`。注意内核描述文件写在 `/root/.local`，属于临时盘，重建环境后要重新执行。

## 7. 进程与长任务

- **长任务必须脱离终端**：`setsid nohup <命令> > <日志> 2>&1 < /dev/null &`。实测普通 `&` 启动的进程仍属于 Cursor 会话，Cursor 断开 300 秒后服务端自动关闭时可能被一起结束；SSH 断线同理。完整模板见 `training.md`。
- **任何进程都活不过环境释放**。释放之前，必须确认任务已经结束，并且记录已经落盘。
- 查看进程：`ps -eo pid,etime,pcpu,rss,cmd --sort=-pcpu | head`。查看 GPU：`nvidia-smi`，或 `nvidia-smi dmon -s pucm -d 5`（按功耗、利用率、显存采样）。
- 结束进程：先 `kill <pid>`（发送 SIGTERM），等待 30 秒，再考虑 `kill -9`。**只结束自己启动、并且记录在 run.json 中的进程**。
- PID 1 是 `run.sh`（bash）。已经退出的后台进程短时间内可能显示为 `<defunct>`，这是无害的。

## 8. Claude Code 与 Grokbot 的运行模式（待学生决定）

| 模式 | 做法 | 优点 | 代价 |
|---|---|---|---|
| A（现行） | Claude Code 在 box 上，通过 `aie1903-ssh` 在学校环境执行命令和编辑文件 | 不用在学校环境装软件 | Claude 读不到学校工作树里的规则，除非 box 上也有一个同步的克隆；文件编辑绕道 ssh，容易出错 |
| B（推荐） | box 先用 `ssh -R 15721:127.0.0.1:15721` 登录学校环境，再在学校环境运行 Claude Code，把 node 和 claude 装在 `/ai/workspace/tools/`（持久、用户态） | 只有一个工作树，CLAUDE.md、规则和 hooks 都直接生效 | 需要一次安装，并要学生授权在 `.venv` 之外装软件 |

在模式 A 下，如果要让 Claude Code 加载项目规则，box 上必须有本仓库的克隆作为工作目录，并在每次开工前执行 `git pull --ff-only`；同时严格遵守单写入者规则（git-workflow §7）。

## 9. 速查与排障

```bash
grep -E 'nr_throttled|throttled_usec' /sys/fs/cgroup/cpu.stat      # CPU 是否被节流
cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.events      # 内存用量与 OOM 次数
nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv     # GPU 占用
nvidia-smi --query-compute-apps=pid,used_memory --format=csv        # 谁在用 GPU
df -h /ai/workspace / && du -sh /ai/workspace/AIE1903/runs           # 磁盘
.venv/bin/python reports/audit/A-20261026-server/server_probe.py     # 完整复测（约 20 秒）
```

| 现象 | 可能原因 | 处理 |
|---|---|---|
| `Could not resolve hostname github.com` | DNS 偶发失败 | 重试；或者在征得同意后改用 FQDN（第 5 节） |
| CPU 任务比预期慢很多，`throttled_usec` 猛增 | 线程数超过了 24 核配额 | 按 `configs/runtime.yaml` 设置线程环境变量 |
| 进程突然消失，`memory.events` 里的 oom 增加 | 超出 32 GiB 内存 | 减小批大小或数据规模，并在 run.json 中记录 |
| CPU 与 GPU 的结果对不上 | GPU 默认使用 TF32 | 按 training.md §3 显式设置精度 |
| Cursor 断线后任务没了 | 任务没有用 `setsid nohup` 启动 | 按 training.md 的模板重新启动，并把这次中断记录到 run.json |
