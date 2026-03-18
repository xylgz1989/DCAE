# DCAE 框架

**Disciplined Consensus-Driven Agentic Engineering** - 全面的 AI 辅助软件工程框架

[English](README.md) | [中文](README_CN.md)

---

## 什么是 DCAE？

DCAE 是一个智能开发助手，帮助您更快地构建更优质的软件。它将 AI 驱动的代码生成与规范的工程实践相结合，提高您的生产力和代码质量。

## 快速开始

```bash
# 安装依赖
pip install -e .

# 初始化 DCAE
python dcae.py init

# 开始 AI 辅助编程
python dcae.py --help
```

## 核心功能

### 🎯 需求管理
- 从自然语言描述生成详细的需求文档
- 早期识别冲突和问题
- 导出和分享需求给团队

### 🏗️ 架构设计
- 根据需求生成架构解决方案
- 对照最佳实践审查和验证架构
- 交互式修改和完善

### 💻 代码生成
- 根据规范生成代码结构
- 自动实现业务逻辑
- 支持多种技术栈和语言

### 🔍 代码审查
- 自动化代码质量分析
- 问题识别和修复建议
- 多层验证系统

### 🧪 测试与文档
- 生成全面的测试用例
- 支持多种测试类型（单元测试、集成测试等）
- 自动生成测试文档

### 🧠 知识融合
- 跨领域知识整合
- 最佳实践推荐
- 项目特定约束学习

### ⚙️ 多 LLM 支持
- 支持通义千问、GLM、GPT-4、Claude 等
- 根据任务复杂度智能选择模型
- 预算管理和使用追踪

### 📊 流程规范
- 可配置的规范级别
- 可调整的验证严格度
- 合规性追踪

## 项目结构

```
DCAE/
├── src/                    # 源代码
│   └── dcae/
│       ├── cli.py          # 命令行接口
│       ├── knowledge_fusion/
│       ├── product_knowledge/
│       ├── task_management/
│       └── ...
├── tests/                  # 测试套件
├── docs/                   # 文档
├── examples/               # 示例代码
├── templates/              # 项目模板
└── config/                 # 配置文件
```

## 安装

### 前置条件
- Python 3.8 或更高版本
- pip 包管理器
- 首选 LLM 提供商的 API 密钥

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/xylgz1989/DCAE.git
   cd DCAE
   ```

2. **安装依赖**
   ```bash
   pip install -e .
   ```

3. **初始化配置**
   ```bash
   python dcae.py init
   ```

4. **配置 LLM 提供商**
   - 选择提供商（通义千问、GLM、OpenAI、Claude 等）
   - 输入 API 密钥
   - 设置预算限制（可选）

## 使用示例

### 生成需求文档
```bash
python dcae.py req "构建一个支持 OAuth2 的用户认证系统"
```

### 生成代码
```bash
python dcae.py gen "创建一个用户注册的 REST API 端点"
```

### 审查代码
```bash
python dcae.py review src/my_module.py
```

### 生成测试
```bash
python dcae.py test-case src/my_module.py
```

## 配置

DCAE 将配置存储在 `~/.dcae/config.json`：

```json
{
  "provider": "qwen",
  "api_key": "your-api-key",
  "model": "qwen-plus",
  "daily_limit": 100,
  "monthly_limit": 1000
}
```

## 支持的 LLM 提供商

| 提供商 | 模型 | 区域 |
|--------|------|------|
| 通义千问 | Turbo, Plus, Coder Plus, Max | 全球/中国 |
| GLM | GLM-4 | 中国 |
| OpenAI | GPT-4o | 全球 |
| Anthropic | Claude 3.5 Sonnet | 全球 |

## 文档

- [最佳实践指南](docs/best_practices.md)
- [约束处理指南](docs/constraint_handling_guide.md)
- [行为准则](CODE_OF_CONDUCT.md)
- [贡献指南](CONTRIBUTING.md)

## 开发

### 运行测试
```bash
python -m pytest tests/ -v
```

### 构建包
```bash
python setup.py build
```

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

我们欢迎贡献！请阅读我们的 [贡献指南](CONTRIBUTING.md) 了解指南。

## 支持

- **问题反馈**: [GitHub Issues](https://github.com/xylgz1989/DCAE/issues)
- **讨论**: [GitHub Discussions](https://github.com/xylgz1989/DCAE/discussions)

## 致谢

基于 BMAD 方法论构建，实现规范的软件工程实践。

---

**版本**: 1.0.0 | **状态**: 稳定版
