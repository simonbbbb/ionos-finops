from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosUser(Resource):
    resource_type = "ionos_user"
    
    def calculate_cost(self) -> Dict[str, Any]:
        # Users are typically free
        return {
            "hourly": 0.0,
            "monthly": 0.0,
            "breakdown": {}
        }


class IonosGroup(Resource):
    resource_type = "ionos_group"
    
    def calculate_cost(self) -> Dict[str, Any]:
        # Groups are typically free
        return {
            "hourly": 0.0,
            "monthly": 0.0,
            "breakdown": {}
        }


class IonosShare(Resource):
    resource_type = "ionos_share"
    
    def calculate_cost(self) -> Dict[str, Any]:
        # Resource shares are typically free
        return {
            "hourly": 0.0,
            "monthly": 0.0,
            "breakdown": {}
        }


class IonosImage(Resource):
    resource_type = "ionos_image"
    
    def calculate_cost(self) -> Dict[str, Any]:
        # Private images may have storage costs
        size = self.config.get("size", 0)
        
        image_hourly = size * self.pricing.get("image_storage_gb_hourly", 0.00005)
        monthly_cost = image_hourly * 730
        
        return {
            "hourly": image_hourly,
            "monthly": monthly_cost,
            "breakdown": {
                "image_storage": monthly_cost
            }
        }


class IonosContract(Resource):
    resource_type = "ionos_contract"
    
    def calculate_cost(self) -> Dict[str, Any]:
        # Contract metadata, no direct cost
        return {
            "hourly": 0.0,
            "monthly": 0.0,
            "breakdown": {}
        }
