# Contributing to IONOS FinOps

Thank you for your interest in contributing to IONOS FinOps! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Terraform version** and IONOS provider version
- **IONOS FinOps version**
- **Sample Terraform files** (sanitized of sensitive data)
- **Error messages** and logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** and motivation
- **Expected behavior** and benefits
- **Possible implementation** approach (optional)

### Adding Support for New Resources

To add support for a new IONOS resource:

1. Create a new resource class in `ionos_finops/resources/`
2. Add pricing data in `pricing_data/`
3. Update the parser to recognize the resource
4. Add tests in `tests/resources/`
5. Update documentation

Example:

```python
# ionos_finops/resources/compute.py
from .base import Resource

class IonosServer(Resource):
    resource_type = "ionos_server"
    
    def calculate_cost(self):
        vcpu_cost = self.config.get('cores', 0) * self.pricing['vcpu_hourly']
        ram_cost = self.config.get('ram', 0) * self.pricing['ram_gb_hourly']
        storage_cost = self.config.get('storage_size', 0) * self.pricing['storage_gb_hourly']
        
        return {
            'hourly': vcpu_cost + ram_cost + storage_cost,
            'monthly': (vcpu_cost + ram_cost + storage_cost) * 730,
            'breakdown': {
                'vcpu': vcpu_cost * 730,
                'ram': ram_cost * 730,
                'storage': storage_cost * 730
            }
        }
```

### Updating Pricing Data

Pricing data should be accurate and up-to-date. To update pricing:

1. Verify pricing from official IONOS sources
2. Update `pricing_data/[region].json`
3. Include source URL and date in commit message
4. Run tests to ensure calculations are correct

### Pull Request Process

1. **Fork** the repository and create your branch from `main`
2. **Install** development dependencies: `pip install -e ".[dev]"`
3. **Make** your changes following the code style guidelines
4. **Add tests** for new functionality
5. **Run tests**: `pytest`
6. **Run linters**: `black .`, `flake8 .`, `mypy .`
7. **Update documentation** if needed
8. **Commit** with clear, descriptive messages
9. **Push** to your fork and submit a pull request

### Pull Request Guidelines

- **One feature per PR**: Keep PRs focused on a single feature or fix
- **Write tests**: Ensure new code is covered by tests
- **Update docs**: Keep documentation in sync with code changes
- **Follow style**: Use Black for formatting, follow PEP 8
- **Descriptive commits**: Write clear commit messages
- **Link issues**: Reference related issues in PR description

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ionos-finops.git
cd ionos-finops

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [type hints](https://docs.python.org/3/library/typing.html) where appropriate
- Maximum line length: 100 characters (Black default)

### Naming Conventions

- **Classes**: PascalCase (e.g., `IonosServer`)
- **Functions/Methods**: snake_case (e.g., `calculate_cost`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_REGION`)
- **Private methods**: prefix with underscore (e.g., `_internal_method`)

### Documentation

- Use docstrings for all public modules, classes, and functions
- Follow [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings

```python
def calculate_monthly_cost(hourly_cost: float, hours_per_month: int = 730) -> float:
    """Calculate monthly cost from hourly rate.
    
    Args:
        hourly_cost: The hourly cost in the configured currency
        hours_per_month: Number of hours per month (default: 730)
        
    Returns:
        The calculated monthly cost
        
    Example:
        >>> calculate_monthly_cost(0.05)
        36.5
    """
    return hourly_cost * hours_per_month
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ionos_finops --cov-report=html

# Run specific test file
pytest tests/test_calculator.py

# Run specific test
pytest tests/test_calculator.py::test_server_cost_calculation
```

### Writing Tests

- Place tests in `tests/` directory
- Mirror the source structure
- Use descriptive test names
- Test edge cases and error conditions
- Use fixtures for common setup

```python
import pytest
from ionos_finops.resources.compute import IonosServer

def test_server_cost_calculation():
    """Test basic server cost calculation."""
    config = {
        'cores': 2,
        'ram': 4,
        'storage_size': 50
    }
    pricing = {
        'vcpu_hourly': 0.01,
        'ram_gb_hourly': 0.005,
        'storage_gb_hourly': 0.0001
    }
    
    server = IonosServer('test-server', config, pricing)
    cost = server.calculate_cost()
    
    assert cost['hourly'] == 0.035
    assert cost['monthly'] == 25.55
```

## Project Structure

```
ionos-finops/
├── ionos_finops/          # Main package
│   ├── cli.py            # Command-line interface
│   ├── parser/           # Terraform parsing
│   ├── pricing/          # Pricing logic
│   ├── resources/        # Resource definitions
│   └── output/           # Output formatters
├── tests/                # Test suite
├── examples/             # Example Terraform files
├── pricing_data/         # Pricing data files
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(resources): add support for ionos_k8s_cluster

Add cost calculation for Kubernetes clusters including node pools
and control plane costs.

Closes #123
```

```
fix(parser): handle missing optional attributes

The parser was failing when optional attributes were not present
in the Terraform configuration. Now defaults to None.

Fixes #456
```

## Release Process

Releases are managed by maintainers. The process:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create release tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will build and publish to PyPI

## Getting Help

- **Documentation**: Check the [Wiki](https://github.com/yourusername/ionos-finops/wiki)
- **Discussions**: Use [GitHub Discussions](https://github.com/yourusername/ionos-finops/discussions)
- **Issues**: Search existing [issues](https://github.com/yourusername/ionos-finops/issues)

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

Thank you for contributing to IONOS FinOps! 🎉
