# Git 工作流

## 1. 仓库与远端

- 唯一工作树：学校持久盘上的 `/ai/workspace/AIE1903`，存储卷 sun。
- 远端：`origin` 为 `git@github.com:yixiangsunLeo/AIE1903.git`，走 SSH，使用 `/ai/workspace/.ssh/config`；`github-https` 是只读备用。
- 课程要求每组一个**私有**仓库 [STARTER]，目前仓库是公开的，由学生决定是否修改（见 current-status）。

## 2. 分支

| 分支 | 用途 | 规则 |
|---|---|---|
| `main` | 稳定基线 | 只接收来自 `task/*` 的合并，紧急修复也要先开任务。唯一例外：只改动 `docs/worklog/` 或 `docs/current-status.md` 的记录追加（类型为 `docs(records)`，比如推送后的核对记录）可以直接提交 |
| `task/<task_id>-<slug>` | 一个任务 | 从最新的 `main` 拉出；合并后删除 |
| `exp/<task_id>-<slug>` | 探索性实验 | 可以不合并，但运行记录必须保留 |

合并时用 `git merge --no-ff task/...`，在合并提交里写任务摘要；也可以走 GitHub PR，课程推荐由组员审核。

## 3. 提交信息

格式如下：

```text
<type>(<scope>): <summary，不超过 72 个字符，建议英文>

正文：为什么改、改了什么、如何验证（命令 + 结果）。

Task: T-YYYYMMDD-NN          # 必需；只修错别字级别的改动可写 Task: trivial
Actor: cursor/<model>        # 必需；也可以是 claude-code/<model>、grokbot+claude-code/<model>、human/<name>
Co-authored-by: ...          # 可选
```

- **type**：`feat`、`fix`、`refactor`、`perf`、`test`、`docs`、`chore`、`build`、`exp`（实验记录）、`data`（数据清单或审计）、`revert`。
- **scope**：功能区名（config、data、splits、features、models、evaluation、tracking、pipelines、viz、cli），或者 `configs`、`rules`、`records`、`env`、`repo`。
- Git 作者统一是学生账号，所以**真实执行者写在 `Actor:` 尾注里**，用来如实区分 AI 与人的贡献。
- 一个提交只做一件完整的事；不要把格式化和逻辑修改混在一起。

## 4. Hooks（`.githooks/`，必须启用）

每个克隆都要执行一次启用命令（学校环境已经启用）：

```bash
git config core.hooksPath .githooks
git config commit.template .gitmessage
```

| hook | 检查内容 |
|---|---|
| `commit-msg` | 标题格式、长度不超过 72 个字符、是否有 `Task:` 和 `Actor:` 尾注（Merge 和 Revert 开头的提交放行） |
| `pre-commit` | 是否混入原始数据或中间数据、runs/、submissions 的 CSV、模型权重、.env、私钥、单个超过 2 MB 的文件、NFS 垃圾文件 `.!!!*`，以及常见的令牌格式 |

不要用 `--no-verify` 绕过。确实需要时，在任务卡里写明原因，并说明事后怎么修复。

## 5. 永远不进 Git 的内容

- `data/raw/**`、`data/interim/*`、`data/processed/*`。原始数据用 `data/checksums.sha256` 校验，按 `data/README.md` 从官方仓库获取。
- `runs/`（README 除外）、`submissions/**/*.csv`、`artifacts/models/*`、`logs/`、`backups/`。
- `.env`、私钥、令牌、`.ssh/`、`.agent-lock`、`.venv/`、各种缓存。
- 注意：`.gitignore` 只能防止新文件入库，**已经在历史里的文件不会因此消失**。历史中曾有原始数据（见 project-context §6），已如实记录，没有改写历史。

## 6. 推送与标签

- **推送需要授权**：用户在本会话中明确要求，或者 `docs/current-status.md` 中记有常设授权。
- 禁止 force push，禁止改写已推送的历史，禁止删除远端标签。
- 版本标签用 `vX.Y.Z`（附注标签）：
  - 框架层变更升 minor；
  - 里程碑完成时打标签，例如 M1–M7 全部完成时打 `v0.3.0`。
- 归档标签用 `archive/<name>`。当前已有 `archive/legacy-scaffold`，保存重建前的旧代码。
- 推送后用 `git ls-remote origin` 确认远端与本地 HEAD 一致，并把结果记进 worklog。

## 7. 学校环境与管理端 box 之间的同步

- 同一时刻只有一个写入者（通过 `.agent-lock` 协调）。
- 如果在 box 上用克隆开发：先在 box 上提交并推送到 GitHub，再在学校环境执行 `git pull --ff-only`；反过来同理。不要两边同时改同一个分支。
- 不要用 scp 覆盖受 Git 跟踪的文件，否则会制造无法追溯的改动。
