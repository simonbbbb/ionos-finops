from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosLoadBalancer(Resource):
    resource_type = "ionos_loadbalancer"

    def calculate_cost(self) -> Dict[str, Any]:
        lb_hourly = self.pricing.get("loadbalancer_hourly", 0.034)
        monthly_cost = lb_hourly * 730

        return {
            "hourly": lb_hourly,
            "monthly": monthly_cost,
            "breakdown": {"loadbalancer": monthly_cost},
        }


class IonosIPBlock(Resource):
    resource_type = "ionos_ipblock"

    def calculate_cost(self) -> Dict[str, Any]:
        size = self.config.get("size", 1)

        ip_hourly = size * self.pricing.get("ipv4_hourly", 0.003)
        monthly_cost = ip_hourly * 730

        return {
            "hourly": ip_hourly,
            "monthly": monthly_cost,
            "breakdown": {"ipv4_addresses": monthly_cost},
        }


class IonosNIC(Resource):
    resource_type = "ionos_nic"

    def calculate_cost(self) -> Dict[str, Any]:
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}


class IonosFirewall(Resource):
    resource_type = "ionos_firewall"

    def calculate_cost(self) -> Dict[str, Any]:
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}
