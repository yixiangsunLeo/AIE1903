# 当前状态

这是项目状态的单一事实来源，每个任务收尾时更新。

更新：2026-10-26 · T-20261026-02 · cursor/claude-opus-5.5

## 一句话

框架 v0.2.1 已搭好，服务器已全面摸底，规则改为以 `rules/` 为唯一源、所有代理都能读完。目前还没有功能代码，也没有训练。下一步是 roadmap 的 **M1 数据层**。

## 赛道、数据与协议

- **赛道**：主线 cell_217；演练 cell_30；扩展 grid_273（主线完成之后）。
- **数据**：三个数据集共 13 个官方文件齐全，与官方提交 `49822d8` 逐字节一致；校验文件是 `data/checksums.sha256`；审计见 `reports/audit/A-20261026-framework/`。
- **验证协议**：expanding_289_v1（ADR-0002，暂行采用，待学生复核）。heldout 为 **untouched**。
- **指标口径**：provisional-v1（ADR-0003，暂行采用，待学生复核）。
- **数据使用规则**：一个运行只用一个数据集；任何 sample 数值都不得读取（ADR-0005）。

## 服务器与环境（审计 A-20261026-server；规则 30、35）

- **平台**：学校平台上的 Kubernetes Pod，镜像基于 NGC PyTorch 26.05，没有作业调度器。对外只暴露 SSH:22 和 Jupyter:8888。Cursor 断开 300 秒后，服务端会自动关闭。
- **资源**：CPU 配额 **24 核**（不是 256）；32 GiB 内存、没有 swap；1 张 RTX 5090（31.4 GiB，sm_120）。torch 默认开 128 线程，必须显式设置线程数。
- **训练栈已验证**：用随机数据跑小 LSTM，GPU 严格 FP32 每步 2.4 ms，CPU 8 线程每步 112 ms；确定性设置下结果逐位一致；`torch.compile` 可用。默认 TF32 会改变结果，所以默认精度设为 `fp32_strict`。
- **持久化**：只有 `/ai/workspace` 是持久的。NFS 大文件约 1 GB/s，小文件约 1 ms 一个。
- **网络**：DNS 偶发解析失败（重试即可）；没有 IPv6；PyPI、阿里云镜像、huggingface 可以访问。
- **项目 venv**：`.venv`（system-site-packages，pytest 9.1.1，ruff 0.17.2）。Git hooks 已启用，提交模板为 `.gitmessage`。

## 已验证的命令

```bash
cd /ai/workspace/AIE1903
(cd data && sha256sum -c checksums.sha256)                        # 13/13 OK
.venv/bin/python -m pytest                                        # 19 passed
.venv/bin/ruff check . && .venv/bin/ruff format --check .         # 通过
.venv/bin/python scripts/check-framework.py                       # 框架完整性检查，175/175
scripts/sync-rules.sh --check                                     # 规则副本与唯一源一致
python3 reports/audit/A-20261026-framework/audit_probe.py         # 数据审计，132 PASS / 0 FAIL
.venv/bin/python reports/audit/A-20261026-server/server_probe.py  # 服务器事实复测（约 20 秒，只读）
.venv/bin/python reports/audit/A-20261026-server/train_smoke.py   # 训练栈冒烟（随机数据，约 11 秒，占用 GPU）
```

## 写入者与授权

- 当前写入者：无（T-20261026-02 结束时已释放 `.agent-lock`）。
- GitHub 推送：**没有常设推送授权**，每次推送都要确认。T-20261026-02 是否推送，见任务卡。
- 仓库可见性：**公开**，与课程"每组一个私有仓库"的要求不符，由学生处理（Q3）。
- 已知问题：学校环境解析 github.com 偶尔失败，重试即可。可选的根治办法是改用 FQDN，需要用户同意（environment.md §5）。

## 最近的任务与运行

| task_id | 状态 | 摘要 |
|---|---|---|
| T-20261026-01 | completed | 框架重建（v0.2.0） |
| T-20261026-02 | completed | 服务器摸底；规则改为唯一源、多代理通用；补充训练手册 |

- 正式运行：无。环境冒烟测试只作为审计证据，不算项目运行。
- legacy 记录：`reports/legacy/`（cell_30 的旧协议回测，未验证）。

## 阻塞与待决事项（详见 docs/sources-and-open-questions.md）

1. **Q3 仓库可见性**：在 GitHub 的 Settings 中改为 Private，并添加课程人员与组员。
2. **Q5 Claude Code 与 Grokbot 的运行模式**：待学生决定，推荐模式 B（environment.md §8）。
3. **Q4 sample 末行疑似含真值**：是否反馈给课程方，由学生决定。
4. **Q6 团队信息**：组员名单和分工待填（README）。
5. **待复核**：ADR-0002、ADR-0003、ADR-0006 待学生确认。
6. **规则加载**：需要在新的 Cursor 会话和真实的 Claude Code 会话中各验证一次（方法见任务卡 T-20261026-02）。
7. **Q9 平台计费、机时上限与自动回收**：在容器内无法确认，以平台页面为准。

已解决：`.cursorignore` 已创建；项目外的 4 个暂存件已删除（Q8）。

## 下一步（可以直接开工）

1. 按 `docs/roadmap.md` 的 M1 建任务卡 `T-YYYYMMDD-01-data-layer`。实现 `aie1903.config`（项目根查找、配置加载与哈希；读取 `configs/runtime.yaml` 中的线程、精度和确定性设置）和 `aie1903.data`（`load_train`、`load_test_template`、合同校验、checksum 校验），并写 `tests/contract/` 的合同测试。验收标准：在三个数据集上复现 A-20261026-framework 的结论。
2. 之后依次做 M2（指标）→ M3（切分与守卫）→ M4（运行记录：按 training.md 的模板落实 setsid、timeout 和资源记录）→ M5（基线回测：先 cell_30，再 cell_217）。
