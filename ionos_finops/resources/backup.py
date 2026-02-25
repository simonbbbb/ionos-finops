from typing import Any, Dict

from ionos_finops.resources.base import Resource


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


class IonosBackupPlan(Resource):
    resource_type = "ionos_backup_plan"

    def calculate_cost(self) -> Dict[str, Any]:
        # Backup plans may have a base cost plus per-GB cost
        base_monthly = self.pricing.get("backup_plan_base_monthly", 5.0)

        # Some plans charge based on backup frequency or retention
        schedule_type = self.config.get("schedule_type", "daily")
        retention_days = self.config.get("retention_days", 7)

        # Additional cost for longer retention
        retention_multiplier = 1.0
        if retention_days > 30:
            retention_multiplier = 1.5
        elif retention_days > 90:
            retention_multiplier = 2.0

        monthly_cost = base_monthly * retention_multiplier
        hourly_cost = monthly_cost / 730

        return {
            "hourly": hourly_cost,
            "monthly": monthly_cost,
            "breakdown": {"backup_plan": monthly_cost},
        }


class IonosSnapshot(Resource):
    resource_type = "ionos_snapshot"

    def calculate_cost(self) -> Dict[str, Any]:
        size = self.config.get("size", 0)

        # Snapshots are typically cheaper than active storage
        snapshot_hourly = size * self.pricing.get("snapshot_gb_hourly", 0.00008)
        monthly_cost = snapshot_hourly * 730

        return {
            "hourly": snapshot_hourly,
            "monthly": monthly_cost,
            "breakdown": {"snapshot_storage": monthly_cost},
        }
