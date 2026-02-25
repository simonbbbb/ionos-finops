import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ionos_finops.pricing.api import IonosPricingAPI, IonosAPIError

logger = logging.getLogger(__name__)


class PricingData:
    def __init__(self, region: str = "de/fra", custom_pricing: Optional[Dict[str, Any]] = None, 
                 use_api: bool = False, api_token: Optional[str] = None, cache_ttl: int = 24):
        self.region = region
        self.custom_pricing = custom_pricing or {}
        self.use_api = use_api
        self.api_token = api_token
        self.cache_ttl = cache_ttl  # hours
        self.pricing_data = self._load_pricing_data()
        
        if use_api and api_token:
            self._update_from_api_if_needed()
    
    def _load_pricing_data(self) -> Dict[str, Any]:
        pricing_file = self._get_pricing_file_path()
        
        if pricing_file and pricing_file.exists():
            with open(pricing_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = self._get_default_pricing()
        
        if self.custom_pricing:
            data = self._merge_pricing(data, self.custom_pricing)
        
        return data
    
    def _get_pricing_file_path(self) -> Optional[Path]:
        package_dir = Path(__file__).parent.parent
        pricing_dir = package_dir / "pricing_data"
        
        region_file = pricing_dir / f"{self.region.replace('/', '_')}.json"
        if region_file.exists():
            return region_file
        
        default_file = pricing_dir / "default.json"
        if default_file.exists():
            return default_file
        
        return None
    
    def _get_default_pricing(self) -> Dict[str, Any]:
        return {
            "region": self.region,
            "currency": "EUR",
            "last_updated": "2026-02-25",
            "source": "https://www.ionos.com/enterprise-cloud/pricing",
            "compute": {
                "vcpu_hourly": 0.01,
                "ram_gb_hourly": 0.005,
            },
            "storage": {
                "storage_hdd_gb_hourly": 0.00005,
                "storage_ssd_gb_hourly": 0.0001,
                "storage_ssd_premium_gb_hourly": 0.00015,
                "s3_storage_gb_monthly": 0.02,
                "s3_requests_per_1000": 0.004,
                "backup_gb_hourly": 0.00015,
            },
            "network": {
                "loadbalancer_hourly": 0.034,
                "ipv4_hourly": 0.003,
                "bandwidth_gb": 0.0,
            },
            "database": {
                "dbaas_postgres_vcpu_hourly": 0.015,
                "dbaas_postgres_ram_gb_hourly": 0.008,
                "dbaas_postgres_storage_ssd_gb_hourly": 0.00015,
                "dbaas_mongo_vcpu_hourly": 0.015,
                "dbaas_mongo_ram_gb_hourly": 0.008,
                "dbaas_mongo_storage_ssd_gb_hourly": 0.00015,
            },
            "kubernetes": {
                "k8s_control_plane_hourly": 0.0,
                "k8s_node_vcpu_hourly": 0.01,
                "k8s_node_ram_gb_hourly": 0.005,
            }
        }
    
    def _merge_pricing(self, base: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()
        
        for key, value in custom.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_pricing(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _update_from_api_if_needed(self) -> None:
        if not self._should_update_from_cache():
            return
        
        try:
            api = IonosPricingAPI(self.api_token)
            if api.validate_api_token():
                logger.info(f"Updating pricing data from API for {self.region}")
                api_pricing = api.get_all_pricing(self.region)
                
                # Merge with custom pricing
                if self.custom_pricing:
                    api_pricing = self._merge_pricing(api_pricing, self.custom_pricing)
                
                self.pricing_data = api_pricing
                self._save_to_cache()
            else:
                logger.warning("Invalid API token, using cached pricing")
        except IonosAPIError as e:
            logger.error(f"Failed to update pricing from API: {e}")
    
    def _should_update_from_cache(self) -> bool:
        if not self.use_api or not self.api_token:
            return False
        
        last_updated = self.pricing_data.get("last_updated")
        if not last_updated:
            return True
        
        try:
            if isinstance(last_updated, str):
                last_updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            else:
                last_updated_dt = last_updated
            
            update_threshold = datetime.now() - timedelta(hours=self.cache_ttl)
            return last_updated_dt < update_threshold
        except (ValueError, TypeError):
            return True
    
    def _save_to_cache(self) -> None:
        cache_dir = Path.home() / ".ionos-finops" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        cache_file = cache_dir / f"pricing_{self.region.replace('/', '_')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(self.pricing_data, f, indent=2)
    
    def get_pricing(self, resource_type: str) -> Dict[str, float]:
        pricing = {}
        
        for category in self.pricing_data.values():
            if isinstance(category, dict):
                pricing.update(category)
        
        return pricing
    
    def get_category_pricing(self, category: str) -> Dict[str, float]:
        return self.pricing_data.get(category, {})
    
    def update_pricing(self, api_token: str) -> bool:
        """Manually update pricing from API"""
        try:
            api = IonosPricingAPI(api_token)
            api_pricing = api.get_all_pricing(self.region)
            
            if self.custom_pricing:
                api_pricing = self._merge_pricing(api_pricing, self.custom_pricing)
            
            self.pricing_data = api_pricing
            self._save_to_cache()
            return True
        except IonosAPIError:
            return False
