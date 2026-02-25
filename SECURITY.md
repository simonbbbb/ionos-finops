# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within IONOS FinOps, please send an email to the maintainers. All security vulnerabilities will be promptly addressed.

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

When reporting a vulnerability, please include:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Suggested fix** (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next release cycle

## Security Best Practices

When using IONOS FinOps:

1. **API Tokens**: Never commit API tokens to version control
   - Use environment variables: `export IONOS_TOKEN=your_token`
   - Use configuration files that are gitignored
   - Use secret management tools in CI/CD

2. **Terraform Files**: Sanitize sensitive data before sharing
   - Remove passwords, tokens, and secrets
   - Use Terraform variables for sensitive values
   - Review `.tfstate` files before sharing

3. **Configuration Files**: Keep `.ionos-finops.yml` private
   - Add to `.gitignore`
   - Use environment variable substitution
   - Don't share files with custom pricing that may be confidential

4. **File Permissions**: Ensure proper file permissions
   - Configuration files: `chmod 600 .ionos-finops.yml`
   - Terraform state: `chmod 600 *.tfstate`

5. **Dependencies**: Keep dependencies updated
   - Regularly run `pip install --upgrade ionos-finops`
   - Review security advisories for dependencies

## Known Security Considerations

### File Path Validation

The tool reads Terraform files from user-specified paths. While we validate paths, users should:
- Only run the tool on trusted Terraform configurations
- Be cautious when using the tool on files from untrusted sources
- Review file paths before processing

### HTML Output

When generating HTML reports:
- Output is intended for internal use only
- Do not expose HTML reports publicly without review
- Reports may contain infrastructure details

### Subprocess Execution

The tool uses `terraform show` to parse plan files:
- Ensure Terraform binary is from official sources
- Keep Terraform updated to latest version
- Run in isolated environments when processing untrusted plans

## Disclosure Policy

When a security vulnerability is fixed:

1. A security advisory will be published
2. Credit will be given to the reporter (if desired)
3. A CVE may be requested for significant vulnerabilities
4. Users will be notified through release notes

## Contact

For security concerns, please contact the maintainers through GitHub.
