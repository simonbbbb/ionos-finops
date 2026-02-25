from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosLAN(Resource):
    resource_type = "ionos_lan"

    def calculate_cost(self) -> Dict[str, Any]:
        # LANs are typically free within the same datacenter
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}


class IonosNIC(Resource):
    resource_type = "ionos_nic"

    def calculate_cost(self) -> Dict[str, Any]:
        # NICs are typically free
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}


class IonosFirewall(Resource):
    resource_type = "ionos_firewall"

    def calculate_cost(self) -> Dict[str, Any]:
        # Basic firewall rules are typically free
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}


class IonosNATGateway(Resource):
    resource_type = "ionos_natgateway"

    def calculate_cost(self) -> Dict[str, Any]:
        nat_hourly = self.pricing.get("natgateway_hourly", 0.05)
        monthly_cost = nat_hourly * 730

        return {
            "hourly": nat_hourly,
            "monthly": monthly_cost,
            "breakdown": {"nat_gateway": monthly_cost},
        }


class IonosCrossConnect(Resource):
    resource_type = "ionos_crossconnect"

    def calculate_cost(self) -> Dict[str, Any]:
        # Cross connect pricing is typically monthly flat rate
        monthly_cost = self.pricing.get("crossconnect_monthly", 100.0)
        hourly_cost = monthly_cost / 730

        return {
            "hourly": hourly_cost,
            "monthly": monthly_cost,
            "breakdown": {"cross_connect": monthly_cost},
        }
