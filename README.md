# IONOS FinOps

[![PyPI version](https://badge.fury.io/py/ionos-finops.svg)](https://badge.fury.io/py/ionos-finops)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**IONOS FinOps** is an open-source cost estimation tool for IONOS Cloud infrastructure defined in Terraform. Similar to Infracost but specifically designed for IONOS, it provides 100% accurate pricing calculations for your infrastructure before deployment.

📦 **Published on PyPI**: https://pypi.org/project/ionos-finops/

## Features

- 🎯 **Accurate Pricing**: Calculate exact costs based on IONOS's current pricing
- 📊 **Terraform Integration**: Parse Terraform files and state to extract IONOS resources
- 💰 **Cost Breakdown**: Detailed cost analysis per resource and resource type
- 🔄 **Diff Support**: Compare costs between Terraform plans
- 📈 **Multiple Output Formats**: JSON, Table, HTML reports
- 🌍 **Multi-Region Support**: Pricing for all IONOS data center locations
- 🔌 **CI/CD Integration**: Easy integration into your deployment pipelines

## Supported IONOS Resources

- **Compute**: Servers (VMs), Cubes, VCPUs, RAM
- **Storage**: Block Storage, Object Storage (S3)
- **Networking**: Load Balancers, IP Addresses, Network Bandwidth
- **Databases**: DBaaS (PostgreSQL, MongoDB, MySQL, MariaDB)
- **Kubernetes**: Managed Kubernetes clusters, node pools
- **Backup**: Backup Units

## Installation

### From PyPI (Recommended)

```bash
pip install ionos-finops
```

### From Source

```bash
git clone https://github.com/simonbbbb/ionos-finops.git
cd ionos-finops
pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Calculate costs from Terraform directory
ionos-finops breakdown --path /path/to/terraform

# Calculate costs from Terraform plan
terraform plan -out=plan.tfplan
ionos-finops breakdown --plan-file plan.tfplan

# Output as JSON
ionos-finops breakdown --path . --format json

# Compare costs between current and planned state
ionos-finops diff --path .
```

### Example Output

```
Project: my-ionos-infrastructure
Region: de/fra

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Resource                                    Monthly Cost    Yearly Cost      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ionos_server.web_server                    €45.00          €540.00          │
│   - 2 vCPUs                                 €20.00          €240.00          │
│   - 4 GB RAM                                €15.00          €180.00          │
│   - 50 GB Storage                           €10.00          €120.00          │
│                                                                               │
│ ionos_volume.data_volume                   €30.00          €360.00          │
│   - 200 GB SSD Storage                      €30.00          €360.00          │
│                                                                               │
│ ionos_loadbalancer.main_lb                 €25.00          €300.00          │
│                                                                               │
│ ionos_ipblock.public_ips                   €5.00           €60.00           │
│   - 2 IPv4 addresses                        €5.00           €60.00           │
├─────────────────────────────────────────────────────────────────────────────┤
│ TOTAL                                       €105.00         €1,260.00        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Configuration

Create a `.ionos-finops.yml` file in your project root:

```yaml
# IONOS API credentials (optional, for real-time pricing updates)
api_url: https://api.ionos.com/cloudapi/v6
api_token: ${IONOS_TOKEN}

# Default region
default_region: de/fra

# Currency
currency: EUR

# Pricing update frequency (in hours)
pricing_cache_ttl: 24

# Custom pricing overrides (optional)
custom_pricing:
  ionos_server:
    vcpu_hourly: 0.01
    ram_gb_hourly: 0.005
```

## CI/CD Integration

### GitHub Actions

```yaml
name: IONOS Cost Estimation

on: [pull_request]

jobs:
  cost-estimate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
      
      - name: Install IONOS FinOps
        run: pip install ionos-finops
      
      - name: Terraform Plan
        run: terraform plan -out=plan.tfplan
      
      - name: Calculate Costs
        run: ionos-finops breakdown --plan-file plan.tfplan --format json > costs.json
      
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const costs = JSON.parse(fs.readFileSync('costs.json', 'utf8'));
            // Add comment logic here
```

### GitLab CI

```yaml
ionos-cost-estimate:
  stage: plan
  script:
    - pip install ionos-finops
    - terraform plan -out=plan.tfplan
    - ionos-finops breakdown --plan-file plan.tfplan
  only:
    - merge_requests
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/simonbbbb/ionos-finops.git
cd ionos-finops

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
flake8 .
mypy .
```

### Project Structure

```
ionos-finops/
├── ionos_finops/
│   ├── __init__.py
│   ├── cli.py                 # CLI interface
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── terraform.py       # Terraform file parser
│   │   └── hcl.py            # HCL parsing utilities
│   ├── pricing/
│   │   ├── __init__.py
│   │   ├── data.py           # Pricing data structures
│   │   ├── api.py            # IONOS API integration
│   │   └── calculator.py     # Cost calculation engine
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── base.py           # Base resource class
│   │   ├── compute.py        # Compute resources
│   │   ├── storage.py        # Storage resources
│   │   ├── network.py        # Network resources
│   │   └── database.py       # Database resources
│   └── output/
│       ├── __init__.py
│       ├── table.py          # Table formatter
│       ├── json.py           # JSON formatter
│       └── html.py           # HTML report generator
├── tests/
├── examples/
├── pricing_data/             # Static pricing data
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Pricing Data

Pricing data is maintained manually based on IONOS website pricing, with comprehensive validation and community contribution processes.

### ⚠️ **Important: IONOS API Limitations**

**IONOS does not provide a public pricing API.** Their APIs focus on account-specific billing data rather than public pricing catalogs.

### 📊 **Current Pricing Data**

| Region | Location | Currency | Status | Source |
|--------|----------|----------|--------|--------|
| de/fra | Frankfurt | EUR | ✅ Current | Manual |
| de/ber | Berlin | EUR | ✅ Current | Manual |
| de/fra2 | Frankfurt 2 | EUR | ✅ Current | Manual |
| gb/lhr | London | GBP | ✅ Current | Manual |
| gb/wor | Worchester | GBP | ✅ Current | Manual |
| fr/par | Paris | EUR | ✅ Current | Manual |
| es/log | Logroño | EUR | ✅ Current | Manual |
| us/las | Las Vegas | USD | ✅ Current | Manual |
| us/ewr | Newark | USD | ✅ Current | Manual |
| us/kc | Lenexa | USD | ✅ Current | Manual |

### 🛠️ **Manual Update Process**

```bash
# Validate current pricing data
make validate-pricing

# Manual update workflow
# 1. Check IONOS website pricing
# 2. Update pricing files manually
# 3. Validate changes
make validate-pricing

# Test with sample infrastructure
ionos-finops breakdown --path examples/
```

### 🤝 **Community Contributions**

**Help keep pricing current!** If you notice pricing changes on the IONOS website:

1. **Check Current Pricing**: Visit [IONOS Pricing Calculator](https://www.ionos.com/enterprise-cloud/pricing)
2. **Update Files**: Edit relevant pricing files in `ionos_finops/pricing_data/`
3. **Validate**: Run `make validate-pricing`
4. **Test**: Verify with sample Terraform files
5. **Submit PR**: Create pull request with pricing changes

### 🔍 **Pricing Validation**

The tool includes comprehensive pricing validation:

```bash
# Validate all pricing data
make validate-pricing

# Check pricing API status
python scripts/check_pricing_status.py

# Run pricing validation tests
pytest tests/test_pricing_validation.py -v
```

### 📖 **Documentation**

See [docs/pricing-updates.md](docs/pricing-updates.md) for detailed pricing update procedures and limitations.

## Roadmap

- [ ] Support for all IONOS Terraform resources
- [ ] Real-time pricing API integration
- [ ] Cost optimization recommendations
- [ ] Budget alerts and thresholds
- [ ] Historical cost tracking
- [ ] Multi-cloud comparison (IONOS vs AWS/Azure/GCP)
- [ ] Terraform Cloud/Enterprise integration
- [ ] Web UI for cost visualization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by [Infracost](https://www.infracost.io/)
- Built for the IONOS Cloud community
- Pricing data sourced from [IONOS Cloud Pricing](https://www.ionos.com/enterprise-cloud/pricing)

## Support

- 📖 [Documentation](https://github.com/simonbbbb/ionos-finops/wiki)
- 🐛 [Issue Tracker](https://github.com/simonbbbb/ionos-finops/issues)
- 💬 [Discussions](https://github.com/simonbbbb/ionos-finops/discussions)

## Related Projects

This project supports and complements larger infrastructure cost management initiatives. If you're using Infracost for multi-cloud environments, IONOS FinOps provides the same level of accuracy specifically for IONOS Cloud resources.

---

Made with ❤️ for the IONOS Cloud community
