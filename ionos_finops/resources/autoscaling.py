from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosAutoscalingGroup(Resource):
    resource_type = "ionos_autoscaling_group"
    
    def calculate_cost(self) -> Dict[str, Any]:
        min_instances = self.config.get("min_instances", 1)
        max_instances = self.config.get("max_instances", 3)
        desired_instances = self.config.get("desired_instances", 2)
        
        # Calculate cost based on desired instances (not max)
        cores = self.config.get("cores", 2)
        ram = self.config.get("ram", 4)
        storage_size = self.config.get("storage_size", 50)
        storage_type = self.config.get("storage_type", "SSD")
        
        vcpu_hourly = cores * self.pricing.get("vcpu_hourly", 0.01)
        ram_hourly = ram * self.pricing.get("ram_gb_hourly", 0.005)
        
        storage_key = f"storage_{storage_type.lower()}_gb_hourly"
        storage_hourly = storage_size * self.pricing.get(storage_key, 0.0001)
        
        hourly_per_instance = vcpu_hourly + ram_hourly + storage_hourly
        hourly_total = hourly_per_instance * desired_instances
        monthly_total = hourly_total * 730
        
        # Autoscaling service fee (if any)
        autoscaling_fee = self.pricing.get("autoscaling_monthly_fee", 0.0)
        monthly_total += autoscaling_fee
        
        return {
            "hourly": hourly_total,
            "monthly": monthly_total,
            "breakdown": {
                "vcpu": vcpu_hourly * desired_instances * 730,
                "ram": ram_hourly * desired_instances * 730,
                "storage": storage_hourly * desired_instances * 730,
                "autoscaling_fee": autoscaling_fee
            }
        }


class IonosScalingPolicy(Resource):
    resource_type = "ionos_scaling_policy"
    
    def calculate_cost(self) -> Dict[str, Any]:
        # Scaling policies are typically free
        return {
            "hourly": 0.0,
            "monthly": 0.0,
            "breakdown": {}
        }
