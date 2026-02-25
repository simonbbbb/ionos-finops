#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual pricing update script for local development

Usage:
    python scripts/manual_pricing_update.py [--force] [--region REGION]

Options:
    --force     Force update even if no changes detected
    --region    Update specific region only (default: all regions)
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.update_pricing import PricingUpdater


def main():
    parser = argparse.ArgumentParser(description="Manual pricing update script")
    parser.add_argument("--force", action="store_true", help="Force update even if no changes detected")
    parser.add_argument("--region", help="Update specific region only")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing pricing data")
    
    args = parser.parse_args()
    
    # Check for API token
    api_token = os.getenv("IONOS_TOKEN")
    if not api_token:
        print("❌ Error: IONOS_TOKEN environment variable not set")
        print("Set it with: export IONOS_TOKEN=your_token")
        return 1
    
    print("🚀 Starting manual pricing update...")
    
    updater = PricingUpdater(api_token, args.force)
    
    if args.validate_only:
        print("🔍 Validating existing pricing data...")
        if updater.validate_pricing_data():
            print("✅ All pricing data is valid")
            return 0
        else:
            print("❌ Pricing data validation failed")
            return 1
    
    try:
        if args.region:
            print("Updating pricing for region: {}".format(args.region))
            # Get base pricing
            from ionos_finops.pricing.api import IonosPricingAPI
            api = IonosPricingAPI(api_token)
            base_pricing = api.get_all_pricing("de/fra")
            
            # Update specific region
            changes = updater._update_region_pricing(args.region, base_pricing)
            if changes:
                print("Updated pricing for {}".format(args.region))
            else:
                print("No changes for {}".format(args.region))
        else:
            print("Updating pricing for all regions...")
            changes = updater.run()
            if changes:
                print("Pricing data updated")
            else:
                print("No pricing changes detected")
        
        # Validate updated pricing
        print("Validating updated pricing data...")
        if updater.validate_pricing_data():
            print("Pricing validation passed")
        else:
            print("Pricing validation failed")
            return 1
        
        return 0
    
    except Exception as e:
        print("Error: {}".format(e))
        return 1


if __name__ == "__main__":
    exit(main())
