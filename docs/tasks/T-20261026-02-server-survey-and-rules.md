# T-20261026-02 服务器摸底，并让规则所有代理都能读

- task_id：T-20261026-02
- 状态：completed（推送是否进行，见"收尾与交接"）
- 执行者：cursor/claude-opus-5.5（Cursor 经 Remote SSH 连到学校环境）
- 工作区与分支：/ai/workspace/AIE1903 · task/T-20261026-02-server-survey-and-rules
- 开始时间与基准提交：2026-10-26 22:22 +08:00 · ad04b79（origin/main）
- 关联：审计 A-20261026-server；ADR-0006

## 目标与范围

- **目标**（用户原话）："把你本机服务器的情况摸清楚，包括怎么运作，怎么训练等等，摸清楚然后写入规则里面，以后所有规则必须是 cursor 以及 claude 或者其他 agent 都能通读的。"
- **本轮做**：
  - 只读摸底；
  - 有上限的性能基准；
  - 用随机数据做训练栈冒烟测试；
  - 写服务器手册和训练手册；
  - 新增或重写服务器、训练规则；
  - 把规则改为唯一源、多代理通用，并用 hook 和检查脚本强制执行。
- **本轮不做**：项目功能代码、项目数据上的训练、修改系统或网络配置、修改项目外的 SSH 配置（只作为建议，见 Q10）。

## 依赖与授权

- **GPU 冒烟测试的依据**：用户要求"摸清楚怎么训练"，所以做了一次有上限的验证：不超过 60 秒、显存不超过 2 GiB、只用随机数据。实际 12.6 秒，峰值显存 400 MiB。
- **推送**：本任务开始时没有推送授权，结束时请示。22:43 用户通过提问表单授权两件事：
  1. 合并到 main、打标签 v0.2.1 并推送；
  2. 修改 `/ai/workspace/.ssh/config`，改用 FQDN（Q10）。

## 预算

- 每个探测脚本 1 分钟以内，GPU 冒烟测试不超过 60 秒；
- 性能基准写入 NFS 和 /tmp 的临时数据各 256 MiB，测完即删。

## 预先验收标准

1. 服务器事实有可复现的证据：脚本加 JSON，环境变量只记录白名单中的值，不读取任何秘密。
2. "怎么运作"和"怎么训练"都写成了手册：environment.md 和 training.md。
3. 关键事实写进了全局规则 30 和 35，并有对应证据。
4. 所有规则以 `rules/` 为唯一源，Cursor、Claude Code 和其他代理都能读到；hook 会拦下不一致的提交。
5. 框架检查、pytest、ruff、规则同步检查全部通过；记录同步更新。

## 实际改动

| 范围 | 改了什么 |
|---|---|
| 审计 | 新增 `reports/audit/A-20261026-server/`：`server_probe.py`、`perf_probe.py`、`train_smoke.py` 和它们输出的 JSON，`framework-check.json`，以及 README |
| 手册 | `docs/runbooks/environment.md` 扩写为完整的服务器手册（平台生命周期、访问、资源、存储、网络、软件栈、进程、运行模式、排障）；新增 `docs/runbooks/training.md`（开跑前检查、环境变量、精度与确定性、启动模板、监控、中断与恢复、GPU 原则、记录、收尾） |
| 规则 | 新建 `rules/` 作为唯一源。00、10、20、30、40 从 `.cursor/rules/` 移入（用 git mv 保留历史）：00 精简并加入规则维护规定，30 重写为实测事实；新增 `35-training.md` 和 `rules/README.md` |
| 适配 | 新增 `scripts/sync-rules.sh`，生成 `.cursor/rules/*.mdc`（真实副本）和 `05-soul.mdc`（来自 SOUL.md），以及 `.claude/rules/*.md`（6 个符号链接） |
| 强制 | `.githooks/pre-commit` 增加规则一致性检查；新增 `scripts/check-framework.py`（175 项检查，取代旧的 `framework_check.py`） |
| 入口 | AGENTS.md 新增"规则"一节和"服务器与训练要点"；CLAUDE.md、README、docs/README、grokbot.md、agent-contract.md、git-workflow.md 同步更新 |
| 配置 | `configs/runtime.yaml` 升到 schema v2：新增 max_threads 24、precision fp32_strict、deterministic、env 默认值、gpu_index |
| 决策与记录 | 新增 ADR-0006；更新 current-status、sources-and-open-questions（Q9、Q10）、CHANGELOG、worklog、ai-use-log、任务索引；版本升到 0.2.1；修正 environment.md 章节号变化带来的引用 |

## 真实验证

| 命令或检查 | 退出码 | 结果 |
|---|---|---|
| `server_probe.py` | 0 | 19.4 秒，各部分都没有报错；见 `server-facts.json` |
| `perf_probe.py` | 0 | 14.3 秒。numpy：24 线程 995 GFLOPS，默认 711（被节流 10.6 秒）。torch：24 线程 993，默认 128 线程只有 330（被节流 51.8 秒）。NFS：写 1019 MiB/s、读 1.1 GB/s、小文件 1.15 ms |
| `train_smoke.py` | 0 | 12.6 秒。CPU 每步 112.5 ms；GPU FP32 每步 2.41 ms；TF32 每步 2.38 ms（结果不同）；bf16 每步 1.99 ms。确定性逐位一致；`torch.compile` 可用；峰值显存 400 MiB；结束后显存释放 |
| TF32 实测 | 0 | 默认相对误差 2.9e-4；`set_float32_matmul_precision("highest")` 后为 3.7e-7 |
| DNS 实测 | — | github.com：50 次失败 3 次、400 次失败 1 次；`github.com.`（FQDN）：400 次失败 0 次；ssh 5 次全部成功 |
| 进程实测 | — | 普通 `&` 启动的进程仍属于 Cursor 会话；`setsid nohup` 启动的进程有独立会话，父进程为 1 |
| `scripts/sync-rules.sh --check` | 同步前 1，同步后 0；篡改副本后 1 | 符合预期 |
| pre-commit 规则检查（临时仓库，5 种情况） | 1、1、0、1、0 | 没同步、没暂存、漏暂存生成文件都被拦；完整同步并暂存后放行 |
| `scripts/check-framework.py` | 0 | 175/175 |
| `.venv/bin/python -m pytest` | 0 | 19 passed（版本已同步为 0.2.1） |
| `ruff check` 和 `ruff format --check` | 0 | 通过；新脚本修正了行长和 B905 |
| SSH 改用 FQDN（已授权）：先备份为 `config.bak-20261026`，再执行 `ssh -G` 和 5 次 BatchMode 的 `ssh -T` | 0 | 生效后 hostname 为 `github.com.`、hostkeyalias 为 `github.com`；5/5 认证成功，没有出现主机密钥提示 |
| 合并到 main、打标签 v0.2.1、推送 `main` 和 `v0.2.1`，再执行 `git ls-remote` | 0（第 3 次尝试成功） | 远端 main 与 `v0.2.1^{}` 都是 2609a3f，与本地一致。**前两次尝试使用 FQDN 配置，仍然报 "Could not resolve hostname github.com."** |
| 结论修正与回滚 | 0 | FQDN 不能防止解析失败（假设被证伪）。用备份恢复了原 SSH 配置（逐字节一致），并删除备份。恢复后认证 3 次：第 1 次解析失败，第 2、3 次成功，说明失败与写法无关 |

**规则加载的实测**：读取 `scripts/check-framework.py` 时，Cursor 自动附加了 `30-server` 和 `40-code-structure` 两条规则，说明 globs 会触发加载；但附加的是会话开始时缓存的**旧版**内容。结合 T-20261026-01 中子代理的实测，可以确认：**新规则必须在新会话中才会生效**。

**未验证**：

- 新的 Cursor 会话是否加载了新规则；
- Claude Code 是否加载了 `.claude/rules` 的符号链接。

验证方法：新开会话后，在不读文件的前提下提问："CPU 线程上限是多少？长任务怎么启动？GPU 默认精度有什么问题？规则的唯一源在哪里？" 预期答案依次是：24；`setsid nohup` 并记录 PID；TF32，默认改为 fp32_strict；`rules/`。Claude Code 再运行 `/context`，确认能看到 `.claude/rules` 中的全局规则。

## 收尾与交接

- **结果**：验收标准 1–5 全部满足。
- **回退办法**：`git revert -m 1 <本任务的合并提交>`。规则回到 `.cursor/rules/` 为源的旧结构，可以参考 v0.2.0。
- **已由用户决定并完成**：合并、打标签 v0.2.1 并推送。
- **SSH 改用 FQDN（Q10）**：按授权应用后，推送时证实无效，已恢复原配置。现在 `/ai/workspace/.ssh/config` 与任务开始前完全相同。
- **待用户处理的事项**：
  1. 复核 ADR-0006；
  2. 新开一个 Cursor 会话，验证规则加载。
- **下一步**：M1 数据层（见 current-status）。
- **记录同步**：CHANGELOG [x] · current-status [x] · worklog [x] · ai-use-log [x] · experiments.csv（无运行，不涉及）。
- **人工复核**：pending。
