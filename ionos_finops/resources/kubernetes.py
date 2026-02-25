from typing import Any, Dict

from ionos_finops.resources.base import Resource


class IonosK8SCluster(Resource):
    resource_type = "ionos_k8s_cluster"

    def calculate_cost(self) -> Dict[str, Any]:
        # Control plane is typically free for managed K8s
        control_plane_hourly = self.pricing.get("k8s_control_plane_hourly", 0.0)
        monthly_control_plane = control_plane_hourly * 730

        return {
            "hourly": control_plane_hourly,
            "monthly": monthly_control_plane,
            "breakdown": {"control_plane": monthly_control_plane},
        }


class IonosK8SNodePool(Resource):
    resource_type = "ionos_k8s_node_pool"

    def calculate_cost(self) -> Dict[str, Any]:
        node_count = self.config.get("node_count", 1)
        cores = self.config.get("cores", 2)
        ram = self.config.get("ram", 4)
        storage_size = self.config.get("storage_size", 50)
        storage_type = self.config.get("storage_type", "SSD")

        vcpu_hourly = cores * self.pricing.get("k8s_node_vcpu_hourly", 0.01)
        ram_hourly = ram * self.pricing.get("k8s_node_ram_gb_hourly", 0.005)

        storage_key = f"k8s_node_storage_{storage_type.lower()}_gb_hourly"
        storage_hourly = storage_size * self.pricing.get(storage_key, 0.0001)

        hourly_per_node = vcpu_hourly + ram_hourly + storage_hourly
        hourly_total = hourly_per_node * node_count
        monthly_total = hourly_total * 730

        return {
            "hourly": hourly_total,
            "monthly": monthly_total,
            "breakdown": {
                "vcpu": vcpu_hourly * node_count * 730,
                "ram": ram_hourly * node_count * 730,
                "storage": storage_hourly * node_count * 730,
            },
        }
