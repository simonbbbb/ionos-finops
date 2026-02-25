import pytest

from ionos_finops.resources.compute import IonosCube, IonosServer
from ionos_finops.resources.database import IonosDBaaS
from ionos_finops.resources.network import IonosIPBlock, IonosLoadBalancer
from ionos_finops.resources.storage import IonosS3Bucket, IonosVolume


class TestIonosServer:
    def test_server_cost_calculation(self):
        config = {"cores": 2, "ram": 4, "volume": {"size": 50, "type": "SSD"}}
        pricing = {"vcpu_hourly": 0.01, "ram_gb_hourly": 0.005, "storage_ssd_gb_hourly": 0.0001}

        server = IonosServer("test-server", config, pricing)
        cost = server.calculate_cost()

        expected_hourly = (2 * 0.01) + (4 * 0.005) + (50 * 0.0001)
        assert cost["hourly"] == pytest.approx(expected_hourly)
        assert cost["monthly"] == pytest.approx(expected_hourly * 730)

    def test_server_with_hdd_storage(self):
        config = {"cores": 1, "ram": 2, "volume": {"size": 100, "type": "HDD"}}
        pricing = {"vcpu_hourly": 0.01, "ram_gb_hourly": 0.005, "storage_hdd_gb_hourly": 0.00005}

        server = IonosServer("test-server", config, pricing)
        cost = server.calculate_cost()

        assert cost["hourly"] > 0
        assert "vcpu" in cost["breakdown"]
        assert "ram" in cost["breakdown"]
        assert "storage" in cost["breakdown"]


class TestIonosVolume:
    def test_volume_cost_calculation(self):
        config = {"size": 200, "type": "SSD"}
        pricing = {"storage_ssd_gb_hourly": 0.0001}

        volume = IonosVolume("test-volume", config, pricing)
        cost = volume.calculate_cost()

        expected_hourly = 200 * 0.0001
        assert cost["hourly"] == pytest.approx(expected_hourly)
        assert cost["monthly"] == pytest.approx(expected_hourly * 730)


class TestIonosLoadBalancer:
    def test_loadbalancer_cost(self):
        config = {}
        pricing = {"loadbalancer_hourly": 0.034}

        lb = IonosLoadBalancer("test-lb", config, pricing)
        cost = lb.calculate_cost()

        assert cost["hourly"] == 0.034
        assert cost["monthly"] == pytest.approx(0.034 * 730)


class TestIonosIPBlock:
    def test_ipblock_cost(self):
        config = {"size": 2}
        pricing = {"ipv4_hourly": 0.003}

        ipblock = IonosIPBlock("test-ips", config, pricing)
        cost = ipblock.calculate_cost()

        assert cost["hourly"] == pytest.approx(2 * 0.003)
        assert cost["monthly"] == pytest.approx(2 * 0.003 * 730)


class TestIonosDBaaS:
    def test_dbaas_cost_calculation(self):
        config = {
            "type": "postgres",
            "cores": 2,
            "ram": 4,
            "storage_size": 50,
            "storage_type": "SSD",
            "instances": 1,
        }
        pricing = {
            "dbaas_postgres_vcpu_hourly": 0.015,
            "dbaas_postgres_ram_gb_hourly": 0.008,
            "dbaas_postgres_storage_ssd_gb_hourly": 0.00015,
        }

        db = IonosDBaaS("test-db", config, pricing)
        cost = db.calculate_cost()

        expected_hourly = (2 * 0.015) + (4 * 0.008) + (50 * 0.00015)
        assert cost["hourly"] == pytest.approx(expected_hourly)

    def test_dbaas_multiple_instances(self):
        config = {
            "type": "postgres",
            "cores": 2,
            "ram": 4,
            "storage_size": 50,
            "storage_type": "SSD",
            "instances": 3,
        }
        pricing = {
            "dbaas_postgres_vcpu_hourly": 0.015,
            "dbaas_postgres_ram_gb_hourly": 0.008,
            "dbaas_postgres_storage_ssd_gb_hourly": 0.00015,
        }

        db = IonosDBaaS("test-db", config, pricing)
        cost = db.calculate_cost()

        expected_per_instance = (2 * 0.015) + (4 * 0.008) + (50 * 0.00015)
        assert cost["hourly"] == pytest.approx(expected_per_instance * 3)


class TestIonosS3Bucket:
    def test_s3_bucket_cost(self):
        config = {"estimated_size_gb": 100, "estimated_requests_monthly": 10000}
        pricing = {"s3_storage_gb_monthly": 0.02, "s3_requests_per_1000": 0.004}

        bucket = IonosS3Bucket("test-bucket", config, pricing)
        cost = bucket.calculate_cost()

        expected_storage = 100 * 0.02
        expected_requests = (10000 / 1000) * 0.004
        expected_monthly = expected_storage + expected_requests

        assert cost["monthly"] == pytest.approx(expected_monthly)
        assert "storage" in cost["breakdown"]
        assert "requests" in cost["breakdown"]
