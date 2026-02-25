from typing import Dict, Any
from ionos_finops.resources.base import Resource


class IonosS3Bucket(Resource):
    resource_type = "ionos_s3_bucket"

    def calculate_cost(self) -> Dict[str, Any]:
        estimated_size_gb = self.config.get("estimated_size_gb", 0)
        estimated_requests_monthly = self.config.get("estimated_requests_monthly", 0)

        storage_monthly = estimated_size_gb * self.pricing.get("s3_storage_gb_monthly", 0.02)

        requests_cost = (estimated_requests_monthly / 1000) * self.pricing.get(
            "s3_requests_per_1000", 0.004
        )

        monthly_cost = storage_monthly + requests_cost
        hourly_cost = monthly_cost / 730

        return {
            "hourly": hourly_cost,
            "monthly": monthly_cost,
            "breakdown": {"storage": storage_monthly, "requests": requests_cost},
        }


class IonosS3Key(Resource):
    resource_type = "ionos_s3_key"

    def calculate_cost(self) -> Dict[str, Any]:
        # S3 keys are typically free
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}


class IonosS3BucketPolicy(Resource):
    resource_type = "ionos_s3_bucket_policy"

    def calculate_cost(self) -> Dict[str, Any]:
        # Bucket policies are typically free
        return {"hourly": 0.0, "monthly": 0.0, "breakdown": {}}
