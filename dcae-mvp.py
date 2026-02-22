#!/usr/bin/env python3
"""DCAE Coding Agent - Simplified MVP

A practical coding assistant for daily development tasks.
Focus on: code generation, review, and bug fixing.

Usage:
    python dcae_mvp.py init                    # Initialize configuration
    python dcae_mvp.py gen <prompt>            # Generate code
    python dcae_mvp.py review <file>          # Review code
    python dcae_mvp.py debug <error>          # Debug issues
    python dcae_mvp.py req <prompt>           # Generate requirement document
    python dcae_mvp.py test-doc <file>        # Generate test documentation
    python dcae_mvp.py test-case <file>       # Generate test cases
    python dcae_mvp.py status                 # Show status
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI


class DCAEConfig:
    """Simple configuration manager."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load()

    def _load(self) -> dict:
        """Load or create configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save(self):
        """Save configuration."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()


class BudgetTracker:
    """Simple budget tracking in tokens."""

    def __init__(self, config: DCAEConfig):
        self.config = config
        self.reset_daily()

    def reset_daily(self):
        """Reset daily budget if needed."""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.config.get('last_date') != today:
            self.config.set('last_date', today)
            self.config.set('daily_used', 0)

    def use(self, tokens: int):
        """Record token usage."""
        daily = self.config.get('daily_used', 0)
        monthly = self.config.get('monthly_used', 0)
        self.config.set('daily_used', daily + tokens)
        self.config.set('monthly_used', monthly + tokens)

    def get_status(self) -> dict:
        """Get budget status."""
        daily_limit = self.config.get('daily_limit', 100000)
        daily_used = self.config.get('daily_used', 0)
        monthly_limit = self.config.get('monthly_limit', 2000000)
        monthly_used = self.config.get('monthly_used', 0)

        return {
            'daily': {'used': daily_used, 'limit': daily_limit, 'percent': daily_used / daily_limit * 100},
            'monthly': {'used': monthly_used, 'limit': monthly_limit, 'percent': monthly_used / monthly_limit * 100}
        }


class DCAEAgent:
    """Main DCAE coding agent."""

    # Model capabilities (simplified)
    MODELS = {
        'qwen-turbo': {
            'cost': 0.0001,  # per 1k tokens (estimated)
            'max_tokens': 8192,
            'strengths': ['simple', 'docs', 'formatting']
        },
        'qwen-plus': {
            'cost': 0.0005,
            'max_tokens': 32768,
            'strengths': ['medium', 'code-gen', 'review']
        },
        'qwen-coder-plus': {
            'cost': 0.001,
            'max_tokens': 32768,
            'strengths': ['coding', 'architecture', 'code-review']
        },
        'qwen-max': {
            'cost': 0.005,
            'max_tokens': 128000,
            'strengths': ['complex', 'security', 'architecture']
        },
        'glm-4': {
            'cost': 0.002,
            'max_tokens': 128000,
            'strengths': ['medium', 'code-gen', 'review']
        },
        'gpt-4o': {
            'cost': 0.01,
            'max_tokens': 128000,
            'strengths': ['complex', 'code-gen', 'debug']
        },
        'claude-3-5-sonnet': {
            'cost': 0.015,
            'max_tokens': 200000,
            'strengths': ['complex', 'code-review', 'architecture']
        }
    }

    def __init__(self, config: DCAEConfig):
        self.config = config
        self.budget = BudgetTracker(config)
        self.client = self._create_client()

    def _create_client(self) -> Optional[AsyncOpenAI]:
        """Create LLM client based on configuration."""
        provider = self.config.get('provider', 'qwen')
        api_key = self.config.get('api_key')

        if not api_key:
            return None

        if provider == 'qwen':
            return AsyncOpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )
        elif provider == 'glm':
            return AsyncOpenAI(
                api_key=api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4"
            )
        elif provider == 'openai':
            return AsyncOpenAI(api_key=api_key)
        elif provider == 'claude':
            # Not supported in MVP - use OpenAI client for now
            return None

        return None

    def select_model(self, task_type: str, complexity: str = 'medium') -> str:
        """Select optimal model based on task and budget."""
        # Get configured model preference
        preferred = self.config.get('model_preference', 'auto')

        if preferred != 'auto':
            return preferred

        # Auto-select based on task
        budget_status = self.budget.get_status()
        daily_percent = budget_status['daily']['percent']

        # If budget is tight, use cheaper model
        if daily_percent > 80:
            fallback = self.config.get('fallback_model', 'qwen-plus')
            if fallback in self.MODELS:
                return fallback

        # Select based on task type
        if task_type == 'gen':
            # Code generation
            if complexity == 'simple':
                return 'qwen-plus'
            elif complexity == 'complex':
                return 'qwen-coder-plus'
            else:
                return 'qwen-coder-plus'

        elif task_type == 'review':
            # Code review
            if daily_percent > 60:
                return 'qwen-plus'
            else:
                return 'qwen-coder-plus'

        elif task_type == 'debug':
            # Debugging
            return 'qwen-coder-plus'

        return 'qwen-plus'  # Default

    async def generate_code(self, prompt: str, save_to: Optional[Path] = None) -> str:
        """Generate code from prompt."""
        model = self.select_model('gen')
        system_prompt = """你是一个专业的软件开发助手。请根据用户需求生成高质量的代码。

要求：
1. 代码应该是完整可运行的
2. 包含必要的导入和错误处理
3. 添加清晰的注释
4. 如果需要依赖，在代码末尾列出 requirements.txt 内容

输出格式：
```语言名
// 代码
```

如果需要依赖：
---
Requirements:
依赖列表
"""

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,
            )

            tokens_used = response.usage.total_tokens
            self.budget.use(tokens_used)

            result = response.choices[0].message.content

            # Extract code blocks
            if '```' in result:
                # Find code block
                lines = result.split('\n')
                code_lines = []
                in_code = False
                code_lang = ''
                requirements = []

                for line in lines:
                    if line.startswith('```'):
                        if not in_code:
                            in_code = True
                            if len(line) > 3:
                                code_lang = line[3:].strip()
                        else:
                            in_code = False
                        continue
                    elif line.startswith('---'):
                        # Check if requirements section
                        if 'Requirements:' in '\n'.join(lines[lines.index(line):]):
                            in_code = False
                            continue
                    elif in_code:
                        code_lines.append(line)
                    elif 'Requirements:' in line:
                        # Start of requirements
                        continue
                    elif in_code == False and code_lines and line.strip() and not line.startswith('---'):
                        if line.strip():
                            requirements.append(line.strip())

                result = '\n'.join(code_lines)

                # Save to file if specified
                if save_to and code_lines:
                    save_to.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_to, 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"✅ Code saved to: {save_to}")

                # Save requirements if found
                if requirements:
                    req_file = save_to.parent / 'requirements.txt' if save_to else Path('requirements.txt')
                    with open(req_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(requirements))
                    print(f"✅ Requirements saved to: {req_file}")

            return result

        except Exception as e:
            return f"Error: {str(e)}"

    async def review_code(self, file_path: Path) -> str:
        """Review code file."""
        if not file_path.exists():
            return f"Error: File not found: {file_path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        model = self.select_model('review')
        system_prompt = """你是一个专业的代码审查助手。请审查提供的代码并给出详细的改进建议。

输出格式：

## 总体评价
[代码整体质量评分和简要评价]

## 发现的问题
1. [问题1] - 严重性: 高/中/低
   - 位置: [文件名:行号]
   - 描述: [问题描述]
   - 建议: [修复建议]

## 改进建议
1. [建议1] - 类别: 性能/可读性/安全性/最佳实践
   - 描述: [建议描述]
   - 示例: [代码示例]

## 最佳实践
- [符合的最佳实践]
- [可以改进的地方]

## 总体评分
[代码质量评分 / 10]
"""

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请审查以下代码：\n\n文件: {file_path.name}\n\n```python\n{code}\n```"}
                ],
                max_tokens=4096,
            )

            tokens_used = response.usage.total_tokens
            self.budget.use(tokens_used)

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    async def debug_issue(self, error_message: str, context: Optional[str] = None) -> str:
        """Debug an issue."""
        model = self.select_model('debug')
        system_prompt = """你是一个专业的调试助手。请帮助用户解决技术问题。

输出格式：

## 问题分析
[分析错误原因]

## 解决方案
[详细的解决步骤]

## 代码示例
[修复后的代码示例]

## 预防措施
[如何避免类似问题]

## 相关资源
[相关文档或链接]
"""

        user_content = f"错误信息: {error_message}"
        if context:
            user_content += f"\n\n上下文代码:\n{context}"

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=4096,
            )

            tokens_used = response.usage.total_tokens
            self.budget.use(tokens_used)

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_requirement(self, prompt: str, save_to: Optional[Path] = None) -> str:
        """Generate requirement document."""
        model = self.select_model('gen', complexity='complex')
        system_prompt = """你是一个专业的产品经理和需求分析师。请根据用户的需求描述生成详细的需求文档。

输出格式：

# [产品/功能名称] 需求文档

## 1. 文档信息
- 文档版本: v1.0
- 创建日期: [日期]
- 负责人: [待定]

## 2. 项目概述
### 2.1 项目背景
[描述项目的背景和起源]

### 2.2 项目目标
[明确的项目目标，使用SMART原则]

### 2.3 目标用户
[描述主要用户群体和使用场景]

## 3. 功能需求
### 3.1 核心功能
[列出核心功能，每个功能包含:]
- 功能名称
- 功能描述
- 用户故事
- 验收标准

### 3.2 次要功能
[列出次要功能]

## 4. 非功能需求
### 4.1 性能需求
[响应时间、吞吐量等]

### 4.2 安全需求
[数据安全、访问控制等]

### 4.3 可用性需求
[系统可用性、容错等]

### 4.4 兼容性需求
[浏览器、设备、系统兼容性]

## 5. 约束条件
### 5.1 技术约束
[技术栈限制]

### 5.2 资源约束
[时间、人力、预算等]

### 5.3 业务约束
[法律法规、业务规则等]

## 6. 验收标准
### 6.1 功能验收
[每个功能的验收标准]

### 6.2 性能验收
[性能指标和测试方法]

### 6.3 安全验收
[安全测试要求]

## 7. 附录
### 7.1 术语表
[项目专用术语解释]

### 7.2 参考文档
[相关文档和链接]
"""

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请为以下需求生成详细的需求文档：\n\n{prompt}"}
                ],
                max_tokens=8192,
            )

            tokens_used = response.usage.total_tokens
            self.budget.use(tokens_used)

            result = response.choices[0].message.content

            # Save to file if specified
            if save_to:
                save_to.parent.mkdir(parents=True, exist_ok=True)
                with open(save_to, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✅ Requirement document saved to: {save_to}")

            return result

        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_test_documentation(self, file_path: Path, save_to: Optional[Path] = None) -> str:
        """Generate test documentation for code file."""
        if not file_path.exists():
            return f"Error: File not found: {file_path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        model = self.select_model('gen', complexity='medium')
        system_prompt = """你是一个专业的测试架构师。请为提供的代码生成详细的测试文档。

输出格式：

# [文件名] 测试文档

## 1. 测试概述
### 1.1 测试目标
[明确测试的目标和范围]

### 1.2 测试策略
[测试方法：单元测试、集成测试、端到端测试等]

## 2. 测试范围
### 2.1 功能测试范围
[需要测试的功能点]

### 2.2 边界测试范围
[边界条件和特殊场景]

### 2.3 异常测试范围
[异常情况和错误处理]

## 3. 测试用例
### 3.1 正常用例
[正常情况下的测试用例，每个用例包含:]
- 用例编号
- 用例名称
- 前置条件
- 测试步骤
- 预期结果

### 3.2 边界用例
[边界条件的测试用例]

### 3.3 异常用例
[异常情况的测试用例]

## 4. 测试数据
### 4.1 测试输入数据
[测试所需的输入数据]

### 4.2 测试环境要求
[测试环境配置]

## 5. 测试工具和框架
### 5.1 推荐测试框架
[推荐的测试框架，如 pytest、unittest 等]

### 5.2 测试工具
[辅助测试工具]

## 6. 测试执行计划
### 6.1 测试顺序
[测试执行的顺序]

### 6.2 测试时间估算
[每个测试用例的时间估算]

## 7. 测试报告模板
[测试报告的格式和内容要求]
"""

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请为以下代码生成测试文档：\n\n文件: {file_path.name}\n\n```python\n{code}\n```"}
                ],
                max_tokens=8192,
            )

            tokens_used = response.usage.total_tokens
            self.budget.use(tokens_used)

            result = response.choices[0].message.content

            # Save to file if specified
            if save_to:
                save_to.parent.mkdir(parents=True, exist_ok=True)
                with open(save_to, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✅ Test documentation saved to: {save_to}")

            return result

        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_test_cases(self, file_path: Path, save_to: Optional[Path] = None) -> str:
        """Generate test cases for code file."""
        if not file_path.exists():
            return f"Error: File not found: {file_path}"

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        model = self.select_model('gen', complexity='medium')
        system_prompt = """你是一个专业的测试工程师。请为提供的代码生成可运行的测试用例代码。

要求：
1. 使用 pytest 框架（除非代码明确使用其他框架）
2. 测试用例应该完整且可运行
3. 包含正常、边界、异常三种类型的测试
4. 添加必要的测试数据准备和清理
5. 添加清晰的注释

输出格式：

```python
# 测试文件代码
# 包含所有必要的导入、测试函数、fixture等
```

如果有额外的测试依赖：
---
Requirements:
依赖列表

如果有测试数据文件需要创建：
---
Test Data Files:
测试数据文件列表
"""

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请为以下代码生成测试用例：\n\n文件: {file_path.name}\n\n```python\n{code}\n```"}
                ],
                max_tokens=8192,
            )

            tokens_used = response.usage.total_tokens
            self.budget.use(tokens_used)

            result = response.choices[0].message.content

            # Extract code blocks and test data
            if '```' in result:
                lines = result.split('\n')
                test_code_lines = []
                in_code = False
                requirements = []
                test_data_files = []
                current_section = None

                for line in lines:
                    if line.startswith('```'):
                        if not in_code:
                            in_code = True
                        else:
                            in_code = False
                        continue
                    elif line.startswith('---'):
                        if 'Requirements:' in '\n'.join(lines[lines.index(line):]):
                            current_section = 'requirements'
                        elif 'Test Data Files:' in '\n'.join(lines[lines.index(line):]):
                            current_section = 'test_data'
                        continue
                    elif in_code:
                        test_code_lines.append(line)
                    elif current_section == 'requirements':
                        if line.strip():
                            requirements.append(line.strip())
                    elif current_section == 'test_data':
                        if line.strip():
                            test_data_files.append(line.strip())

                test_code = '\n'.join(test_code_lines)

                # Determine test file name
                test_file_name = f"test_{file_path.stem}.py"
                if save_to:
                    save_to = save_to.with_name(test_file_name)
                else:
                    save_to = file_path.parent / test_file_name

                # Save test code
                save_to.parent.mkdir(parents=True, exist_ok=True)
                with open(save_to, 'w', encoding='utf-8') as f:
                    f.write(test_code)
                print(f"✅ Test cases saved to: {save_to}")

                # Save requirements if found
                if requirements:
                    req_file = save_to.parent / 'test_requirements.txt'
                    with open(req_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(requirements))
                    print(f"✅ Test requirements saved to: {req_file}")

                # Create test data files if specified
                for test_data_file in test_data_files:
                    data_file_path = save_to.parent / test_data_file
                    # Create empty file as placeholder
                    data_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(data_file_path, 'w', encoding='utf-8') as f:
                        f.write("# TODO: Add test data\n")
                    print(f"✅ Test data file created: {data_file_path}")

                return test_code

            return result

        except Exception as e:
            return f"Error: {str(e)}"


async def cmd_init(args):
    """Initialize DCAE configuration."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if config_path.exists():
        print("⚠️  Configuration already exists")
        print(f"   Location: {config_path}")
        print("   Run 'dcae_mvp.py init --reset' to reinitialize")
        return

    print("=" * 60)
    print("DCAE 初始化向导")
    print("=" * 60)
    print()

    # Select provider
    print("1. 选择 LLM 提供商:")
    print("   [1] Qwen (推荐中国用户)")
    print("   [2] GLM (智谱AI)")
    print("   [3] OpenAI")
    print("   [4] Claude (暂不支持)")
    provider_choice = input("   选择 (1-4): ").strip() or '1'

    provider_map = {'1': 'qwen', '2': 'glm', '3': 'openai', '4': 'claude'}
    provider = provider_map.get(provider_choice, 'qwen')

    # API Key
    api_key = input("2. 输入 API Key: ").strip()
    while not api_key:
        api_key = input("   API Key 不能为空，请重新输入: ").strip()

    # Budget mode
    print()
    print("3. 预算控制方式:")
    print("   [1] Token 数量")
    print("   [2] 金额")
    budget_mode = input("   选择 (1-2): ").strip() or '1'
    budget_mode = 'token' if budget_mode == '1' else 'amount'

    # Daily budget
    if budget_mode == 'token':
        daily_default = 100000
        daily_input = input(f"4. 每日预算 (Token, 默认 {daily_default}): ").strip()
        daily_limit = int(daily_input) if daily_input else daily_default

        monthly_default = 2000000
        monthly_input = input(f"5. 每月预算 (Token, 默认 {monthly_default}): ").strip()
        monthly_limit = int(monthly_input) if monthly_input else monthly_default
    else:
        daily_default = 10
        daily_input = input(f"4. 每日预算 (元, 默认 {daily_default}): ").strip()
        daily_limit = float(daily_input) if daily_input else daily_default

        monthly_default = 200
        monthly_input = input(f"5. 每月预算 (元, 默认 {monthly_default}): ").strip()
        monthly_limit = float(monthly_input) if monthly_input else monthly_default

    # Model preference
    print()
    print("6. 模型选择方式:")
    print("   [1] 自动选择 (推荐)")
    print("   [2] 固定模型")
    model_choice = input("   选择 (1-2): ").strip() or '1'

    if model_choice == '1':
        model_preference = 'auto'
        # Set fallback model
        fallback_map = {'qwen': 'qwen-plus', 'glm': 'glm-4', 'openai': 'gpt-4o', 'claude': 'claude-3-5-sonnet'}
        fallback_model = fallback_map.get(provider, 'qwen-plus')
        config.set('fallback_model', fallback_model)
    else:
        print(f"   可用模型: {', '.join(DCAEAgent.MODELS.keys())}")
        model_input = input("   选择模型: ").strip()
        model_preference = model_input if model_input in DCAEAgent.MODELS else 'auto'

    # Save configuration
    config.set('provider', provider)
    config.set('api_key', api_key)
    config.set('budget_mode', budget_mode)
    config.set('daily_limit', daily_limit)
    config.set('monthly_limit', monthly_limit)
    config.set('model_preference', model_preference)
    config.set('daily_used', 0)
    config.set('monthly_used', 0)
    config.set('last_date', datetime.now().strftime('%Y-%m-%d'))

    print()
    print("=" * 60)
    print("✅ 配置完成！")
    print("=" * 60)
    print()
    print("你现在可以开始使用 DCAE:")
    print("  python dcae_mvp.py gen \"写一个用户登录功能\"")
    print("  python dcae_mvp.py review src/main.py")
    print("  python dcae_mvp.py debug \"出现401错误\"")
    print("  python dcae_mvp.py status")
    print()


async def cmd_gen(args):
    """Generate code from prompt."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)

    if not agent.client:
        print("❌ 无法创建 LLM 客户端，请检查配置")
        return

    prompt = args.prompt
    output_file = args.output

    print(f"🤖 正在生成代码...")
    print(f"   Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"   Prompt: {prompt}")
    print()

    result = await agent.generate_code(prompt, Path(output_file) if output_file else None)

    print()
    print("=" * 60)
    print("生成结果:")
    print("=" * 60)
    print()
    print(result)
    print()
    print("=" * 60)
    print("Budget Status:")
    budget_status = agent.budget.get_status()
    print(f"   Daily: {budget_status['daily']['used']:,} / {budget_status['daily']['limit']:,} tokens ({budget_status['daily']['percent']:.1f}%)")
    print("=" * 60)


async def cmd_review(args):
    """Review code file."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)

    if not agent.client:
        print("❌ 无法创建 LLM 客户端，请检查配置")
        return

    file_path = Path(args.file)

    print(f"🔍 正在审查代码...")
    print(f"   File: {file_path}")
    print()

    result = await agent.review_code(file_path)

    print()
    print("=" * 60)
    print("代码审查报告:")
    print("=" * 60)
    print()
    print(result)
    print()
    print("=" * 60)
    print("Budget Status:")
    budget_status = agent.budget.get_status()
    print(f"   Daily: {budget_status['daily']['used']:,} / {budget_status['daily']['limit']:,} tokens ({budget_status['daily']['percent']:.1f}%)")
    print("=" * 60)


async def cmd_debug(args):
    """Debug an issue."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)

    if not agent.client:
        print("❌ 无法创建 LLM 客户端，请检查配置")
        return

    error_message = args.error
    context = None

    if args.context:
        context_file = Path(args.context)
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                context = f.read()

    print(f"🐛 正在分析问题...")
    print(f"   Error: {error_message[:50]}..." if len(error_message) > 50 else f"   Error: {error_message}")
    print()

    result = await agent.debug_issue(error_message, context)

    print()
    print("=" * 60)
    print("问题分析:")
    print("=" * 60)
    print()
    print(result)
    print()
    print("=" * 60)
    print("Budget Status:")
    budget_status = agent.budget.get_status()
    print(f"   Daily: {budget_status['daily']['used']:,} / {budget_status['daily']['limit']:,} tokens ({budget_status['daily']['percent']:.1f}%)")
    print("=" * 60)


async def cmd_status(args):
    """Show status."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)
    budget_status = agent.budget.get_status()

    print("=" * 60)
    print("DCAE 状态")
    print("=" * 60)
    print()
    print("配置信息:")
    print(f"  Provider: {config.get('provider', 'N/A')}")
    print(f"  Model Preference: {config.get('model_preference', 'N/A')}")
    print(f"  Budget Mode: {config.get('budget_mode', 'N/A')}")
    print()
    print("预算状态:")
    daily = budget_status['daily']
    monthly = budget_status['monthly']
    print(f"  Daily: {daily['used']:,} / {daily['limit']:,} tokens ({daily['percent']:.1f}%)")
    print(f"  Monthly: {monthly['used']:,} / {monthly['limit']:,} tokens ({monthly['percent']:.1f}%)")
    print()
    print("可用模型:")
    for model_name, model_info in DCAEAgent.MODELS.items():
        strengths = ', '.join(model_info['strengths'])
        print(f"  {model_name:20} - {strengths}")
    print()
    print("=" * 60)


async def cmd_req(args):
    """Generate requirement document."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)

    if not agent.client:
        print("❌ 无法创建 LLM 客户端，请检查配置")
        return

    prompt = args.prompt
    output_file = args.output

    print(f"📋 正在生成需求文档...")
    print(f"   Prompt: {prompt[:50]}..." if len(prompt) > 50 else f"   Prompt: {prompt}")
    print()

    result = await agent.generate_requirement(prompt, Path(output_file) if output_file else None)

    print()
    print("=" * 60)
    print("需求文档:")
    print("=" * 60)
    print()
    print(result)
    print()
    print("=" * 60)
    print("Budget Status:")
    budget_status = agent.budget.get_status()
    print(f"   Daily: {budget_status['daily']['used']:,} / {budget_status['daily']['limit']:,} tokens ({budget_status['daily']['percent']:.1f}%)")
    print("=" * 60)


async def cmd_test_doc(args):
    """Generate test documentation."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)

    if not agent.client:
        print("❌ 无法创建 LLM 客户端，请检查配置")
        return

    file_path = Path(args.file)
    output_file = args.output

    print(f"📝 正在生成测试文档...")
    print(f"   File: {file_path}")
    print()

    result = await agent.generate_test_documentation(file_path, Path(output_file) if output_file else None)

    print()
    print("=" * 60)
    print("测试文档:")
    print("=" * 60)
    print()
    print(result)
    print()
    print("=" * 60)
    print("Budget Status:")
    budget_status = agent.budget.get_status()
    print(f"   Daily: {budget_status['daily']['used']:,} / {budget_status['daily']['limit']:,} tokens ({budget_status['daily']['percent']:.1f}%)")
    print("=" * 60)


async def cmd_test_case(args):
    """Generate test cases."""
    config_path = Path.home() / '.dcae' / 'config.json'
    config = DCAEConfig(config_path)

    if not config_path.exists():
        print("❌ 未找到配置，请先运行: python dcae_mvp.py init")
        return

    agent = DCAEAgent(config)

    if not agent.client:
        print("❌ 无法创建 LLM 客户端，请检查配置")
        return

    file_path = Path(args.file)

    print(f"🧪 正在生成测试用例...")
    print(f"   File: {file_path}")
    print()

    result = await agent.generate_test_cases(file_path)

    if result and not result.startswith("Error"):
        print()
        print("=" * 60)
        print("测试用例已生成！")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("测试用例:")
        print("=" * 60)
        print()
        print(result)
        print()

    print("=" * 60)
    print("Budget Status:")
    budget_status = agent.budget.get_status()
    print(f"   Daily: {budget_status['daily']['used']:,} / {budget_status['daily']['limit']:,} tokens ({budget_status['daily']['percent']:.1f}%)")
    print("=" * 60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='DCAE Coding Agent - Simplified MVP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configuration
  python dcae_mvp.py init

  # Development workflow
  python dcae_mvp.py req "用户登录功能需求"
  python dcae_mvp.py gen "写一个用户登录功能" -o auth.py
  python dcae_mvp.py review auth.py
  python dcae_mvp.py test-doc auth.py
  python dcae_mvp.py test-case auth.py

  # Debugging
  python dcae_mvp.py debug "401错误"
  python dcae_mvp.py debug "401错误" --context auth.py

  # Status
  python dcae_mvp.py status
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # init command
    subparsers.add_parser('init', help='Initialize DCAE configuration')

    # gen command
    gen_parser = subparsers.add_parser('gen', help='Generate code from prompt')
    gen_parser.add_argument('prompt', help='Prompt for code generation')
    gen_parser.add_argument('-o', '--output', help='Output file path')

    # review command
    review_parser = subparsers.add_parser('review', help='Review code file')
    review_parser.add_argument('file', help='File to review')

    # debug command
    debug_parser = subparsers.add_parser('debug', help='Debug an issue')
    debug_parser.add_argument('error', help='Error message')
    debug_parser.add_argument('-c', '--context', help='Context file')

    # status command
    subparsers.add_parser('status', help='Show DCAE status')

    # req command
    req_parser = subparsers.add_parser('req', help='Generate requirement document')
    req_parser.add_argument('prompt', help='Requirement prompt')
    req_parser.add_argument('-o', '--output', help='Output file path')

    # test-doc command
    test_doc_parser = subparsers.add_parser('test-doc', help='Generate test documentation')
    test_doc_parser.add_argument('file', help='Code file to generate test docs for')
    test_doc_parser.add_argument('-o', '--output', help='Output file path')

    # test-case command
    test_case_parser = subparsers.add_parser('test-case', help='Generate test cases')
    test_case_parser.add_argument('file', help='Code file to generate test cases for')

    args = parser.parse_args()

    if args.command == 'init':
        await cmd_init(args)
    elif args.command == 'gen':
        await cmd_gen(args)
    elif args.command == 'review':
        await cmd_review(args)
    elif args.command == 'debug':
        await cmd_debug(args)
    elif args.command == 'status':
        await cmd_status(args)
    elif args.command == 'req':
        await cmd_req(args)
    elif args.command == 'test-doc':
        await cmd_test_doc(args)
    elif args.command == 'test-case':
        await cmd_test_case(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    asyncio.run(main())