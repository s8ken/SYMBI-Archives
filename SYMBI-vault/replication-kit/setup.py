#!/usr/bin/env python3
"""
SYMBI Replication Kit Setup
A comprehensive toolkit for replicating SYMBI protocol research and A/B testing.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SYMBI Replication Kit for constitutional AI research and A/B testing"

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="symbi-replication-kit",
    version="1.0.0",
    author="SYMBI Core Protocol",
    author_email="research@symbi.world",
    description="Replication kit for SYMBI constitutional AI protocol research",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/symbi-world/replication-kit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
            "notebook>=6.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "symbi-ab-test=symbi_kit.cli:run_ab_test",
            "symbi-analyze=symbi_kit.cli:analyze_results",
            "symbi-validate=symbi_kit.cli:validate_receipts",
        ],
    },
    include_package_data=True,
    package_data={
        "symbi_kit": [
            "data/*.json",
            "templates/*.py",
            "schemas/*.json",
        ],
    },
    zip_safe=False,
)