import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)


class IonosBillingAPIError(Exception):
    pass


class IonosBillingAPI:
    """
    IONOS Billing API client for fetching real pricing data.

    This uses the official IONOS Billing API to get actual pricing
    from your contract, providing the most accurate cost calculations.
    """

    def __init__(self, username: str, password: str, contract_id: str):
        self.username = username
        self.password = password
        self.contract_id = contract_id
        self.base_url = "https://api.ionos.com/billing/v3"
        self.session = requests.Session()

        # Set up authentication - try Basic Auth first
        self.session.auth = (username, password)
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        # Try to get a token for Bearer Auth
        self.token = None
        self._setup_bearer_auth()

    def _setup_bearer_auth(self):
        """Try to get Bearer token from IONOS Cloud API"""
        try:
            # Try to get token from IONOS Cloud API
            cloud_api_url = "https://api.ionos.com/cloudapi/v6"
            token_response = self.session.post(f"{cloud_api_url}/tokens", json={})
            if token_response.status_code == 202:
                token_data = token_response.json()
                self.token = token_data.get("token")
                if self.token:
                    # Switch to Bearer Auth
                    self.session.auth = None
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    logger.info("Successfully switched to Bearer authentication")
        except Exception as e:
            logger.debug(f"Bearer auth setup failed, using Basic Auth: {e}")
            pass

    def test_connection(self) -> bool:
        """Test API connection and authentication"""
        try:
            # Try internal ping first
            response = self.session.get(f"{self.base_url}/internal/ping")
            if response.status_code == 200:
                return True

            # If that fails, try profile endpoint
            response = self.session.get(f"{self.base_url}/profile")
            if response.status_code == 200:
                return True

            # If that fails, try products endpoint
            response = self.session.get(f"{self.base_url}/{self.contract_id}/products")
            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            logger.error(f"API connection test failed: {e}")
            return False

    def get_products(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get products and pricing for the contract.

        Args:
            date: Optional date in YYYY-MM-DD format for specific pricing

        Returns:
            Dictionary with product pricing information
        """
        try:
            url = f"{self.base_url}/{self.contract_id}/products"
            params = {}
            if date:
                params["date"] = date

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data: Dict[str, Any] = response.json()
            logger.info(f"Successfully fetched {len(data.get('products', []))} products")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch products: {e}")
            raise IonosBillingAPIError(f"Failed to fetch products: {e}")

    def get_profile(self) -> Dict[str, Any]:
        """Get billing profile information"""
        try:
            response = self.session.get(f"{self.base_url}/profile")
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch profile: {e}")
            raise IonosBillingAPIError(f"Failed to fetch profile: {e}")

    def parse_pricing_from_products(self, products_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse pricing data from the products API response.

        Returns structured pricing data compatible with the tool.
        """
        products = products_data.get("products", [])

        # Initialize pricing structure
        pricing: Dict[str, Dict[str, float]] = {
            "compute": {},
            "storage": {},
            "network": {},
            "database": {},
            "kubernetes": {},
            "backup": {},
            "autoscaling": {},
            "management": {},
        }

        # Product code mappings
        product_mappings = {
            # Compute
            "C01000": ("compute", "vcpu_hourly"),
            "C010US": ("compute", "vcpu_hourly_us"),
            "C02000": ("compute", "ram_gb_hourly"),
            "C03000": ("compute", "ram_gb_hourly_high"),
            "C04000": ("compute", "ram_gb_hourly_ultra"),
            "C05000": ("compute", "dedicated_core_hourly"),
            "C06000": ("compute", "dedicated_core_high_hourly"),
            # Storage
            "S01000": ("storage", "storage_hdd_gb_hourly"),
            "S02000": ("storage", "storage_ssd_gb_hourly"),
            "S03000": ("storage", "storage_ssd_premium_gb_hourly"),
            "S05000": ("storage", "snapshot_gb_hourly"),
            # S3 Object Storage
            "S3SU1000": ("storage", "s3_storage_gb_monthly"),
            "S3SU1100": ("storage", "s3_storage_gb_monthly_standard"),
            "S3SU1200": ("storage", "s3_storage_gb_monthly_premium"),
            "S3SU1300": ("storage", "s3_storage_gb_monthly_archive"),
            "S3SU2000": ("storage", "s3_requests_per_1000"),
            "S3TI1000": ("storage", "s3_tiered_requests_per_1000"),
            "S3TO1000": ("storage", "s3_transfer_out_gb"),
            # Network
            "NLB1000": ("network", "loadbalancer_hourly"),
            "NLB1100": ("network", "loadbalancer_hourly_plus"),
            "NAT1000": ("network", "natgateway_hourly"),
            "VPNG1000": ("network", "vpn_gateway_hourly"),
            "VPNG1100": ("network", "vpn_gateway_hourly_ha"),
            "ALB1000": ("network", "app_loadbalancer_hourly"),
            # Database
            "DBPGB1000": ("database", "dbaas_postgres_vcpu_hourly"),
            "DBPGB1100": ("database", "dbaas_postgres_ram_gb_hourly"),
            "DBPGB1200": ("database", "dbaas_postgres_storage_ssd_gb_hourly"),
            "DBPGB1300": ("database", "dbaas_postgres_storage_hdd_gb_hourly"),
            "DBMB1000": ("database", "dbaas_mongo_vcpu_hourly"),
            "DBMB1100": ("database", "dbaas_mongo_ram_gb_hourly"),
            "DBMB1200": ("database", "dbaas_mongo_storage_ssd_gb_hourly"),
            "DBMAB1000": ("database", "dbaas_mariadb_vcpu_hourly"),
            "DBMAB1100": ("database", "dbaas_mariadb_ram_gb_hourly"),
            "DBMAB1200": ("database", "dbaas_mariadb_storage_ssd_gb_hourly"),
            "DBMIM1000": ("database", "dbaas_mysql_vcpu_hourly"),
            "DBMIM1100": ("database", "dbaas_mysql_ram_gb_hourly"),
            "DBMIM1200": ("database", "dbaas_mysql_storage_ssd_gb_hourly"),
            # Backup
            "BA1100": ("backup", "backup_plan_base_monthly"),
            "BA1200": ("backup", "backup_gb_hourly"),
            "BA1300": ("backup", "backup_gb_hourly_premium"),
            # Kubernetes (if available)
            "K8S1000": ("kubernetes", "k8s_control_plane_hourly"),
            "K8S1100": ("kubernetes", "k8s_node_vcpu_hourly"),
            "K8S1200": ("kubernetes", "k8s_node_ram_gb_hourly"),
            # Management
            "WL1000": ("management", "image_storage_gb_hourly"),
            "WL2000": ("management", "image_storage_gb_hourly_premium"),
        }

        # Parse products
        for product in products:
            meter_id = product.get("meterId", "")
            unit_cost = product.get("unitCost", {})

            if meter_id in product_mappings:
                category, key = product_mappings[meter_id]

                # Extract pricing from unitCost
                if unit_cost and isinstance(unit_cost, dict):
                    # Look for common pricing fields
                    price_value = None
                    for field in ["value", "amount", "price", "cost"]:
                        if field in unit_cost:
                            price_value = unit_cost[field]
                            break

                    if price_value is not None:
                        # Convert to hourly if needed
                        if product.get("unit") == "GB" and "monthly" in meter_id.lower():
                            # Convert monthly to hourly
                            price_value = price_value / 730  # Average hours per month
                        elif product.get("unit") == "GB" and "per_1000" in key:
                            # Already per 1000
                            pass
                        elif product.get("unit") in ["GB", "vCPU", "Core"]:
                            # Per unit pricing
                            pass

                        pricing[category][key] = float(price_value)

        return pricing

    def get_current_pricing(self) -> Dict[str, Any]:
        """
        Get current pricing data from your IONOS contract.

        Returns:
            Complete pricing data structure
        """
        try:
            # Get products data
            products_data = self.get_products()

            # Parse pricing
            pricing = self.parse_pricing_from_products(products_data)

            # Add metadata
            metadata = {
                "region": "de/fra",  # Default, can be updated based on contract
                "currency": "EUR",  # Default, can be updated based on contract
                "last_updated": datetime.now().isoformat(),
                "source": f"{self.base_url}/{self.contract_id}/products",
                "contract_id": self.contract_id,
                "customer_id": products_data.get("metadata", {}).get("customerId"),
                "liability": products_data.get(
                    "liability", "Please check your contract for prices."
                ),
            }

            # Merge metadata with pricing
            result = {**metadata, **pricing}

            logger.info(f"Successfully parsed pricing for {len(pricing)} categories")
            return result

        except Exception as e:
            logger.error(f"Failed to get current pricing: {e}")
            raise IonosBillingAPIError(f"Failed to get current pricing: {e}")

    def get_contract_info(self) -> Dict[str, Any]:
        """Get contract and profile information"""
        try:
            profile = self.get_profile()
            products = self.get_products()

            return {
                "contract_id": self.contract_id,
                "customer_id": products.get("metadata", {}).get("customerId"),
                "companies": profile.get("companies", []),
                "liability": products.get("liability"),
                "total_products": len(products.get("products", [])),
                "last_updated": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get contract info: {e}")
            raise IonosBillingAPIError(f"Failed to get contract info: {e}")
