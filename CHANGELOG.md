# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Real-time pricing API integration
- Cost optimization recommendations
- Budget alerts and thresholds
- Historical cost tracking
- Terraform Cloud/Enterprise integration
- Web UI for cost visualization
- Multi-cloud comparison

## [0.1.0] - 2026-02-25

### Added
- Initial release of IONOS FinOps
- Terraform file parsing support (.tf files)
- Terraform plan file parsing support (.tfplan files)
- Cost calculation for IONOS Cloud resources:
  - Compute: Servers, Cubes, vCPU servers
  - Storage: Volumes, S3 buckets, Backup units
  - Network: Load balancers, IP blocks
  - Database: PostgreSQL, MongoDB clusters
- Multiple output formats:
  - Rich table format for terminal
  - JSON format for programmatic use
  - HTML format for reports
- CLI interface with `breakdown` command
- Pricing data for de/fra region
- Custom pricing configuration support
- Comprehensive test suite
- Example Terraform configurations
- Full documentation (README, CONTRIBUTING, examples)
- MIT License

### Technical Details
- Python 3.8+ support
- HCL2 parsing for Terraform files
- Rich library for beautiful terminal output
- Click for CLI interface
- Jinja2 for HTML report generation
- Pydantic for data validation

[Unreleased]: https://github.com/yourusername/ionos-finops/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/ionos-finops/releases/tag/v0.1.0
