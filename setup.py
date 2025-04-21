"""
Setup script for Hermes Ingestor package.
"""

from setuptools import setup, find_packages
import os
import re

# Get package version from __init__.py
with open(os.path.join("src", "__init__.py"), "r") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

# Get long description from README.md
with open("README.md", "r") as f:
    long_description = f.read()

# Get requirements from requirements.txt
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="hermes-ingestor",
    version=version,
    description="Document processing and embedding service for knowledge bases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hermes",
    author_email="info@example.com",
    url="https://github.com/user/hermes-ingestor",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hermes-ingestor=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 