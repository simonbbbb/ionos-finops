from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosServer(Resource):
    resource_type = "ionos_server"

    def calculate_cost(self) -> Dict[str, Any]:
        cores = self.config.get("cores", 0)
        ram = self.config.get("ram", 0)

        volume = self.config.get("volume", {})
        storage_size = volume.get("size", 0) if isinstance(volume, dict) else 0
        storage_type = volume.get("type", "HDD") if isinstance(volume, dict) else "HDD"

        vcpu_hourly = cores * self.pricing.get("vcpu_hourly", 0.01)
        ram_hourly = ram * self.pricing.get("ram_gb_hourly", 0.005)

        storage_key = f"storage_{storage_type.lower()}_gb_hourly"
        storage_hourly = storage_size * self.pricing.get(storage_key, 0.0001)

        hourly_total = vcpu_hourly + ram_hourly + storage_hourly
        monthly_total = hourly_total * 730

        return {
            "hourly": hourly_total,
            "monthly": monthly_total,
            "breakdown": {
                "vcpu": vcpu_hourly * 730,
                "ram": ram_hourly * 730,
                "storage": storage_hourly * 730,
            },
        }


class IonosCube(Resource):
    resource_type = "ionos_cube_server"

    def calculate_cost(self) -> Dict[str, Any]:
        template_id = self.config.get("template_uuid", "")

        cube_templates_raw = self.pricing.get("cube_templates", {})
        cube_templates: Dict[str, Any] = (
            cube_templates_raw if isinstance(cube_templates_raw, dict) else {}
        )
        template_cost = cube_templates.get(template_id, {})
        if not isinstance(template_cost, dict):
            template_cost = {}

        hourly_cost = template_cost.get("hourly", 0.0)
        monthly_cost = hourly_cost * 730

        return {
            "hourly": hourly_cost,
            "monthly": monthly_cost,
            "breakdown": {"cube_instance": monthly_cost},
        }


class IonosVCPU(Resource):
    resource_type = "ionos_vcpu_server"

    def calculate_cost(self) -> Dict[str, Any]:
        cores = self.config.get("cores", 0)
        ram = self.config.get("ram", 0)

        vcpu_hourly = cores * self.pricing.get("vcpu_hourly", 0.01)
        ram_hourly = ram * self.pricing.get("ram_gb_hourly", 0.005)

        hourly_total = vcpu_hourly + ram_hourly
        monthly_total = hourly_total * 730

        return {
            "hourly": hourly_total,
            "monthly": monthly_total,
            "breakdown": {"vcpu": vcpu_hourly * 730, "ram": ram_hourly * 730},
        }
