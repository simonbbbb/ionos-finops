from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ionos-finops",
    version="0.1.0",
    author="IONOS FinOps Contributors",
    description="Cost estimation tool for IONOS Cloud infrastructure defined in Terraform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ionos-finops",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-hcl2>=4.3.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "jinja2>=3.1.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
            "types-requests>=2.31.0",
            "types-pyyaml>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ionos-finops=ionos_finops.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ionos_finops": ["pricing_data/*.json", "templates/*.html"],
    },
)
