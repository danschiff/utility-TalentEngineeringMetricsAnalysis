"""Setup configuration for TalentEngineeringMetricsAnalysis."""

from setuptools import setup, find_packages

setup(
    name="talent-engineering-metrics-analysis",
    version="0.1.0",
    description="A tool for analyzing Talent Engineering Metrics",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": ["pytest>=6.2.0"],
    },
)
