#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch real pricing data from IONOS Billing API

This script connects to your IONOS account and fetches the actual
pricing from your contract, then updates the local pricing files.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ionos_finops.pricing.billing_api import IonosBillingAPI, IonosBillingAPIError


def main():
    """Fetch real pricing from IONOS Billing API"""
    print("🔗 IONOS Real Pricing Fetcher")
    print("=" * 50)
    
    # Get credentials from environment or prompt
    username = os.getenv("IONOS_USERNAME")
    password = os.getenv("IONOS_PASSWORD")
    contract_id = os.getenv("IONOS_CONTRACT_ID")  
    
    if not all([username, password, contract_id]):
        print("❌ Missing required credentials:")
        print("   Set environment variables:")
        print("   export IONOS_USERNAME=your_email")
        print("   export IONOS_PASSWORD=your_password") 
        print("   export IONOS_CONTRACT_ID=your_contract_number")
        return 1
    
    try:
        # Initialize API client
        print(f"🔐 Connecting to IONOS Billing API...")
        print(f"   Username: {username}")
        print(f"   Contract ID: {contract_id}")
        
        api = IonosBillingAPI(username, password, contract_id)
        
        # Test connection
        print("🔍 Testing API access...")
        try:
            # Try to get profile first
            profile = api.get_profile()
            print("✅ Successfully connected to IONOS API")
        except Exception as e:
            print(f"⚠️  Profile access failed: {e}")
            print("   Trying products endpoint directly...")
            # Continue anyway, products might work
        
        # Get contract info
        print("\n📋 Fetching contract information...")
        contract_info = api.get_contract_info()
        print(f"   Customer ID: {contract_info.get('customer_id')}")
        print(f"   Total Products: {contract_info.get('total_products')}")
        print(f"   Liability: {contract_info.get('liability')}")
        
        # Get current pricing
        print("\n💰 Fetching real pricing data...")
        pricing_data = api.get_current_pricing()
        
        print(f"   Region: {pricing_data.get('region')}")
        print(f"   Currency: {pricing_data.get('currency')}")
        print(f"   Source: {pricing_data.get('source')}")
        
        # Show some sample pricing
        compute = pricing_data.get('compute', {})
        if compute:
            print(f"   vCPU: €{compute.get('vcpu_hourly', 0):.4f}/hour")
            print(f"   RAM: €{compute.get('ram_gb_hourly', 0):.4f}/GB/hour")
        
        storage = pricing_data.get('storage', {})
        if storage:
            print(f"   SSD: €{storage.get('storage_ssd_gb_hourly', 0):.4f}/GB/hour")
            print(f"   S3: €{storage.get('s3_storage_gb_monthly', 0):.4f}/GB/month")
        
        # Save pricing data
        print("\n💾 Saving pricing data...")
        pricing_dir = Path(__file__).parent.parent / "ionos_finops" / "pricing_data"
        pricing_dir.mkdir(parents=True, exist_ok=True)
        
        # Update main pricing file
        pricing_file = pricing_dir / "de_fra.json"
        with open(pricing_file, 'w', encoding='utf-8') as f:
            json.dump(pricing_data, f, indent=2, sort_keys=True)
        
        print(f"   Saved to: {pricing_file}")
        
        # Validate the saved file
        print("\n🔍 Validating saved pricing data...")
        with open(pricing_file, 'r') as f:
            loaded_data = json.load(f)
        
        required_fields = ["region", "currency", "compute", "storage"]
        missing_fields = [field for field in required_fields if field not in loaded_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return 1
        
        print("✅ Pricing data validation passed")
        
        # Show summary
        print("\n📊 Summary:")
        print(f"   ✅ Successfully fetched real IONOS pricing")
        print(f"   ✅ Updated {pricing_file}")
        print(f"   ✅ Validation passed")
        print(f"   ✅ Ready for accurate cost calculations")
        
        return 0
        
    except IonosBillingAPIError as e:
        print(f"❌ IONOS API Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
