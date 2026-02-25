from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosDBaaS(Resource):
    resource_type = "ionos_dbaas"
    
    def calculate_cost(self) -> Dict[str, Any]:
        cores = self.config.get("cores", 1)
        ram = self.config.get("ram", 2)
        storage_size = self.config.get("storage_size", 20)
        storage_type = self.config.get("storage_type", "HDD")
        instances = self.config.get("instances", 1)
        
        db_type = self.config.get("type", "postgres")
        
        vcpu_hourly = cores * self.pricing.get(f"dbaas_{db_type}_vcpu_hourly", 0.015)
        ram_hourly = ram * self.pricing.get(f"dbaas_{db_type}_ram_gb_hourly", 0.008)
        
        storage_key = f"dbaas_{db_type}_storage_{storage_type.lower()}_gb_hourly"
        storage_hourly = storage_size * self.pricing.get(storage_key, 0.00015)
        
        hourly_per_instance = vcpu_hourly + ram_hourly + storage_hourly
        hourly_total = hourly_per_instance * instances
        monthly_total = hourly_total * 730
        
        return {
            "hourly": hourly_total,
            "monthly": monthly_total,
            "breakdown": {
                "vcpu": vcpu_hourly * instances * 730,
                "ram": ram_hourly * instances * 730,
                "storage": storage_hourly * instances * 730
            }
        }


class IonosPostgresCluster(IonosDBaaS):
    resource_type = "ionos_pg_cluster"
    
    def __init__(self, name: str, config: Dict[str, Any], pricing: Dict[str, float], region: str = "de/fra"):
        config["type"] = "postgres"
        super().__init__(name, config, pricing, region)


class IonosMongoCluster(IonosDBaaS):
    resource_type = "ionos_mongo_cluster"
    
    def __init__(self, name: str, config: Dict[str, Any], pricing: Dict[str, float], region: str = "de/fra"):
        config["type"] = "mongo"
        super().__init__(name, config, pricing, region)
