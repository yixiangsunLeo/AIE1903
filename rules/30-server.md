---
description: 学校服务器的事实、资源上限、持久化、网络、软件与进程规则（全局，始终加载）
alwaysApply: true
---

# 服务器规则

详细手册见 docs/runbooks/environment.md。依据是 reports/audit/A-20261026-server/ 的实测结果（2026-10-26）；开工时用 `server_probe.py` 复测，数值以复测为准。

**这台机器是什么**
- 学校 AI 平台上的一个 Kubernetes Pod：环境 111，镜像 jr1903:0.0.1（基于 NVIDIA NGC PyTorch 26.05），以 root 运行。
- 没有作业调度器，训练就是在容器里直接跑进程。
- 平台只对外暴露 SSH（22）和 Jupyter（8888）。Cursor 经 Remote SSH 连接；客户端断开 300 秒后，Cursor 服务端会自动关闭。

**资源上限（硬约束）**
- **CPU 配额只有 24 核。** `os.cpu_count()` 返回的 256 是宿主机的数字，不可信。torch 默认开 128 线程、OpenBLAS 默认开 64 线程，都会过度订阅：实测慢 30% 到 3 倍，并被 cgroup 节流。所以每次运行都要显式设置线程数，默认 8，不超过 24。
- **内存 32 GiB，没有 swap**，超出会被直接 OOM kill。`/dev/shm` 的占用也计入这个上限。
- **GPU 只有 1 张 RTX 5090**（可用 31.4 GiB，sm_120）。同一时间只跑一个 GPU 作业。

**持久化**
- 只有 /ai/workspace（NFS）是持久的。`/`、`/root`、`/tmp`、`/root/.cache`、Cursor 服务端和 Cursor 会话记录都在临时盘上，环境一释放就会丢失。
- NFS 上大文件读写约 1 GB/s，但小文件创建约 1 ms 一个。日志要聚合写入，checkpoint 只保留少数几个；禁止每步或每个样本写一个文件。
- `.!!!*` 是存储层生成的文件：忽略它们，不要单独删除或修改。

**网络**
- DNS 偶尔解析失败（github.com 实测失败率 0% 到 6%）。网络操作重试 3–4 次即可，不要改系统 DNS。
- 没有 IPv6 出网能力，也没有代理。PyPI、阿里云镜像、download.pytorch.org、huggingface.co 都可以访问。
- 不把原始数据发给任何外部服务。wandb 只能设为 disabled 或 offline。

**软件**
- 只用项目 .venv（带 --system-site-packages）。pip 不得替换镜像自带的 torch、torchvision、triton、numpy：安装前先用 `pip install --dry-run` 检查。新增依赖要同步更新 pyproject.toml 和 requirements.lock。
- 不改系统 Python、CUDA、驱动或全局配置；不用 sudo。

**进程**
- 长任务必须用 `setsid nohup … &` 启动，并记录 PID（模板见 docs/runbooks/training.md §4）。任何进程都活不过环境释放。
- 不结束归属不明的进程。释放环境前，按 docs/runbooks/sync-backup-release.md 收尾。
- 不打印全部环境变量，环境里有 root 密码和 Jupyter 口令；也不打印任何密钥或口令。
