# 运行手册：同步、备份与释放环境

## 1. 每批工作之后

```bash
cd /ai/workspace/AIE1903
sync                                   # 刷新 NFS 写缓存
git status                             # 确认改动符合预期，没有数据或秘密
.venv/bin/python -m pytest && .venv/bin/ruff check .
git add -A && git commit               # 提交信息格式见 git-workflow；hooks 会自动检查
```

如果已获授权，再推送：

```bash
export GIT_SSH_COMMAND="ssh -F /ai/workspace/.ssh/config -o UserKnownHostsFile=/ai/workspace/.ssh/known_hosts"
git push origin main --follow-tags     # 或推送 task 分支
git ls-remote origin                   # 确认远端与本地 HEAD 一致，结果写进 worklog
```

## 2. 备份执行记录

受 Git 跟踪的记录（任务卡、worklog、CHANGELOG、审计、运行摘要、实验索引）**推送到 GitHub 就完成了备份**。不受 Git 跟踪的部分按下面的方式处理：

```bash
cd /ai/workspace/AIE1903
mkdir -p backups logs/agent-sessions/cursor

# Cursor 会话记录位于容器盘 /root，环境释放后就会丢失，所以要复制到持久盘（不进 Git，可能含私密对话）
src=/root/.cursor/projects/ai-workspace-AIE1903/agent-transcripts
[ -d "$src" ] && cp -a "$src/." logs/agent-sessions/cursor/

# 对完整运行产物和日志做快照，并生成校验值
stamp=$(date +%Y%m%d-%H%M%S)
tar -czf "backups/records-$stamp.tar.gz" runs logs 2>/dev/null || true
( cd backups && sha256sum "records-$stamp.tar.gz" >> SHA256SUMS && sha256sum -c SHA256SUMS )
```

- `backups/` 和 `logs/` 都不进 Git。快照和原件在同一个存储卷上，**只能防误删，防不了存储卷丢失**。
- 需要异地备份时，由学生决定存放位置，不要放进公开仓库。

## 3. 释放环境之前（必须按顺序完成）

1. **确认没有在跑的任务**：`ps -eo pid,etime,cmd`、`nvidia-smi`，以及 `runs/*/run.json` 中没有 `running`。别人的作业不能动。
2. **提交并同步**：完成第 1 节。暂时不推送的，要在 worklog 中写明原因并得到学生同意。
3. **备份**：完成第 2 节。
4. **保存镜像**：在平台上执行"保存镜像"，在 worklog 里记下镜像名和时间。
5. **校验持久盘**：`sync`，并执行 `(cd data && sha256sum -c checksums.sha256)`。
6. **删除** `.agent-lock`，在 worklog 记一条"释放前检查完成"。
7. 以上都完成后，才在平台上**释放**环境 `111`，停止计费。关掉网页不等于释放。

## 4. 重建环境之后

```bash
cd /ai/workspace/AIE1903 && git status && git log --oneline -3
(cd data && sha256sum -c checksums.sha256)
git config --get core.hooksPath        # 应输出 .githooks（这项配置在 .git/config 里，持久保存）
.venv/bin/python -m pytest             # 如果 .venv 失效（比如换了镜像），按 environment.md §6 重建
```
