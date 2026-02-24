from setuptools import setup, find_packages

# Read the requirements file
with open("requirements.txt") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read the README for long description
long_description = """
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework

The DCAE framework combines BMAD (Business Manager, Architect, Developer) role-based workflow,
MassGen (multi-model consensus) for quality validation, and Superpowers (methodological
enforcement) for disciplined execution in a unified development workflow.

Key Features:
- Role-based workflow with specialized agents (Business, Architect, Developer)
- Multi-model consensus validation for quality assurance
- Configurable discipline levels (Fast/Balanced/Strict modes)
- Seamless integration with multiple LLM providers (OpenAI, Anthropic, Qwen, GLM)
- Methodology enforcement through Superpowers system
- Project initialization and state management
"""

setup(
    name="dcae-framework",
    version="1.0.0",
    author="DCAE Development Team",
    author_email="dcae@example.com",
    description="Disciplined Consensus-Driven Agentic Engineering Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dcae/dcae-framework",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dcae=dcae_cli:main",
        ],
    },
    keywords="ai, development, workflow, agentic, bmad, dcae",
    project_urls={
        "Bug Reports": "https://github.com/dcae/dcae-framework/issues",
        "Source": "https://github.com/dcae/dcae-framework/",
    },
)