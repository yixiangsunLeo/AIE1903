# 运行手册：环境、访问与项目 venv

## 1. 学校平台与访问

以下内容原先分散在旧版的 CLAUDE.md、README 和 SYNC 清单里，现集中在这里。

| 项 | 值 |
|---|---|
| 开发环境 | 环境名 `111`；镜像 `jr1903:0.0.1`（旧 README 写作 `jr/jr1903`，以平台显示为准）；把存储卷 **sun** 挂载到 `/ai/workspace` |
| 项目根 | `/ai/workspace/AIE1903`（唯一的持久工作树） |
| 校园 VPN（在管理端 box 上） | `~/.local/bin/cuhksz-vpn-{up,status,down}`；连接不稳定，断了就先重启 VPN 再重试 SSH |
| 平台 UI 代理（在 box 上） | `http://127.0.0.1:18080/` |
| SSH | box 上的 `/home/box/.local/bin/aie1903-ssh`，目标 `root@10.27.126.1 -p <动态端口>`。密码在私有文件 `aie1903-env.env` 里，**绝不打印** |
| 禁用主机 | **10.27.126.205（研究用 SSH 主机，本课程永不使用）** |
| GitHub SSH | 密钥 `/ai/workspace/.ssh/id_ed25519_github`，配置 `/ai/workspace/.ssh/config`。2026-10-26 实测已能以 yixiangsunLeo 身份认证 |
| Cursor | 经 Remote SSH 直接连到学校环境，终端就是学校环境 |
| Claude Code | 跑在 box 上，经 CC Switch 调用模型：`ANTHROPIC_BASE_URL=http://127.0.0.1:15721`，推荐 `--model claude-opus-5`（由 CC Switch 映射）。学校环境**没有** node 和 claude |

在学校环境里使用 git 时，需要加上 SSH 配置：

```bash
export GIT_SSH_COMMAND="ssh -F /ai/workspace/.ssh/config -o UserKnownHostsFile=/ai/workspace/.ssh/known_hosts"
```

## 2. 实测环境（2026-10-26，证据：reports/audit/A-20261026-framework/environment.json）

| 项 | 实测值 | 说明 |
|---|---|---|
| OS | Ubuntu 24.04.4 LTS | 容器 |
| CPU | cgroup 配额 **24 核** | `nproc` 和 `os.cpu_count()` 显示的 256 是宿主机的值，不能当可用核数 |
| 内存 | cgroup 上限 **32 GiB**，无 swap | |
| GPU | NVIDIA GeForce RTX 5090，32 GiB，驱动 610.43.03 | torch 2.12.0a0（NV 26.05），CUDA 13.2 可用 |
| Python | 3.12.3（`/usr/bin/python3`） | 镜像自带 numpy 2.1.0、pandas 3.0.2、scipy 1.17.1、matplotlib 3.10.9、PyYAML 6.0.1、jupyterlab |
| 缺少 | pytest、ruff、scikit-learn、statsmodels | pytest 和 ruff 已装进项目 `.venv`；其余由需要它们的任务再安装 |
| pip | 通过环境变量设置了 `PIP_CONSTRAINT=/etc/pip/constraint.txt`、`PIP_BREAK_SYSTEM_PACKAGES=1` | 在 `.venv` 中同样生效 |
| 时区 | `/etc/localtime` 为 Asia/Shanghai（+08:00） | 只影响日志时间，与数据时钟无关 |
| 持久盘 | `/ai/workspace`（NFS，248T 空间） | 其他路径（`/root`、`/tmp`、`/workspace`）随环境释放而消失 |

可用余量会变化，每次开工时以现场探测为准，不要把上表当成永久事实。

## 3. 项目 venv（已于 2026-10-26 验证）

为什么这样建 venv，见 ADR-0004：复用镜像里的 numpy、pandas、torch，不碰系统 Python。

```bash
cd /ai/workspace/AIE1903
python3 -m venv --system-site-packages .venv          # 换了镜像或 Python 版本后需要重建
.venv/bin/python -m pip install -e '.[dev]'           # 以可编辑方式安装 aie1903，并安装 pytest 和 ruff
.venv/bin/python -m pytest                            # 框架冒烟测试
.venv/bin/ruff check . && .venv/bin/ruff format --check .
```

- 依赖的唯一来源是 `pyproject.toml`；实际验证过的版本记在 `requirements.lock`，增删依赖时要同步更新。
- 不要 `pip install` 到系统 Python，不要 `sudo`，不要升级 CUDA 或 torch。

## 4. Claude Code 与 Grokbot 的运行模式（待学生决定）

| 模式 | 做法 | 优点 | 代价 |
|---|---|---|---|
| A（现行） | Claude Code 在 box 上，通过 `aie1903-ssh` 在学校环境执行命令和编辑文件 | 不用在学校环境装软件 | Claude 读不到学校工作树里的 CLAUDE.md 和规则，除非 box 上也有一个同步的克隆；文件编辑绕道 ssh，容易出错 |
| B（推荐） | box 先用 `ssh -R 15721:127.0.0.1:15721` 登录学校环境，再在学校环境运行 Claude Code，把 node 和 claude 装在 `/ai/workspace/tools/`（持久、用户态） | 只有一个工作树，CLAUDE.md、规则和 hooks 都直接生效 | 需要一次安装，并要学生授权在 `.venv` 之外装软件 |

在模式 A 下，如果要让 Claude Code 加载项目指令，box 上必须有本仓库的克隆作为工作目录，并在每次开工前执行 `git pull --ff-only`；同时严格遵守单写入者规则（git-workflow §7）。

## 5. 持久化与 NFS

- 代码、数据、`.git`、`.cursor`、`.claude`、密钥、有价值的运行产物，**只能**放在 `/ai/workspace` 下。
- 存储层会在新建的目录里自动生成 `.!!!*` 文件（8 KB 左右，扩展名随机）。忽略它们（`.gitignore` 已写入，`.cursorignore` 的拟定内容里也有），**不要删除、移动或修改**，也不要批量删除整个目录。
- 不清空整块存储盘；工作只在 `AIE1903/` 内进行。
