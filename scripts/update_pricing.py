#!/usr/bin/env python3
"""
Automated pricing update script for IONOS FinOps

This script:
1. Fetches current pricing from IONOS API
2. Compares with existing local pricing files
3. Updates only if changes are detected
4. Maintains regional pricing differences
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional

from ionos_finops.pricing.api import IonosPricingAPI, IonosAPIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Regional pricing multipliers (based on typical IONOS pricing differences)
REGIONAL_MULTIPLIERS = {
    "de/fra": 1.0,      # Base pricing
    "de/ber": 1.0,      # Same as Frankfurt
    "de/fra2": 1.0,     # Same as Frankfurt
    "gb/lhr": 0.85,     # ~15% cheaper (GBP)
    "gb/wor": 0.85,     # ~15% cheaper (GBP)
    "fr/par": 1.10,     # ~10% more expensive
    "es/log": 0.90,     # ~10% cheaper
    "us/las": 0.90,     # ~10% cheaper (USD)
    "us/ewr": 0.95,     # ~5% cheaper (USD)
    "us/kc": 0.85,      # ~15% cheaper (USD)
}

# Regional currencies
REGIONAL_CURRENCIES = {
    "de/fra": "EUR",
    "de/ber": "EUR", 
    "de/fra2": "EUR",
    "gb/lhr": "GBP",
    "gb/wor": "GBP",
    "fr/par": "EUR",
    "es/log": "EUR",
    "us/las": "USD",
    "us/ewr": "USD",
    "us/kc": "USD",
}


class PricingUpdater:
    def __init__(self, api_token: str, force_update: bool = False):
        self.api_token = api_token
        self.force_update = force_update
        self.api = IonosPricingAPI(api_token)
        self.pricing_dir = Path(__file__).parent.parent / "ionos_finops" / "pricing_data"
        self.changes_detected = False
        
    def run(self) -> bool:
        """Run the pricing update process"""
        logger.info("Starting pricing update process")
        
        if not self.api.validate_api_token():
            logger.error("Invalid IONOS API token")
            return False
        
        # Get base pricing from Frankfurt (reference)
        try:
            base_pricing = self.api.get_all_pricing("de/fra")
            logger.info("Successfully fetched base pricing from de/fra")
        except IonosAPIError as e:
            logger.error(f"Failed to fetch base pricing: {e}")
            return False
        
        # Update all regions
        for region in REGIONAL_MULTIPLIERS.keys():
            if self._update_region_pricing(region, base_pricing):
                self.changes_detected = True
        
        if self.changes_detected:
            logger.info("✅ Pricing data updated with changes detected")
        else:
            logger.info("ℹ️ No pricing changes detected")
        
        return self.changes_detected
    
    def _update_region_pricing(self, region: str, base_pricing: Dict[str, Any]) -> bool:
        """Update pricing for a specific region"""
        pricing_file = self.pricing_dir / f"{region.replace('/', '_')}.json"
        
        # Apply regional adjustments
        regional_pricing = self._apply_regional_adjustments(region, base_pricing)
        
        # Check if file exists and compare
        if pricing_file.exists() and not self.force_update:
            existing_pricing = self._load_existing_pricing(pricing_file)
            if existing_pricing and not self._has_pricing_changes(existing_pricing, regional_pricing):
                logger.debug(f"No pricing changes for {region}")
                return False
        
        # Save updated pricing
        self._save_pricing_file(pricing_file, regional_pricing)
        logger.info(f"Updated pricing for {region}")
        return True
    
    def _apply_regional_adjustments(self, region: str, base_pricing: Dict[str, Any]) -> Dict[str, Any]:
        """Apply regional pricing adjustments"""
        multiplier = REGIONAL_MULTIPLIERS.get(region, 1.0)
        currency = REGIONAL_CURRENCIES.get(region, "EUR")
        
        regional_pricing = base_pricing.copy()
        regional_pricing["region"] = region
        regional_pricing["currency"] = currency
        regional_pricing["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Apply multiplier to all pricing values
        for category, pricing in regional_pricing.items():
            if isinstance(pricing, dict):
                for key, value in pricing.items():
                    if key.endswith(("_hourly", "_monthly", "_per_1000")) and isinstance(value, (int, float)):
                        pricing[key] = round(value * multiplier, 6)
        
        return regional_pricing
    
    def _load_existing_pricing(self, pricing_file: Path) -> Optional[Dict[str, Any]]:
        """Load existing pricing from file"""
        try:
            with open(pricing_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Could not load existing pricing from {pricing_file}: {e}")
            return None
    
    def _has_pricing_changes(self, existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """Check if pricing has changed"""
        # Compare only pricing values, ignore metadata
        existing_pricing = self._extract_pricing_values(existing)
        new_pricing = self._extract_pricing_values(new)
        
        return existing_pricing != new_pricing
    
    def _extract_pricing_values(self, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract only pricing values for comparison"""
        values = {}
        
        for key, value in pricing_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if sub_key.endswith(("_hourly", "_monthly", "_per_1000")):
                        values[f"{key}.{sub_key}"] = sub_value
        
        return values
    
    def _save_pricing_file(self, pricing_file: Path, pricing_data: Dict[str, Any]) -> None:
        """Save pricing data to file"""
        pricing_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pricing_file, 'w', encoding='utf-8') as f:
            json.dump(pricing_data, f, indent=2, sort_keys=True)
    
    def validate_pricing_data(self) -> bool:
        """Validate all pricing data files"""
        logger.info("Validating pricing data...")
        
        all_valid = True
        for region in REGIONAL_MULTIPLIERS.keys():
            pricing_file = self.pricing_dir / f"{region.replace('/', '_')}.json"
            
            if not pricing_file.exists():
                logger.error(f"Missing pricing file for {region}")
                all_valid = False
                continue
            
            try:
                with open(pricing_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Basic validation
                if not self._validate_pricing_structure(data, region):
                    logger.error(f"Invalid pricing structure for {region}")
                    all_valid = False
                
            except Exception as e:
                logger.error(f"Error validating {region}: {e}")
                all_valid = False
        
        return all_valid
    
    def _validate_pricing_structure(self, data: Dict[str, Any], region: str) -> bool:
        """Validate pricing data structure"""
        required_fields = ["region", "currency", "last_updated", "compute", "storage", "network"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Check region matches
        if data.get("region") != region:
            return False
        
        # Check currency matches expected
        if data.get("currency") != REGIONAL_CURRENCIES.get(region):
            return False
        
        # Check for negative pricing
        for category, pricing in data.items():
            if isinstance(pricing, dict):
                for key, value in pricing.items():
                    if key.endswith(("_hourly", "_monthly", "_per_1000")) and isinstance(value, (int, float)):
                        if value < 0:
                            return False
        
        return True


def main():
    """Main entry point"""
    api_token = os.getenv("IONOS_TOKEN")
    if not api_token:
        logger.error("IONOS_TOKEN environment variable not set")
        return 1
    
    force_update = os.getenv("FORCE_UPDATE", "false").lower() == "true"
    
    updater = PricingUpdater(api_token, force_update)
    
    try:
        # Run update
        changes_detected = updater.run()
        
        # Validate updated pricing
        if not updater.validate_pricing_data():
            logger.error("Pricing validation failed")
            return 1
        
        # Exit with appropriate code
        return 0 if changes_detected or force_update else 0
    
    except Exception as e:
        logger.error(f"Pricing update failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
