# DCAE Coding Agent MVP

## 简介

DCAE Coding Agent 是一个命令行 AI 编程助手，专注于日常开发任务：
- 代码生成
- 代码审查
- 问题调试
- 需求文档生成
- 测试文档生成
- 测试用例生成

## 快速开始

### 第 1 步：安装依赖

```bash
pip install openai
```

### 第 2 步：初始化配置

```bash
python dcae-mvp.py init
```

配置向导会引导你设置：
1. 选择 LLM 提供商（Qwen、GLM、OpenAI）
2. 输入 API Key
3. 设置预算控制（Token 数量或金额）

### 第 3 步：开始使用

## 命令参考

### 初始化

```bash
python dcae-mvp.py init
```

### 需求文档生成

```bash
# 生成需求文档（显示在终端）
python dcae_mvp.py req "用户登录功能需求"

# 保存到文件
python dcae_mvp.py req "用户登录功能需求" -o docs/requirements.md
```

### 代码生成

```bash
# 生成代码（显示在终端）
python dcae_mvp.py gen "写一个用户登录功能"

# 保存到文件
python dcae_mvp.py gen "写一个用户登录功能" -o auth.py
```

### 代码审查

```bash
python dcae_mvp.py review auth.py
```

### 测试文档生成

```bash
# 生成测试文档
python dcae_mvp.py test-doc auth.py

# 保存到文件
python dcae_mvp.py test-doc auth.py -o docs/test_documentation.md
```

### 测试用例生成

```bash
# 为代码文件生成测试用例
python dcae_mvp.py test-case auth.py
```

### 问题调试

```bash
# 基本调试
python dcae_mvp.py debug "401错误"

# 带上下文调试
python dcae_mvp.py debug "401错误" --context auth.py
```

### 查看状态

```bash
python dcae_mvp.py status
```

显示：
- 配置信息
- 预算使用情况
- 可用模型列表

## 开发工作流示例

### 完整开发流程

```bash
# 1. 生成需求文档
python dcae_mvp.py req "用户认证系统需求" -o docs/requirements.md

# 2. 生成代码
python dcae_mvp.py gen "实现用户认证系统" -o src/auth.py

# 3. 审查代码
python dcae_mvp.py review src/auth.py

# 4. 生成测试文档
python dcae_mvp.py test-doc src/auth.py -o docs/test_plan.md

# 5. 生成测试用例
python dcae_mvp.py test-case src/auth.py

# 6. 运行测试
pytest tests/
```

## 支持的 LLM 提供商

| 提供商 | 推荐模型 | 特点 |
|--------|---------|------|
| Qwen | qwen-coder-plus | 编程专用，性价比高 |
| GLM | glm-4 | 综合能力强 |
| OpenAI | gpt-4o | 国际领先 |
| Claude | claude-3-5-sonnet | 代码审查优秀 |

## 预算控制

系统自动追踪 Token 使用量：

- **每日预算**：默认 100,000 tokens
- **每月预算**：默认 2,000,000 tokens

当预算使用超过 80% 时，系统会自动降级到更便宜的模型。

## 智能模型选择

系统会根据任务类型和预算自动选择最合适的模型：

- **简单任务** → qwen-turbo（便宜）
- **中等任务** → qwen-plus（平衡）
- **复杂任务** → qwen-coder-plus（编程）
- **高优先级** → qwen-max（最强）

## 配置文件

配置文件位于：`~/.dcae/config.json`

示例配置：

```json
{
  "provider": "qwen",
  "api_key": "your-api-key",
  "budget_mode": "token",
  "daily_limit": 100000,
  "monthly_limit": 2000000,
  "model_preference": "auto",
  "fallback_model": "qwen-plus",
  "daily_used": 0,
  "monthly_used": 0,
  "last_date": "2024-01-01"
}
```

## 使用技巧

1. **生成需求时**：尽可能详细地描述功能需求和场景
2. **生成代码时**：指定技术栈（如 Python + FastAPI）
3. **审查代码时**：提供上下文信息（如其他相关文件）
4. **调试问题时**：粘贴完整的错误信息和相关代码

## 故障排查

### 常见问题

**Q: 提示"未找到配置"**
A: 请先运行 `python dcae_mvp.py init`

**Q: API 调用失败**
A: 检查 API Key 是否正确，网络是否通畅

**Q: 预算超出**
A: 可以修改 `~/.dcae/config.json` 中的预算限制

**Q: 生成质量不满意**
A: 尝试在 prompt 中添加更多细节和要求

## 下一步功能

- [ ] 代码重构建议
- [ ] 架构设计生成
- [ ] 多文件项目管理
- [ ] Web UI 界面
- [ ] VS Code 插件

## License

MIT