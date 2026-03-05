from setuptools import setup, find_packages

setup(
    name="dcae",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Dependencies would be added here in a real project
        # For example:
        # "requests>=2.25.0",
        # "click>=8.0.0",
        # "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dcae=dcae.cli:main",
        ],
    },
    author="DCAE Development Team",
    description="Disciplined Consensus-Driven Agentic Engineering Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/xylgz1989/DCAE",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
)