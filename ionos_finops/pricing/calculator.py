from typing import Dict, List, Any, Optional
from ionos_finops.parser.terraform import TerraformParser
from ionos_finops.pricing.data import PricingData
from ionos_finops.resources import RESOURCE_REGISTRY


class CostCalculator:
    def __init__(
        self,
        region: str = "de/fra",
        custom_pricing: Optional[Dict[str, Any]] = None,
        use_api: bool = False,
        api_token: Optional[str] = None,
        cache_ttl: int = 24
    ):
        self.region = region
        self.pricing_data = PricingData(
            region=region, 
            custom_pricing=custom_pricing,
            use_api=use_api,
            api_token=api_token,
            cache_ttl=cache_ttl
        )
        self.resources: List[Any] = []
    
    def load_from_terraform(self, path: str) -> None:
        parser = TerraformParser(path)
        tf_resources = parser.parse()
        
        for tf_resource in tf_resources:
            resource_type = tf_resource["type"]
            resource_name = tf_resource["name"]
            resource_config = tf_resource["config"]
            
            if resource_type in RESOURCE_REGISTRY:
                resource_class = RESOURCE_REGISTRY[resource_type]
                pricing = self.pricing_data.get_pricing(resource_type)
                
                resource_instance = resource_class(
                    name=resource_name,
                    config=resource_config,
                    pricing=pricing,
                    region=self.region
                )
                self.resources.append(resource_instance)
    
    def calculate_total_cost(self) -> Dict[str, float]:
        total_hourly = 0.0
        total_monthly = 0.0
        total_yearly = 0.0
        
        for resource in self.resources:
            total_hourly += resource.get_hourly_cost()
            total_monthly += resource.get_monthly_cost()
            total_yearly += resource.get_yearly_cost()
        
        return {
            "hourly": total_hourly,
            "monthly": total_monthly,
            "yearly": total_yearly
        }
    
    def get_cost_by_resource_type(self) -> Dict[str, Dict[str, float]]:
        costs_by_type: Dict[str, Dict[str, float]] = {}
        
        for resource in self.resources:
            resource_type = resource.resource_type
            
            if resource_type not in costs_by_type:
                costs_by_type[resource_type] = {
                    "hourly": 0.0,
                    "monthly": 0.0,
                    "yearly": 0.0,
                    "count": 0
                }
            
            costs_by_type[resource_type]["hourly"] += resource.get_hourly_cost()
            costs_by_type[resource_type]["monthly"] += resource.get_monthly_cost()
            costs_by_type[resource_type]["yearly"] += resource.get_yearly_cost()
            costs_by_type[resource_type]["count"] += 1
        
        return costs_by_type
    
    def get_detailed_breakdown(self) -> List[Dict[str, Any]]:
        breakdown = []
        
        for resource in self.resources:
            breakdown.append(resource.to_dict())
        
        return breakdown
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "region": self.region,
            "total_resources": len(self.resources),
            "total_cost": self.calculate_total_cost(),
            "cost_by_type": self.get_cost_by_resource_type(),
            "resources": self.get_detailed_breakdown()
        }
