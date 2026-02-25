#!/usr/bin/env python3
"""
Check IONOS pricing API status and current pricing data validity.

This script checks:
1. IONOS API limitations and availability
2. Current pricing data validation
3. Recommendations for pricing updates
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ionos_finops.pricing.api import IonosPricingAPI, IonosAPIError
from ionos_finops.pricing.data import PricingData


def main():
    """Check IONOS pricing API status and validate current pricing data"""
    print("🔍 IONOS FinOps - Pricing Status Check")
    print("=" * 50)
    
    # Check API status
    api_token = os.getenv("IONOS_TOKEN")
    if api_token:
        print("✅ IONOS_TOKEN found")
        api = IonosPricingAPI(api_token)
        
        # Check API token validity
        if api.validate_api_token():
            print("✅ IONOS API token is valid")
        else:
            print("❌ IONOS API token is invalid")
        
        # Get pricing API status
        status = api.get_pricing_api_status()
        print(f"\n📊 IONOS API Status:")
        print(f"   Public Pricing API: {'✅' if status['public_pricing_api'] else '❌'}")
        print(f"   Account Billing API: {'✅' if status['account_billing_api'] else '❌'}")
        
        print(f"\n⚠️  API Limitations:")
        for limitation in status['limitations']:
            print(f"   • {limitation}")
        
        print(f"\n💡 Recommended Alternatives:")
        for alternative in status['alternatives']:
            print(f"   • {alternative}")
        
        print(f"\n🔧 Current Implementation: {status['current_implementation']}")
        print(f"📝 Recommendation: {status['recommendation']}")
        
    else:
        print("⚠️  IONOS_TOKEN not found (expected for public pricing)")
        print("   IONOS does not provide public pricing APIs")
    
    print("\n" + "=" * 50)
    
    # Validate current pricing data
    print("📋 Validating Current Pricing Data")
    print("=" * 50)
    
    regions = ["de/fra", "de/ber", "de/fra2", "gb/lhr", "gb/wor", 
               "fr/par", "es/log", "us/las", "us/ewr", "us/kc"]
    
    all_valid = True
    for region in regions:
        try:
            pricing_data = PricingData(region=region)
            
            # Check if pricing file exists and is valid
            pricing = pricing_data.get_pricing("ionos_server")
            
            if pricing and len(pricing) > 0:
                # Check for reasonable pricing values
                vcpu_price = pricing.get("vcpu_hourly", 0)
                ram_price = pricing.get("ram_gb_hourly", 0)
                
                if 0.001 <= vcpu_price <= 0.05 and 0.001 <= ram_price <= 0.02:
                    print(f"✅ {region}: Valid pricing (vCPU: €{vcpu_price:.4f}/h, RAM: €{ram_price:.4f}/h)")
                else:
                    print(f"⚠️  {region}: Pricing may be unrealistic (vCPU: €{vcpu_price:.4f}/h, RAM: €{ram_price:.4f}/h)")
                    all_valid = False
            else:
                print(f"❌ {region}: No pricing data found")
                all_valid = False
                
        except Exception as e:
            print(f"❌ {region}: Error validating pricing - {e}")
            all_valid = False
    
    print("\n" + "=" * 50)
    
    # Summary and recommendations
    print("📊 Summary & Recommendations")
    print("=" * 50)
    
    if all_valid:
        print("✅ All pricing data is valid and reasonable")
        print("\n🔄 Recommended Update Process:")
        print("   1. Check IONOS website pricing calculator")
        print("   2. Compare with current pricing data")
        print("   3. Update if changes detected")
        print("   4. Submit PR with pricing updates")
    else:
        print("⚠️  Some pricing data may need attention")
        print("\n🔧 Immediate Actions:")
        print("   1. Review flagged pricing data")
        print("   2. Update unrealistic values")
        print("   3. Run: make validate-pricing")
    
    print(f"\n📅 Last Check: {datetime.now(timezone.utc).isoformat()}")
    print(f"📖 Documentation: docs/pricing-updates.md")
    
    return 0 if all_valid else 1


if __name__ == "__main__":
    exit(main())
