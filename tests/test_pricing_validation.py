import pytest
import json
from decimal import Decimal
from typing import Dict, Any

from ionos_finops.pricing.data import PricingData
from ionos_finops.pricing.api import IonosPricingAPI
from ionos_finops.resources import RESOURCE_REGISTRY
from ionos_finops.resources.base import Resource


class TestPricingValidation:
    """Tests to validate pricing data integrity and accuracy"""
    
    @pytest.fixture
    def sample_pricing_data(self):
        """Sample pricing data for validation"""
        return {
            "region": "de/fra",
            "currency": "EUR",
            "last_updated": "2026-02-25",
            "source": "test",
            "compute": {
                "vcpu_hourly": 0.01,
                "ram_gb_hourly": 0.005
            },
            "storage": {
                "storage_hdd_gb_hourly": 0.00005,
                "storage_ssd_gb_hourly": 0.0001,
                "storage_ssd_premium_gb_hourly": 0.00015,
                "s3_storage_gb_monthly": 0.02,
                "s3_requests_per_1000": 0.004,
                "backup_gb_hourly": 0.00015,
                "snapshot_gb_hourly": 0.00008
            },
            "network": {
                "loadbalancer_hourly": 0.034,
                "ipv4_hourly": 0.003,
                "natgateway_hourly": 0.05,
                "crossconnect_monthly": 100.0
            },
            "database": {
                "dbaas_postgres_vcpu_hourly": 0.015,
                "dbaas_postgres_ram_gb_hourly": 0.008,
                "dbaas_postgres_storage_ssd_gb_hourly": 0.00015,
                "dbaas_mongo_vcpu_hourly": 0.015,
                "dbaas_mongo_ram_gb_hourly": 0.008,
                "dbaas_mongo_storage_ssd_gb_hourly": 0.00015
            },
            "kubernetes": {
                "k8s_control_plane_hourly": 0.0,
                "k8s_node_vcpu_hourly": 0.01,
                "k8s_node_ram_gb_hourly": 0.005,
                "k8s_node_storage_ssd_gb_hourly": 0.0001
            },
            "backup": {
                "backup_plan_base_monthly": 5.0,
                "backup_gb_hourly": 0.00015
            },
            "autoscaling": {
                "autoscaling_monthly_fee": 0.0
            },
            "management": {
                "image_storage_gb_hourly": 0.00005
            }
        }
    
    def test_pricing_data_structure_validation(self, sample_pricing_data):
        """Test that pricing data has required structure"""
        required_categories = [
            "compute", "storage", "network", "database", 
            "kubernetes", "backup", "autoscaling", "management"
        ]
        
        for category in required_categories:
            assert category in sample_pricing_data, f"Missing category: {category}"
            assert isinstance(sample_pricing_data[category], dict), f"Category {category} must be a dict"
    
    def test_pricing_values_are_positive_numbers(self, sample_pricing_data):
        """Test that all pricing values are positive numbers"""
        for category, pricing in sample_pricing_data.items():
            if isinstance(pricing, dict):
                for key, value in pricing.items():
                    if key.endswith("_hourly") or key.endswith("_monthly") or key.endswith("_per_1000"):
                        assert isinstance(value, (int, float)), f"{key} must be a number"
                        assert value >= 0, f"{key} must be non-negative: {value}"
    
    def test_pricing_consistency_across_regions(self):
        """Test pricing consistency logic across regions"""
        regions = ["de/fra", "de/ber", "gb/lhr", "us/las"]
        
        for region in regions:
            pricing_data = PricingData(region=region)
            pricing = pricing_data.get_pricing("ionos_server")
            
            # Basic pricing should exist
            assert "vcpu_hourly" in pricing
            assert "ram_gb_hourly" in pricing
            assert isinstance(pricing["vcpu_hourly"], (int, float))
            assert isinstance(pricing["ram_gb_hourly"], (int, float))
    
    def test_storage_pricing_hierarchy(self, sample_pricing_data):
        """Test that storage pricing follows expected hierarchy"""
        storage = sample_pricing_data["storage"]
        
        # SSD should be more expensive than HDD
        assert storage["storage_ssd_gb_hourly"] > storage["storage_hdd_gb_hourly"]
        
        # Premium SSD should be most expensive
        assert storage["storage_ssd_premium_gb_hourly"] > storage["storage_ssd_gb_hourly"]
        
        # Backup should be cheaper than active storage
        assert storage["backup_gb_hourly"] < storage["storage_hdd_gb_hourly"]
    
    def test_database_pricing_consistency(self, sample_pricing_data):
        """Test database pricing consistency across engines"""
        db = sample_pricing_data["database"]
        
        # PostgreSQL and MongoDB should have similar pricing structure
        postgres_vcpu = db["dbaas_postgres_vcpu_hourly"]
        mongo_vcpu = db["dbaas_mongo_vcpu_hourly"]
        
        # Should be reasonably close (within 20%)
        ratio = max(postgres_vcpu, mongo_vcpu) / min(postgres_vcpu, mongo_vcpu)
        assert ratio <= 1.2, f"Database vCPU pricing too different: {ratio}"
    
    def test_pricing_units_are_reasonable(self, sample_pricing_data):
        """Test that pricing units are reasonable"""
        # vCPU pricing should be in cents per hour range
        vcpu_hourly = sample_pricing_data["compute"]["vcpu_hourly"]
        assert 0.005 <= vcpu_hourly <= 0.05, f"vCPU hourly price unreasonable: {vcpu_hourly}"
        
        # RAM pricing should be in cents per GB per hour range
        ram_hourly = sample_pricing_data["compute"]["ram_gb_hourly"]
        assert 0.002 <= ram_hourly <= 0.02, f"RAM hourly price unreasonable: {ram_hourly}"
        
        # Storage pricing should be in fractions of cents per GB per hour
        ssd_hourly = sample_pricing_data["storage"]["storage_ssd_gb_hourly"]
        assert 0.00005 <= ssd_hourly <= 0.0005, f"SSD hourly price unreasonable: {ssd_hourly}"
    
    def test_monthly_vs_hourly_consistency(self, sample_pricing_data):
        """Test consistency between monthly and hourly pricing"""
        # For services with both monthly and hourly pricing
        # Monthly ≈ Hourly × 730 (average hours per month)
        
        # Test crossconnect pricing
        crossconnect_monthly = sample_pricing_data["network"]["crossconnect_monthly"]
        crossconnect_hourly = crossconnect_monthly / 730
        assert 0.1 <= crossconnect_hourly <= 1.0, f"Crossconnect hourly price unreasonable: {crossconnect_hourly}"
    
    def test_resource_cost_calculation_accuracy(self, sample_pricing_data):
        """Test that resource cost calculations are accurate"""
        # Test server cost calculation
        config = {"cores": 2, "ram": 4, "volume": {"size": 50, "type": "SSD"}}
        pricing = sample_pricing_data["compute"].copy()
        pricing.update(sample_pricing_data["storage"])
        
        from ionos_finops.resources.compute import IonosServer
        server = IonosServer("test-server", config, pricing)
        cost = server.calculate_cost()
        
        # Manual calculation
        expected_hourly = (
            2 * pricing["vcpu_hourly"] + 
            4 * pricing["ram_gb_hourly"] + 
            50 * pricing["storage_ssd_gb_hourly"]
        )
        
        assert abs(cost["hourly"] - expected_hourly) < 0.0001, f"Cost calculation inaccurate: {cost['hourly']} vs {expected_hourly}"
        assert cost["monthly"] == cost["hourly"] * 730, "Monthly cost calculation incorrect"
    
    def test_all_supported_resources_have_pricing(self, sample_pricing_data):
        """Test that all supported resources have required pricing"""
        all_pricing = {}
        for category in sample_pricing_data.values():
            if isinstance(category, dict):
                all_pricing.update(category)
        
        # Check each resource type has required pricing
        for resource_type, resource_class in RESOURCE_REGISTRY.items():
            # Create a minimal resource instance to check pricing requirements
            try:
                resource = resource_class("test", {}, all_pricing)
                cost = resource.calculate_cost()
                
                # Should not raise exceptions and should return valid cost structure
                assert "hourly" in cost
                assert "monthly" in cost
                assert isinstance(cost["hourly"], (int, float))
                assert isinstance(cost["monthly"], (int, float))
                
            except Exception as e:
                pytest.fail(f"Resource {resource_type} failed with pricing: {e}")
    
    def test_pricing_data_json_serialization(self, sample_pricing_data):
        """Test that pricing data can be serialized to JSON"""
        try:
            json_str = json.dumps(sample_pricing_data)
            parsed = json.loads(json_str)
            
            assert parsed == sample_pricing_data
        except (TypeError, ValueError) as e:
            pytest.fail(f"Pricing data not JSON serializable: {e}")
    
    def test_currency_consistency(self, sample_pricing_data):
        """Test that currency is consistent"""
        assert "currency" in sample_pricing_data
        assert sample_pricing_data["currency"] == "EUR"
    
    def test_metadata_fields_present(self, sample_pricing_data):
        """Test required metadata fields are present"""
        required_fields = ["region", "currency", "last_updated", "source"]
        
        for field in required_fields:
            assert field in sample_pricing_data, f"Missing metadata field: {field}"
            assert sample_pricing_data[field], f"Empty metadata field: {field}"
    
    def test_pricing_data_version_compatibility(self):
        """Test that pricing data structure is version compatible"""
        pricing_data = PricingData()
        
        # Should have all required categories
        pricing = pricing_data.get_pricing("ionos_server")
        assert isinstance(pricing, dict)
        assert len(pricing) > 0
    
    def test_edge_cases_in_pricing(self):
        """Test edge cases in pricing calculations"""
        # Zero pricing for free resources
        free_pricing = {"vcpu_hourly": 0, "ram_gb_hourly": 0}
        
        from ionos_finops.resources.networking import IonosLAN
        lan = IonosLAN("test-lan", {}, free_pricing)
        cost = lan.calculate_cost()
        
        assert cost["hourly"] == 0
        assert cost["monthly"] == 0
    
    def test_precision_in_calculations(self):
        """Test that calculations maintain appropriate precision"""
        config = {"cores": 1, "ram": 1, "volume": {"size": 1, "type": "SSD"}}
        pricing = {
            "vcpu_hourly": 0.012345,
            "ram_gb_hourly": 0.006789,
            "storage_ssd_gb_hourly": 0.000123
        }
        
        from ionos_finops.resources.compute import IonosServer
        server = IonosServer("test", config, pricing)
        cost = server.calculate_cost()
        
        # Should maintain reasonable precision
        assert cost["hourly"] > 0
        assert len(str(cost["hourly"]).split('.')[-1]) <= 6  # Max 6 decimal places


class TestPricingValidationWithRealData:
    """Tests with real pricing data files"""
    
    def test_default_pricing_file_validation(self):
        """Test that default pricing file is valid"""
        pricing_data = PricingData()
        
        # Should load without errors
        assert pricing_data.pricing_data is not None
        assert pricing_data.region in pricing_data.pricing_data.get("region", "")
    
    def test_pricing_file_format_validation(self):
        """Test that pricing files have correct format"""
        from pathlib import Path
        
        package_dir = Path(__file__).parent.parent
        pricing_dir = package_dir / "ionos_finops" / "pricing_data"
        
        for pricing_file in pricing_dir.glob("*.json"):
            with open(pricing_file, 'r') as f:
                try:
                    data = json.load(f)
                    
                    # Validate structure
                    assert "region" in data
                    assert "currency" in data
                    assert isinstance(data.get("compute", {}), dict)
                    assert isinstance(data.get("storage", {}), dict)
                    
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {pricing_file}: {e}")
                except AssertionError as e:
                    pytest.fail(f"Invalid structure in {pricing_file}: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
