---
description: 代码功能区边界、依赖方向与编码规范
globs: src/**/*.py,tests/**/*.py,scripts/**,notebooks/**
paths: src/**/*.py,tests/**/*.py,scripts/**,notebooks/**
alwaysApply: false
---

# 代码结构规则

依据：docs/architecture.md（功能区与接口草案）、docs/standards/coding.md（写法）。

**功能区与允许的内部依赖**（src/aie1903/）
- config：无内部依赖
- data：config
- splits：config
- features：config、data、splits
- models：config、data、features（**不能导入 evaluation**）
- evaluation：config、data（**不能导入 models**）
- tracking：config
- pipelines：以上全部
- viz：config、data、evaluation
- cli.py（计划）：pipelines、data、evaluation、tracking

禁止反向依赖和循环导入；不新建 utils、common 这类杂物间。新模块先在 docs/architecture.md 登记职责，再写代码；接口有变化时，同步更新 architecture.md §4。

**写法**
- Python ≥3.11；加类型标注；docstring 用英文，写清形状、单位和时间语义。用 ruff 做检查和格式化。
- 不硬编码绝对路径。项目根由 config 查找；用环境变量 AIE1903_* 覆盖时要记录。
- 尽量写纯函数；IO 只放在 data、tracking、pipelines。
- 按 pandas 3.x（Copy-on-Write）的语义写；数组用 float64、形状 [T, N]；时间戳保持 naive。
- 每个功能实现都配套测试，放在 tests/<area>/；泄漏测试放在 tests/leakage/；依赖真实数据的测试放在 tests/contract/（数据缺失时 skip）。
- scripts/ 只放薄封装和运维脚本。notebooks/ 只做探索，不承载唯一逻辑，提交前清空输出。
