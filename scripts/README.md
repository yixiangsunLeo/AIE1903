# scripts/

这里只放两类文件：

- 包装 `aie1903` 功能的**薄入口**（不含业务逻辑）；
- **运维脚本**，例如环境重建、备份。

所有预测相关的功能都通过统一 CLI 提供：`python -m aie1903.cli <command>`（计划在 roadmap M7 实现）。

当前为空。v0.2.0 之前的 7 个重复入口已移除，保留在标签 `archive/legacy-scaffold` 中。

规则：

- 脚本不硬编码路径和参数，一律从配置读取；
- 脚本的产物遵守运行记录规范（`docs/standards/records.md`）。
