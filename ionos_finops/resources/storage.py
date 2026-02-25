from typing import Any, Dict

from ionos_finops.resources.base import Resource


class IonosVolume(Resource):
    resource_type = "ionos_volume"

    def calculate_cost(self) -> Dict[str, Any]:
        size = self.config.get("size", 0)
        disk_type = self.config.get("type", "HDD")

        storage_key = f"storage_{disk_type.lower()}_gb_hourly"
        storage_hourly = size * self.pricing.get(storage_key, 0.0001)

        monthly_cost = storage_hourly * 730

        return {
            "hourly": storage_hourly,
            "monthly": monthly_cost,
            "breakdown": {f"storage_{disk_type}": monthly_cost},
        }


class IonosS3Bucket(Resource):
    resource_type = "ionos_s3_bucket"

    def calculate_cost(self) -> Dict[str, Any]:
        estimated_size_gb = self.config.get("estimated_size_gb", 0)
        estimated_requests = self.config.get("estimated_requests_monthly", 0)

        storage_monthly = estimated_size_gb * self.pricing.get("s3_storage_gb_monthly", 0.02)

        requests_cost = (estimated_requests / 1000) * self.pricing.get(
            "s3_requests_per_1000", 0.004
        )

        monthly_cost = storage_monthly + requests_cost
        hourly_cost = monthly_cost / 730

        return {
            "hourly": hourly_cost,
            "monthly": monthly_cost,
            "breakdown": {"storage": storage_monthly, "requests": requests_cost},
        }


class IonosBackupUnit(Resource):
    resource_type = "ionos_backup_unit"

    def calculate_cost(self) -> Dict[str, Any]:
        size = self.config.get("size", 0)

        backup_hourly = size * self.pricing.get("backup_gb_hourly", 0.00015)
        monthly_cost = backup_hourly * 730

        return {
            "hourly": backup_hourly,
            "monthly": monthly_cost,
            "breakdown": {"backup_storage": monthly_cost},
        }
