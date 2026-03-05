from setuptools import setup, find_packages

setup(
    name="dcae",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Add dependencies as needed
    ],
    author="DCAE Development Team",
    description="Development-Centric AI Engineering Framework",
    python_requires=">=3.7",
)