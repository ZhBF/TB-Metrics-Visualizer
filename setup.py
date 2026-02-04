#!/usr/bin/env python3
"""Setup script for TB-Metrics-Visualizer."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tb-metrics-visualizer",
    version="0.1.0",
    author="Your Name",
    description="A powerful batch visualization tool for aggregating and comparing TensorBoard scalar metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/TB-Metrics-Visualizer",
    py_modules=["main"],
    python_requires=">=3.6",  # 放宽到 Python 3.6+
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tb-visualizer=main:main",
            "tbviz=main:main",  # 短别名
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
