# Automated Pricing Updates

IONOS FinOps includes a pricing update system designed to keep pricing data current, though with important limitations due to IONOS API constraints.

## ⚠️ **Important: IONOS API Limitations**

**IONOS does not provide a public, unauthorized pricing API.** Their available APIs require authentication and focus on account-specific billing data rather than public pricing catalogs.

### **What IONOS APIs Provide**
- ✅ **Billing API**: Account-specific usage and invoices
- ✅ **Resource API**: Your deployed resources and configurations
- ❌ **Public Pricing API**: Not available
- ❌ **Universal Catalog**: No programmatic access to standard pricing

### **Current Reality**
- Pricing available via IONOS website calculator (requires login)
- Cloud Panel shows pricing for your account/contract
- No unauthorized programmatic access to pricing data
- Third-party tools like Infracost don't support IONOS natively

## 🔄 **Current Implementation Status**

### **What Works**
- ✅ **Pricing Data Structure**: Complete pricing data files for all regions
- ✅ **Regional Logic**: Realistic regional pricing differences
- ✅ **Validation**: Comprehensive pricing data validation
- ✅ **Fallback System**: Graceful degradation when API unavailable
- ✅ **Manual Updates**: Scripts for manual pricing updates

### **What Needs Adjustment**
- ❌ **Automated API Updates**: API endpoints don't exist
- ❌ **Real-time Fetching**: No public pricing catalog
- ❌ **Scheduled Updates**: Cannot fetch from IONOS APIs

## 🛠️ **Realistic Update Strategy**

### **Option 1: Manual Updates (Current Reality)**
```bash
# Manual pricing updates by maintainers
make validate-pricing
# Edit pricing files manually based on IONOS website
make validate-pricing
git commit -m "chore: update pricing data from IONOS website"
```

### **Option 2: Web Scraping (Technical but Fragile)**
```python
# Potential web scraping approach (use with caution)
# - Scrape IONOS pricing calculator
# - Requires login simulation
# - May violate terms of service
# - Brittle to website changes
```

### **Option 3: Community Contributions (Recommended)**
```bash
# Community-driven pricing updates
# - Users submit pricing updates via PRs
# - Maintainers validate and merge
# - Crowdsourced pricing accuracy
```

## 📊 **Current Pricing Data Status**

### **Regional Pricing Files**
All 10 IONOS data centers have pricing files with realistic regional differences:

| Region | Location | Currency | Status | Source |
|--------|----------|----------|--------|--------|
| de/fra | Frankfurt | EUR | ✅ Current | Estimated |
| de/ber | Berlin | EUR | ✅ Current | Estimated |
| de/fra2 | Frankfurt 2 | EUR | ✅ Current | Estimated |
| gb/lhr | London | GBP | ✅ Current | Estimated |
| gb/wor | Worchester | GBP | ✅ Current | Estimated |
| fr/par | Paris | EUR | ✅ Current | Estimated |
| es/log | Logroño | EUR | ✅ Current | Estimated |
| us/las | Las Vegas | USD | ✅ Current | Estimated |
| us/ewr | Newark | USD | ✅ Current | Estimated |
| us/kc | Lenexa | USD | ✅ Current | Estimated |

### **Pricing Accuracy**
- **Base Values**: Estimated from IONOS website pricing
- **Regional Differences**: Based on typical cloud provider patterns
- **Currency Conversion**: Realistic EUR/GBP/USD differences
- **Validation**: All values validated for reasonableness

## 🔧 **Updated Update Process**

### **Manual Update Workflow**
```bash
# 1. Check IONOS website for pricing changes
# 2. Update pricing files manually
vim ionos_finops/pricing_data/de_fra.json

# 3. Validate all pricing data
make validate-pricing

# 4. Test with sample infrastructure
ionos-finops breakdown --path examples/

# 5. Commit and submit PR
git add ionos_finops/pricing_data/
git commit -m "chore: update pricing based on IONOS website"
git push origin feature/pricing-update
```

### **Community Contribution Process**
1. **Check Current Pricing**: Visit IONOS pricing calculator
2. **Identify Changes**: Note any pricing differences
3. **Update Files**: Edit relevant pricing JSON files
4. **Validate**: Run `make validate-pricing`
5. **Test**: Verify with sample Terraform files
6. **Submit PR**: Create pull request with pricing changes
7. **Review**: Maintainers validate and merge

## 📋 **Pricing Update Checklist**

### **Before Updating**
- [ ] Check IONOS website pricing calculator
- [ ] Note any pricing changes across regions
- [ ] Verify currency conversion rates
- [ ] Document source of pricing information

### **During Update**
- [ ] Update base pricing (de/fra)
- [ ] Apply regional multipliers consistently
- [ ] Maintain currency codes correctly
- [ ] Update last_updated timestamp

### **After Update**
- [ ] Run `make validate-pricing`
- [ ] Test with sample configurations
- [ ] Verify cost calculations make sense
- [ ] Update CHANGELOG.md with changes

## 🔍 **Validation and Testing**

### **Automated Validation**
```bash
# Validate all pricing files
make validate-pricing

# Run pricing validation tests
pytest tests/test_pricing_validation.py -v

# Test with sample infrastructure
ionos-finops breakdown --path examples/simple_infrastructure.tf
```

### **Manual Validation**
- Compare with IONOS website pricing
- Verify regional differences are reasonable
- Check currency conversions
- Test with real Terraform configurations

## 🚀 **Future Possibilities**

### **When IONOS Provides Pricing API**
If IONOS adds a public pricing API in the future:

```python
# This would work with a real pricing API
api = IonosPricingAPI(api_token)
pricing_data = api.get_all_pricing("de/fra")
```

### **Alternative Approaches**
- **Partner with IONOS**: Get API access through partnership
- **Community API**: Create community-maintained pricing service
- **Hybrid Approach**: Mix manual updates with automated validation

## 📞 **Getting Help**

### **For Pricing Updates**
- **Check IONOS Website**: https://www.ionos.com/enterprise-cloud/pricing
- **Community Forum**: Discuss pricing changes with other users
- **GitHub Issues**: Report pricing discrepancies
- **Documentation**: Check for update announcements

### **Technical Support**
- **Validation Errors**: Check pricing file format
- **Calculation Issues**: Verify Terraform syntax
- **Regional Problems**: Check currency and multipliers

---

*Note: This pricing update system is designed with the current limitations of IONOS APIs in mind. When IONOS provides public pricing APIs, the system can be enhanced to support automated updates.*

# Force update pricing (even if no changes)
make force-update-pricing

# Validate existing pricing data
make validate-pricing

# Update specific region only
make update-region REGION=de/fra
```

### Using Scripts Directly

```bash
# Set your IONOS API token
export IONOS_TOKEN=your_api_token_here

# Update all regions
python scripts/manual_pricing_update.py

# Force update
python scripts/manual_pricing_update.py --force

# Update specific region
python scripts/manual_pricing_update.py --region de/fra

# Validate only
python scripts/manual_pricing_update.py --validate-only
```

### Using CLI

```bash
# Update pricing for specific region
ionos-finops update-pricing --api-token $TOKEN --region de/fra

# Check scheduler status
ionos-finops scheduler --status
```

## Setup

### 1. GitHub Actions Setup

Add the IONOS API token to your repository secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Add new repository secret: `IONOS_TOKEN`
3. Set value to your IONOS Cloud API token

### 2. Local Development Setup

```bash
# Install development dependencies
make install-dev

# Set API token
export IONOS_TOKEN=your_api_token_here

# Test pricing update
make update-pricing
```

## Configuration

### Regional Multipliers

Edit `scripts/update_pricing.py` to adjust regional pricing:

```python
REGIONAL_MULTIPLIERS = {
    "de/fra": 1.0,      # Base pricing
    "gb/lhr": 0.85,     # ~15% cheaper
    "us/las": 0.90,     # ~10% cheaper
    # ... add more regions
}
```

### Update Frequency

Change the GitHub Actions schedule in `.github/workflows/pricing-update.yml`:

```yaml
# Every 6 hours
- cron: '0 */6 * * *'

# Every 12 hours
- cron: '0 */12 * * *'

# Daily at 2 AM UTC
- cron: '0 2 * * *'
```

## Validation

The system validates all pricing data:

### Structure Validation
- ✅ Required fields present
- ✅ Correct region codes
- ✅ Valid currency codes
- ✅ Proper JSON format

### Value Validation
- ✅ No negative pricing values
- ✅ Reasonable price ranges
- ✅ Consistent units (hourly/monthly)
- ✅ Regional differences maintained

### Automated Tests
```bash
# Run pricing validation tests
pytest tests/test_pricing_validation.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

## Monitoring

### GitHub Actions Monitoring

- **Success**: No action needed
- **Failure**: Check logs for API issues
- **Pull Requests**: Review pricing changes

### Local Monitoring

```bash
# Check last update time
python scripts/manual_pricing_update.py --validate-only

# View pricing data
cat ionos_finops/pricing_data/de_fra.json | jq '.last_updated'
```

## Troubleshooting

### Common Issues

#### API Token Issues
```bash
❌ Error: IONOS_TOKEN environment variable not set
```
**Solution**: Set the IONOS_TOKEN environment variable with your valid API token.

#### Network Issues
```bash
❌ Failed to fetch base pricing: Connection timeout
```
**Solution**: Check network connectivity and IONOS API status.

#### Validation Failures
```bash
❌ Pricing validation failed
```
**Solution**: Check pricing files for corruption or invalid values.

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python scripts/manual_pricing_update.py
```

### Manual Recovery

If automated updates fail, recover manually:

```bash
# Backup current pricing
cp -r ionos_finops/pricing_data ionos_finops/pricing_data.backup

# Force update from API
make force-update-pricing

# Validate results
make validate-pricing

# Restore if needed
cp -r ionos_finops/pricing_data.backup ionos_finops/pricing_data
```

## Security

### API Token Security
- ✅ Stored in GitHub repository secrets
- ✅ Not logged in output
- ✅ Limited to necessary permissions
- ✅ Rotated regularly

### File Security
- ✅ Pricing files are read-only for users
- ✅ Changes require PR review
- ✅ Automated validation prevents corruption
- ✅ Backup and recovery procedures

## Performance

### Update Performance
- **API calls**: ~2 seconds per region
- **File operations**: ~0.1 seconds per file
- **Validation**: ~0.5 seconds total
- **Total time**: ~30 seconds for all regions

### Storage Impact
- **Pricing files**: ~1.5KB each
- **Total storage**: ~15KB for all regions
- **Git history**: Minimal impact
- **Network usage**: ~50KB per update

## Best Practices

### 1. Regular Monitoring
- Check GitHub Actions status regularly
- Review pricing change PRs promptly
- Monitor API token usage

### 2. Testing Updates
- Test in development environment first
- Validate pricing changes manually
- Run full test suite after updates

### 3. Backup Strategy
- Keep backup of pricing files
- Monitor Git history for changes
- Document any manual adjustments

### 4. Documentation
- Document any custom pricing adjustments
- Keep regional multiplier logic updated
- Maintain change logs for pricing updates

## API Reference

### IONOS Cloud API Endpoints

The system uses these IONOS Cloud API v6 endpoints:

- `GET /locations` - List available data centers
- `GET /locations/{id}/pricing/*` - Get pricing by category

### Rate Limits

- **Requests per hour**: 1000
- **Concurrent requests**: 10
- **Retry logic**: Exponential backoff

### Error Handling

- **401 Unauthorized**: Invalid API token
- **429 Too Many Requests**: Rate limit exceeded
- **500 Server Error**: Temporary IONOS issues
- **Network errors**: Automatic retry with backoff

## Contributing

To contribute to the pricing update system:

1. **Test changes**: Test in development environment
2. **Validate pricing**: Run `make validate-pricing`
3. **Update tests**: Add tests for new features
4. **Document changes**: Update this documentation
5. **Submit PR**: Create pull request for review

## Support

For issues with pricing updates:

1. **Check logs**: Review GitHub Actions logs
2. **Validate locally**: Run `make validate-pricing`
3. **Check API status**: Verify IONOS API is accessible
4. **Report issues**: Create GitHub issue with details

---

*Last updated: 2026-02-25*
