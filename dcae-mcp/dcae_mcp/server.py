#!/usr/bin/env python3
"""
DCAE MCP Server - Model Context Protocol Server for DCAE Framework

This server enables Claude Code and other MCP-compatible agents to directly
invoke DCAE (Design-Code-Analyze-Evolve) TDD workflow tools.

Usage:
    # Start server via stdio
    python -m dcae_mcp.server

    # Configure in Claude Desktop / Claude Code:
    {
      "mcpServers": {
        "dcae": {
          "command": "python3",
          "args": ["-m", "dcae_mcp.server"]
        }
      }
    }
"""

import asyncio
import logging
from mcp.server import FastMCP

from dcae import DCAEFramework, DCAEResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dcae-mcp-server")

# Create MCP server instance
server = FastMCP("dcae")


# =============================================================================
# DCAE Tools
# =============================================================================

@server.tool()
async def tdd_run(
    task: str,
    test_file: str,
    source_file: str,
    project_root: str = ".",
    max_iterations: int = 10
) -> dict:
    """
    运行完整 TDD 流程 (DCAE cycle)
    
    执行完整的 Design-Code-Analyze-Evolve 循环，直到所有测试通过且覆盖率达标。
    
    Args:
        task: 任务描述或用户故事
        test_file: 测试文件路径 (例如：tests/test_feature.py)
        source_file: 源代码文件路径 (例如：src/feature.py)
        project_root: 项目根目录 (默认当前目录)
        max_iterations: 最大 TDD 迭代次数 (默认 10)
    
    Returns:
        包含测试状态、覆盖率、迭代次数和产物的字典
    """
    logger.info(f"Starting TDD run for task: {task}")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.run(test_file, source_file, max_iterations)
        result_dict = result.to_dict()
        result_dict["task"] = task
        
        logger.info(f"TDD run completed: status={result_dict['status']}")
        return result_dict
    
    except Exception as e:
        logger.error(f"TDD run failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "error",
            "error": str(e),
            "task": task
        }


@server.tool()
async def tdd_design(
    test_file: str,
    project_root: str = ".",
    test_cases: list = None
) -> dict:
    """
    TDD Design 阶段 - 创建失败的测试规范
    
    Phase 1: 编写测试用例，定义预期行为，建立验收标准。
    """
    logger.info(f"Starting DCAE Design phase: {test_file}")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.design(test_file, test_cases)
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Design phase failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "design",
            "error": str(e)
        }


@server.tool()
async def tdd_code(
    source_file: str,
    project_root: str = "."
) -> dict:
    """
    TDD Code 阶段 - 实现最小化代码以通过测试
    
    Phase 2: 编写刚好能让测试通过的最简单代码。
    """
    logger.info(f"Starting DCAE Code phase: {source_file}")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.code(source_file)
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Code phase failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "code",
            "error": str(e)
        }


@server.tool()
async def tdd_analyze(
    project_root: str = ".",
    coverage_threshold: float = 80.0
) -> dict:
    """
    TDD Analyze 阶段 - 检查代码质量和测试覆盖率
    
    Phase 3: 运行完整测试套件，检查覆盖率指标，审查代码风格。
    """
    logger.info(f"Starting DCAE Analyze phase, threshold: {coverage_threshold}%")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.analyze(coverage_threshold)
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Analyze phase failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "analyze",
            "error": str(e)
        }


@server.tool()
async def tdd_evolve(
    project_root: str = ".",
    optimize: bool = False
) -> dict:
    """
    TDD Evolve 阶段 - 重构代码而不改变行为
    
    Phase 4: 在测试保护下重构代码，提高代码质量。
    """
    logger.info(f"Starting DCAE Evolve phase, optimize: {optimize}")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.evolve(optimize)
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Evolve phase failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "evolve",
            "error": str(e)
        }


@server.tool()
async def tdd_init(
    project_name: str,
    project_root: str = "."
) -> dict:
    """
    初始化新的 DCAE 项目
    
    创建项目目录结构，包括 tests/、src/ 和 pytest 配置。
    """
    logger.info(f"Initializing DCAE project: {project_name}")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.init(project_name)
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Project initialization failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "init",
            "error": str(e)
        }


@server.tool()
async def tdd_status(project_root: str = ".") -> dict:
    """
    显示当前 DCAE 状态
    
    返回当前 TDD 阶段、迭代次数和文件路径。
    """
    logger.info("Getting DCAE status")
    
    try:
        dcae = DCAEFramework(project_root)
        result = dcae.status()
        return result.to_dict()
    
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {
            "status": "failed",
            "phase": "error",
            "error": str(e)
        }


# =============================================================================
# Resources
# =============================================================================

@server.resource("dcae://version")
async def get_version() -> str:
    """Get DCAE MCP Server version."""
    return "1.0.0"


@server.resource("dcae://tools")
async def get_tools() -> list:
    """Get list of available tools."""
    return [
        "tdd_run",
        "tdd_design",
        "tdd_code",
        "tdd_analyze",
        "tdd_evolve",
        "tdd_init",
        "tdd_status"
    ]


@server.resource("dcae://workflow")
async def get_workflow() -> dict:
    """Get DCAE workflow description."""
    return {
        "name": "DCAE TDD Workflow",
        "phases": [
            {"name": "Design", "tool": "tdd_design", "description": "Write failing tests (Red)"},
            {"name": "Code", "tool": "tdd_code", "description": "Implement to pass (Green)"},
            {"name": "Analyze", "tool": "tdd_analyze", "description": "Check quality"},
            {"name": "Evolve", "tool": "tdd_evolve", "description": "Refactor (Refactor)"}
        ],
        "quick_start": {"tool": "tdd_run", "description": "Run complete DCAE cycle"}
    }


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Main function - start MCP Server."""
    logger.info("Starting DCAE MCP Server...")
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
