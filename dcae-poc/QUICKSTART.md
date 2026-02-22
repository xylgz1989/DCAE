# DCAE POC 快速开始指南

## 📦 安装依赖

```bash
cd dcae-poc
pip install -r requirements.txt
# 或
pip install pydantic pydantic-settings typer anthropic openai aiosqlite pyyaml httpx zhipuai dashscope
```

## 🔑 设置 API 密钥

### 使用中国 LLM (GLM + Qwen) - 推荐

#### 方式 1: 环境变量（推荐）

```bash
# Windows (PowerShell)
$env:GLM_API_KEY="your-glm-api-key"
$env:QWEN_API_KEY="your-qwen-api-key"

# Windows (CMD)
set GLM_API_KEY=your-glm-api-key
set QWEN_API_KEY=your-qwen-api-key

# Linux/Mac
export GLM_API_KEY="your-glm-api-key"
export QWEN_API_KEY="your-qwen-api-key"
```

#### 方式 2: 使用中国版配置文件

```bash
# 使用 config-china.yaml 配置
PYTHONPATH=./src python -m dcae.cli --config config-china.yaml run workflows/user_login.yaml
```

### 使用海外 LLM (Claude + OpenAI)

#### 方式 1: 环境变量

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
$env:OPENAI_API_KEY="your-openai-api-key"

# Windows (CMD)
set ANTHROPIC_API_KEY=your-anthropic-api-key
set OPENAI_API_KEY=your-openai-api-key

# Linux/Mac
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

#### 方式 2: 修改 config.yaml

编辑 `config.yaml`，直接填入 API 密钥：

```yaml
llm_config:
  claude:
    api_key: "your-actual-key-here"  # 直接填入
  openai:
    api_key: "your-actual-key-here"  # 直接填入
```

## 🚀 运行第一个工作流

### 使用中国 LLM

```bash
# Windows
PYTHONPATH=./src python -m dcae.cli --config config-china.yaml run workflows/user_login.yaml

# Linux/Mac
PYTHONPATH=./src python -m dcae.cli --config config-china.yaml run workflows/user_login.yaml
```

### 使用海外 LLM

```bash
PYTHONPATH=./src python -m dcae.cli run workflows/user_login.yaml
```

## 📊 支持的 LLM 提供商

| 提供商 | 模型示例 | 配置键 | 状态 |
|--------|----------|----------|------|
| **GLM (智谱)** | glm-4, glm-4-flash, glm-3-turbo | `glm` | ✅ 支持 |
| **Qwen (通义)** | qwen-max, qwen-turbo, qwen-plus | `qwen` | ✅ 支持 |
| **Claude** | claude-3-5-sonnet-20241022 | `claude` | ✅ 支持 |
| **OpenAI** | gpt-4o, gpt-4o-mini | `openai` | ✅ 支持 |

### 中国 LLM 模型列表

#### GLM (Zhipu AI)
- `glm-4` - 最新的 GLM-4 模型
- `glm-4-flash` - 快速版本
- `glm-4-air` - 轻量版本
- `glm-3-turbo` - 高性价比版本

#### Qwen (Alibaba DashScope)
- `qwen-max` - 最强模型
- `qwen-plus` - 增强版本
- `qwen-turbo` - 快速版本
- `qwen-long` - 长文本版本

## 📊 预期输出

```
============================================================
🚀 Starting Workflow: 用户登录功能开发
============================================================
Description: 使用 DCAE 框架实现用户登录功能...
Steps: 5
============================================================

────────────────────────────────────────────────────────────
Step 1/5: pm
Task: 编写用户登录功能的需求文档...
────────────────────────────────────────────────────────────
✅ Step Complete
...
```

## 🔍 查看命令帮助

```bash
# 查看所有可用命令
PYTHONPATH=./src python -m dcae.cli --help

# 查看可用 Agent
PYTHONPATH=./src python -m dcae.cli agents

# 查看可用技能
PYTHONPATH=./src python -m dcae.cli skills

# 查看决策记录
PYTHONPATH=./src python -m dcae.cli decisions

# 查看特定 Agent 的决策
PYTHONPATH=./src python -m dcae.cli decisions --agent architect
```

## 🧪 运行测试

```bash
PYTHONPATH=./src python -m pytest tests/ -v
```

## 📁 项目结构说明

```
dcae-poc/
├── config.yaml           # 主配置文件（海外 LLM）
├── config-china.yaml    # 中国版配置文件（GLM + Qwen）
├── src/dcae/            # 源代码
│   ├── config.py         # 配置加载
│   ├── core.py           # 核心编排器
│   ├── agent.py          # Agent 实现
│   ├── consensus.py      # 共识引擎
│   ├── skill.py          # 技能管理
│   ├── storage.py        # SQLite 存储
│   └── cli.py            # 命令行接口
├── skills/               # Superpowers 技能
│   ├── brainstorming.yaml
│   ├── tdd.yaml
│   └── code_review.yaml
├── workflows/            # 工作流定义
│   └── user_login.yaml
├── tests/                # 测试
└── dcae-poc.db         # 运行后生成的数据库
```

## ⚙️ 配置说明

### Agent 配置

每个 Agent 可以配置是否启用共识：

```yaml
agents:
  pm:
    model: "glm-4"              # 使用 GLM-4 模型
    consensus:
      enabled: false             # PM 不启用共识，单模型

  architect:
    model: "qwen-max"            # 使用 Qwen-Max 模型
    consensus:
      enabled: true              # Architect 启用共识
      models:                    # 使用的模型列表
        - glm-4                  # 智谱 GLM
        - qwen-max               # 通义 Qwen
      voting_strategy: "majority"  # 多数投票
      threshold: 0.6             # 60% 同意率
```

### 投票策略

- `unanimous` - 全体一致通过
- `majority` - 简单多数
- `weighted` - 加权投票（待实现）

### 技能配置

```yaml
skills:
  tdd:
    mandatory_for:
      - coding          # TDD 强制用于 coding 角色
  brainstorming:
    mandatory_for:
      - architect       # 头脑风暴强制用于 architect
```

## 🎯 下一步

1. 创建你自己的工作流：
   ```bash
   PYTHONPATH=./src python -m dcae.cli init my-project
   cd my-project
   PYTHONPATH=./src python -m dcae.cli run workflows/main.yaml
   ```

2. 修改配置文件调整模型和共识策略：
   ```yaml
   # 使用 GLM 和 Qwen 混合共识
   agents:
     architect:
       model: "glm-4"
       consensus:
         models:
           - glm-4
           - qwen-max
   ```

3. 在 `skills/` 目录添加自定义技能

4. 查看决策数据库追踪 AI 的决策过程

## 🐛 故障排除

### 问题: "No LLM client available"

**原因**: API 密钥未正确配置

**解决**: 检查环境变量或 config.yaml 中的 API 密钥

### 问题: 导入错误

**原因**: Poetry 虚拟环境未激活

**解决**: 使用 `PYTHONPATH=./src` 前缀运行命令

### 问题: 数据库错误

**解决**: 删除 `dcae-poc.db` 文件，重新运行

### 问题: GLM/Qwen 调用失败

**可能原因**:
1. API 密钥无效或已过期
2. 模型名称不正确
3. 网络连接问题

**解决**:
1. 检查 API 密钥是否正确
2. 确认模型名称（如 glm-4, qwen-max）
3. 测试网络连接

## 📝 自定义工作流示例

创建 `workflows/my-feature.yaml`:

```yaml
name: 我的新功能
description: 使用 DCAE 开发新功能

steps:
  - agent: pm
    task: "分析需求"

  - agent: architect
    skill: brainstorming
    task: "设计架构"
    # 将使用 glm-4 和 qwen-max 共识

  - agent: developer
    skill: tdd
    task: "实现功能"
    # 将使用 glm-4-flash 和 qwen-turbo 共识

  - agent: developer
    skill: code_review
    task: "代码审查"
```

运行：
```bash
PYTHONPATH=./src python -m dcae.cli run workflows/my-feature.yaml
```

## 🔗 获取 API 密钥

### GLM (智谱 AI)
1. 访问：https://open.bigmodel.cn/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key

### Qwen (阿里通义)
1. 访问：https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 创建 DashScope API Key
