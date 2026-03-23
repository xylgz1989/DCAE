# DCAE 独立部署指南

> DCAE (Design-Code-Analyze-Evolve) 框架现已完全独立于 OpenClaw，可通过多种方式直接使用

**版本**: 1.0.0  
**最后更新**: 2026-03-22

---

## 目录

1. [架构概览](#架构概览)
2. [核心场景（不需要 OpenClaw）](#核心场景不需要-openclaw)
3. [可选场景（需要 OpenClaw）](#可选场景需要-openclaw)
4. [安装指南](#安装指南)
5. [Claude Code 配置](#claude-code-配置)
6. [调用示例](#调用示例)
7. [故障排查](#故障排查)

---

## 架构概览

### 设计原则

DCAE 框架设计为**独立可运行的 TDD 框架**：

- ✅ **自包含**: 有独立的 Python 实现
- ✅ **多入口**: 提供 MCP Server、CLI、Python 模块三种调用方式
- ✅ **无依赖**: 不依赖 OpenClaw Runtime 即可运行

### 包结构

```
dcae-core/          # 核心框架包 (pip install dcae)
├── dcae/
│   ├── core.py     # DCAE 核心逻辑
│   ├── cli.py      # 命令行接口
│   └── phases/     # 各阶段实现

dcae-mcp/           # MCP 服务器包 (pip install dcae-mcp)
└── dcae_mcp/
    └── server.py   # MCP Server 实现
```

---

## 核心场景（不需要 OpenClaw）

以下场景**完全独立于 OpenClaw**，可直接使用：

| 模式 | 调用方式 | 依赖 | 适用场景 |
|------|---------|------|---------|
| **Standalone MCP Server** | Claude Code → MCP → DCAE | dcae-mcp | Claude Code 原生集成 |
| **Standalone CLI** | exec → dcae CLI → DCAE | dcae | 任意 coding agent |
| **Python Library** | import dcae → DCAE | dcae | Python 程序集成 |

### 场景 1: Standalone MCP Server

**最佳实践**: Claude Code 用户首选

```bash
# 安装
pip install dcae-mcp

# 配置 Claude Code
# ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "dcae": {
      "command": "python3",
      "args": ["-m", "dcae_mcp.server"]
    }
  }
}
```

**优势**:
- Claude Code 原生支持
- 工具自动发现
- 支持流式输出

### 场景 2: Standalone CLI

**最佳实践**: 通用方案，任意 agent 可用

```bash
# 安装
pip install dcae

# 使用
dcae run --task "实现功能" --test tests/test.py --source src/code.py
```

**优势**:
- 简单直接
- 支持 JSON 输出
- 任意工具可调用

### 场景 3: Python Library

**最佳实践**: Python 程序内集成

```python
from dcae import DCAEFramework

dcae = DCAEFramework()
result = dcae.run("tests/test.py", "src/code.py")
```

---

## 可选场景（需要 OpenClaw）

| 模式 | 调用方式 | 依赖 | 说明 |
|------|---------|------|------|
| **OpenClaw Skill** | Claude Code → OpenClaw → DCAE Skill | dcae + openclaw | 仅作为文档/触发器 |

**注意**: OpenClaw Skill 场景中，实际执行仍通过 dcae 包，OpenClaw 仅提供 Skill 描述和触发词。

---

## 安装指南

### 前置要求

- Python 3.11+
- pip 包管理器

### 安装核心包

```bash
# 基础安装
pip install dcae

# 开发模式（包含测试工具）
pip install dcae[dev]
```

### 安装 MCP 服务器

```bash
# MCP Server（用于 Claude Code 集成）
pip install dcae-mcp
```

### 验证安装

```bash
# 检查 CLI
dcae --help

# 检查版本
python3 -c "import dcae; print(dcae.__version__)"
```

---

## Claude Code 配置

### 步骤 1: 安装 MCP 包

```bash
pip install dcae-mcp
```

### 步骤 2: 配置 Claude Desktop

编辑配置文件：

**Linux/macOS**: `~/.config/claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dcae": {
      "command": "python3",
      "args": ["-m", "dcae_mcp.server"]
    }
  }
}
```

### 步骤 3: 重启 Claude Code

重启后，DCAE 工具将自动出现在工具列表中。

### 验证配置

在 Claude Code 中输入：

```
列出可用的 DCAE 工具
```

应看到：
- tdd_run
- tdd_design
- tdd_code
- tdd_analyze
- tdd_evolve
- tdd_init
- tdd_status

---

## 调用示例

### 示例 1: 完整 TDD 循环（CLI）

```bash
dcae run \
  --task "实现快速排序算法" \
  --test tests/test_quick_sort.py \
  --source src/quick_sort.py \
  --max-iterations 10
```

### 示例 2: 完整 TDD 循环（JSON 输出）

```bash
dcae --json run \
  --task "实现快速排序" \
  --test tests/test_sort.py \
  --source src/sort.py
```

### 示例 3: 分阶段执行

```bash
# Phase 1: Design
dcae design --test tests/test_feature.py

# Phase 2: Code
dcae code --source src/feature.py

# Phase 3: Analyze
dcae analyze --threshold 80

# Phase 4: Evolve
dcae evolve --optimize
```

### 示例 4: Claude Code 调用

```
请使用 DCAE 框架实现快速排序：
- 调用 tdd_run 工具
- task: "实现快速排序算法"
- test_file: "tests/test_quick_sort.py"
- source_file: "src/quick_sort.py"
- max_iterations: 10
```

### 示例 5: Python API

```python
from dcae import DCAEFramework

# 创建实例
dcae = DCAEFramework(project_root="/path/to/project")

# 运行完整循环
result = dcae.run(
    test_file="tests/test_feature.py",
    source_file="src/feature.py",
    max_iterations=10
)

# 处理结果
if result.status == "success":
    print(f"✅ 完成，覆盖率：{result.coverage_lines:.1f}%")
else:
    print(f"⚠️ 状态：{result.status}")
    for rec in result.recommendations:
        print(f"  - {rec}")
```

---

## 故障排查

### 问题 1: CLI 命令未找到

**错误**: `command not found: dcae`

**解决**:
```bash
# 确认安装
pip show dcae

# 检查 PATH
echo $PATH

# 重新安装
pip install --user dcae
```

### 问题 2: MCP Server 未连接

**错误**: Claude Code 未显示 DCAE 工具

**解决**:
1. 检查配置文件语法（JSON 格式）
2. 确认 dcae-mcp 已安装：`pip show dcae-mcp`
3. 重启 Claude Code
4. 手动测试服务器：`python3 -m dcae_mcp.server`

### 问题 3: 测试无法运行

**错误**: pytest 未找到或测试失败

**解决**:
```bash
# 安装测试依赖
pip install pytest pytest-cov

# 验证 pytest
pytest --version

# 检查测试文件路径
ls -la tests/
```

### 问题 4: 覆盖率报告为空

**错误**: Coverage: 0.0%

**解决**:
```bash
# 安装 coverage 工具
pip install coverage pytest-cov

# 手动运行覆盖率
pytest --cov=dcae --cov-report=term-missing
```

---

## 快速参考

### 命令速查

| 命令 | 说明 |
|------|------|
| `dcae run` | 完整 TDD 循环 |
| `dcae design` | Phase 1: 创建测试 |
| `dcae code` | Phase 2: 实现代码 |
| `dcae analyze` | Phase 3: 分析质量 |
| `dcae evolve` | Phase 4: 重构优化 |
| `dcae init` | 初始化项目 |
| `dcae status` | 查看状态 |

### 质量门槛

| 指标 | 门槛 | 失败处理 |
|------|------|---------|
| 测试通过率 | 100% | 立即修复 |
| 行覆盖率 | ≥80% | 添加测试 |
| 函数覆盖率 | ≥90% | 添加边界测试 |
| 圈复杂度 | ≤10 | 重构 |

---

## 相关资源

- [DCAE README](README.md)
- [DCAE GitHub](https://github.com/openclaw/dcae)
- [MCP 协议文档](https://modelcontextprotocol.io)
- [TDD 最佳实践](references/tdd-fundamentals.md)

---

*文档版本：1.0.0*  
*维护者：OpenClaw Community*
