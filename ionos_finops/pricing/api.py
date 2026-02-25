import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IonosAPIError(Exception):
    pass


class IonosPricingAPI:
    """
    IONOS API client with realistic limitations.

    IMPORTANT: IONOS does not provide a public pricing API.
    This class provides fallback functionality and documentation
    of the actual API limitations.
    """

    def __init__(
        self, api_token: Optional[str] = None, api_url: str = "https://api.ionos.com/cloudapi/v6"
    ):
        self.api_url = api_url
        self.api_token = api_token or os.getenv("IONOS_TOKEN")
        self.session = requests.Session()

        if self.api_token:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
            )

    def _make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request with proper error handling"""
        url = f"{self.api_url}/{endpoint}"

        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise IonosAPIError(f"Failed to fetch data from IONOS API: {e}")

    def get_locations(self) -> List[Dict[str, Any]]:
        """
        Get available IONOS data center locations.

        Note: This endpoint requires authentication and returns
        account-specific information, not a public catalog.
        """
        try:
            return self._make_request("locations")
        except IonosAPIError:
            # Fallback to known locations
            fallback: List[Dict[str, Any]] = [
                {"id": "de/fra", "name": "Frankfurt", "country": "Germany"},
                {"id": "de/ber", "name": "Berlin", "country": "Germany"},
                {"id": "de/fra2", "name": "Frankfurt 2", "country": "Germany"},
                {"id": "gb/lhr", "name": "London", "country": "United Kingdom"},
                {"id": "gb/wor", "name": "Worchester", "country": "United Kingdom"},
                {"id": "fr/par", "name": "Paris", "country": "France"},
                {"id": "es/log", "name": "Logroño", "country": "Spain"},
                {"id": "us/las", "name": "Las Vegas", "country": "United States"},
                {"id": "us/ewr", "name": "Newark", "country": "United States"},
                {"id": "us/kc", "name": "Lenexa", "country": "United States"},
            ]
            return fallback

    def get_server_pricing(self, location: str) -> Dict[str, Any]:
        """
        Get server pricing for a specific location.

        NOTE: IONOS does not provide a public pricing API.
        This method always returns fallback pricing.
        """
        logger.warning(f"IONOS pricing API not available. Using fallback pricing for {location}")
        return self._get_fallback_pricing()

    def get_storage_pricing(self, location: str) -> Dict[str, Any]:
        """
        Get storage pricing for a specific location.

        NOTE: IONOS does not provide a public pricing API.
        This method always returns fallback pricing.
        """
        logger.warning(f"IONOS pricing API not available. Using fallback pricing for {location}")
        return self._get_fallback_pricing()

    def get_network_pricing(self, location: str) -> Dict[str, Any]:
        """
        Get network pricing for a specific location.

        NOTE: IONOS does not provide a public pricing API.
        This method always returns fallback pricing.
        """
        logger.warning(f"IONOS pricing API not available. Using fallback pricing for {location}")
        return self._get_fallback_pricing()

    def get_database_pricing(self, location: str) -> Dict[str, Any]:
        """
        Get database pricing for a specific location.

        NOTE: IONOS does not provide a public pricing API.
        This method always returns fallback pricing.
        """
        logger.warning(f"IONOS pricing API not available. Using fallback pricing for {location}")
        return self._get_fallback_pricing()

    def get_kubernetes_pricing(self, location: str) -> Dict[str, Any]:
        """
        Get Kubernetes pricing for a specific location.

        NOTE: IONOS does not provide a public pricing API.
        This method always returns fallback pricing.
        """
        logger.warning(f"IONOS pricing API not available. Using fallback pricing for {location}")
        return self._get_fallback_pricing()

    def get_all_pricing(self, location: str) -> Dict[str, Any]:
        """
        Get all pricing data for a specific location.

        NOTE: IONOS does not provide a public pricing API.
        This method returns structured fallback pricing.
        """
        logger.info(f"Using fallback pricing data for {location}")

        pricing_data = {
            "region": location,
            "currency": self._get_currency_for_region(location),
            "last_updated": datetime.now().isoformat(),
            "source": "fallback_data",
            "compute": self._get_fallback_pricing(),
            "storage": self._get_fallback_pricing(),
            "network": self._get_fallback_pricing(),
            "database": self._get_fallback_pricing(),
            "kubernetes": self._get_fallback_pricing(),
            "backup": {"backup_plan_base_monthly": 5.0, "backup_gb_hourly": 0.00015},
            "autoscaling": {"autoscaling_monthly_fee": 0.0},
            "management": {"image_storage_gb_hourly": 0.00005},
        }

        return pricing_data

    def _get_fallback_pricing(self) -> Dict[str, Any]:
        """Get fallback pricing data based on typical IONOS pricing"""
        return {
            "vcpu_hourly": 0.01,
            "ram_gb_hourly": 0.005,
            "storage_hdd_gb_hourly": 0.00005,
            "storage_ssd_gb_hourly": 0.0001,
            "storage_ssd_premium_gb_hourly": 0.00015,
            "s3_storage_gb_monthly": 0.02,
            "s3_requests_per_1000": 0.004,
            "backup_gb_hourly": 0.00015,
            "snapshot_gb_hourly": 0.00008,
            "loadbalancer_hourly": 0.034,
            "ipv4_hourly": 0.003,
            "natgateway_hourly": 0.05,
            "bandwidth_gb": 0.0,
            "crossconnect_monthly": 100.0,
            "dbaas_postgres_vcpu_hourly": 0.015,
            "dbaas_postgres_ram_gb_hourly": 0.008,
            "dbaas_postgres_storage_ssd_gb_hourly": 0.00015,
            "dbaas_postgres_storage_hdd_gb_hourly": 0.00008,
            "dbaas_mongo_vcpu_hourly": 0.015,
            "dbaas_mongo_ram_gb_hourly": 0.008,
            "dbaas_mongo_storage_ssd_gb_hourly": 0.00015,
            "dbaas_mysql_vcpu_hourly": 0.015,
            "dbaas_mysql_ram_gb_hourly": 0.008,
            "dbaas_mysql_storage_ssd_gb_hourly": 0.00015,
            "dbaas_mariadb_vcpu_hourly": 0.015,
            "dbaas_mariadb_ram_gb_hourly": 0.008,
            "dbaas_mariadb_storage_ssd_gb_hourly": 0.00015,
            "k8s_control_plane_hourly": 0.0,
            "k8s_node_vcpu_hourly": 0.01,
            "k8s_node_ram_gb_hourly": 0.005,
            "k8s_node_storage_ssd_gb_hourly": 0.0001,
            "k8s_node_storage_hdd_gb_hourly": 0.00005,
        }

    def _get_currency_for_region(self, region: str) -> str:
        """Get currency code for a specific region"""
        currencies = {
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
        return currencies.get(region, "EUR")

    def validate_api_token(self) -> bool:
        """
        Validate API token by making a test request.

        Note: This will only work with valid IONOS credentials
        for account-specific APIs, not pricing APIs.
        """
        try:
            self._make_request("locations")
            return True
        except IonosAPIError:
            return False

    def get_pricing_api_status(self) -> Dict[str, Any]:
        """
        Get the status of IONOS pricing API availability.

        Returns information about API limitations and alternatives.
        """
        return {
            "public_pricing_api": False,
            "account_billing_api": True,
            "limitations": [
                "IONOS does not provide a public pricing API",
                "Pricing only available via website calculator (requires login)",
                "Account-specific billing data available with authentication",
                "No programmatic access to standard pricing catalog",
            ],
            "alternatives": [
                "Manual pricing updates from website",
                "Community-driven pricing contributions",
                "Web scraping (may violate terms of service)",
                "Partnership with IONOS for API access",
            ],
            "current_implementation": "fallback_pricing_data",
            "recommendation": "Manual pricing updates with community validation",
        }
