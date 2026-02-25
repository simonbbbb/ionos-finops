from ionos_finops.resources.base import Resource
from ionos_finops.resources.compute import IonosServer, IonosCube, IonosVCPU
from ionos_finops.resources.storage import IonosVolume, IonosS3Bucket, IonosBackupUnit
from ionos_finops.resources.network import IonosLoadBalancer, IonosIPBlock, IonosNIC, IonosFirewall
from ionos_finops.resources.database import IonosDBaaS
from ionos_finops.resources.kubernetes import IonosK8SCluster, IonosK8SNodePool
from ionos_finops.resources.networking import IonosLAN, IonosNATGateway, IonosCrossConnect
from ionos_finops.resources.backup import IonosBackupPlan, IonosSnapshot
from ionos_finops.resources.autoscaling import IonosAutoscalingGroup, IonosScalingPolicy
from ionos_finops.resources.management import (
    IonosUser,
    IonosGroup,
    IonosShare,
    IonosImage,
    IonosContract,
)
from ionos_finops.resources.s3 import IonosS3Key, IonosS3BucketPolicy

from typing import Dict, Type

RESOURCE_REGISTRY: Dict[str, Type[Resource]] = {
    # Compute
    "ionos_server": IonosServer,
    "ionos_cube_server": IonosCube,
    "ionos_vcpu_server": IonosVCPU,
    # Storage
    "ionos_volume": IonosVolume,
    "ionos_s3_bucket": IonosS3Bucket,
    "ionos_backup_unit": IonosBackupUnit,
    "ionos_snapshot": IonosSnapshot,
    # Network
    "ionos_loadbalancer": IonosLoadBalancer,
    "ionos_ipblock": IonosIPBlock,
    "ionos_nic": IonosNIC,
    "ionos_firewall": IonosFirewall,
    "ionos_lan": IonosLAN,
    "ionos_natgateway": IonosNATGateway,
    "ionos_crossconnect": IonosCrossConnect,
    # Database
    "ionos_pg_cluster": IonosDBaaS,
    "ionos_mongo_cluster": IonosDBaaS,
    "ionos_mysql_cluster": IonosDBaaS,
    "ionos_mariadb_cluster": IonosDBaaS,
    # Kubernetes
    "ionos_k8s_cluster": IonosK8SCluster,
    "ionos_k8s_node_pool": IonosK8SNodePool,
    # Backup
    "ionos_backup_plan": IonosBackupPlan,
    # Autoscaling
    "ionos_autoscaling_group": IonosAutoscalingGroup,
    "ionos_scaling_policy": IonosScalingPolicy,
    # Management
    "ionos_user": IonosUser,
    "ionos_group": IonosGroup,
    "ionos_share": IonosShare,
    "ionos_image": IonosImage,
    "ionos_contract": IonosContract,
    # S3
    "ionos_s3_key": IonosS3Key,
    "ionos_s3_bucket_policy": IonosS3BucketPolicy,
}

__all__ = [
    "Resource",
    # Compute
    "IonosServer",
    "IonosCube",
    "IonosVCPU",
    # Storage
    "IonosVolume",
    "IonosS3Bucket",
    "IonosBackupUnit",
    "IonosSnapshot",
    # Network
    "IonosLoadBalancer",
    "IonosIPBlock",
    "IonosNIC",
    "IonosFirewall",
    "IonosLAN",
    "IonosNATGateway",
    "IonosCrossConnect",
    # Database
    "IonosDBaaS",
    # Kubernetes
    "IonosK8SCluster",
    "IonosK8SNodePool",
    # Backup
    "IonosBackupPlan",
    # Autoscaling
    "IonosAutoscalingGroup",
    "IonosScalingPolicy",
    # Management
    "IonosUser",
    "IonosGroup",
    "IonosShare",
    "IonosImage",
    "IonosContract",
    # S3
    "IonosS3Key",
    "IonosS3BucketPolicy",
    "RESOURCE_REGISTRY",
]
