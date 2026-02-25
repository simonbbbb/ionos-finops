from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Resource(ABC):
    resource_type: str = ""
    
    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        pricing: Dict[str, float],
        region: str = "de/fra"
    ):
        self.name = name
        self.config = config
        self.pricing = pricing
        self.region = region
    
    @abstractmethod
    def calculate_cost(self) -> Dict[str, Any]:
        pass
    
    def get_hourly_cost(self) -> float:
        cost = self.calculate_cost()
        return cost.get("hourly", 0.0)
    
    def get_monthly_cost(self) -> float:
        cost = self.calculate_cost()
        return cost.get("monthly", 0.0)
    
    def get_yearly_cost(self) -> float:
        return self.get_monthly_cost() * 12
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        cost = self.calculate_cost()
        return cost.get("breakdown", {})
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.resource_type,
            "region": self.region,
            "config": self.config,
            "costs": {
                "hourly": self.get_hourly_cost(),
                "monthly": self.get_monthly_cost(),
                "yearly": self.get_yearly_cost(),
                "breakdown": self.get_cost_breakdown()
            }
        }
