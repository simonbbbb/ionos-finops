import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ionos_finops.pricing.api import IonosPricingAPI, IonosAPIError
from ionos_finops.pricing.data import PricingData
from ionos_finops.pricing.calculator import CostCalculator
from ionos_finops.parser.terraform import TerraformParser


class TestIonosAPIIntegration:
    """Integration tests for IONOS API functionality"""
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response data"""
        return {
            "region": "de/fra",
            "currency": "EUR",
            "last_updated": "2026-02-25T10:00:00",
            "source": "https://api.ionos.com/cloudapi/v6/pricing",
            "compute": {
                "vcpu_hourly": 0.012,
                "ram_gb_hourly": 0.006
            },
            "storage": {
                "storage_ssd_gb_hourly": 0.00012,
                "s3_storage_gb_monthly": 0.025
            },
            "network": {
                "loadbalancer_hourly": 0.035,
                "ipv4_hourly": 0.004
            },
            "database": {
                "dbaas_postgres_vcpu_hourly": 0.018,
                "dbaas_postgres_ram_gb_hourly": 0.009
            },
            "kubernetes": {
                "k8s_control_plane_hourly": 0.0,
                "k8s_node_vcpu_hourly": 0.012,
                "k8s_node_ram_gb_hourly": 0.006
            }
        }
    
    @pytest.fixture
    def sample_terraform_config(self):
        """Sample Terraform configuration for testing"""
        return '''
        resource "ionos_server" "web" {
            name = "web-server"
            cores = 2
            ram = 4096
            volume {
                name = "system"
                size = 50
                disk_type = "SSD"
            }
        }
        
        resource "ionos_volume" "data" {
            name = "data-volume"
            size = 100
            disk_type = "SSD"
        }
        
        resource "ionos_loadbalancer" "main" {
            name = "main-lb"
        }
        '''
    
    def test_api_initialization_with_token(self):
        """Test API initialization with token"""
        api = IonosPricingAPI(api_token="test-token")
        assert api.api_token == "test-token"
        assert "Authorization" in api.session.headers
    
    def test_api_initialization_without_token(self):
        """Test API initialization without token"""
        with patch.dict('os.environ', {'IONOS_TOKEN': 'env-token'}):
            api = IonosPricingAPI()
            assert api.api_token == "env-token"
    
    def test_api_token_validation_success(self, mock_api_response):
        """Test successful API token validation"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": "de/fra", "name": "Frankfurt"}]
            mock_get.return_value = mock_response
            
            api = IonosPricingAPI(api_token="valid-token")
            assert api.validate_api_token() is True
    
    def test_api_token_validation_failure(self):
        """Test API token validation failure"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = Exception("Unauthorized")
            mock_get.return_value = mock_response
            
            api = IonosPricingAPI(api_token="invalid-token")
            assert api.validate_api_token() is False
    
    def test_get_server_pricing_success(self, mock_api_response):
        """Test successful server pricing fetch"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response["compute"]
            mock_get.return_value = mock_response
            
            api = IonosPricingAPI(api_token="test-token")
            pricing = api.get_server_pricing("de/fra")
            
            assert pricing["vcpu_hourly"] == 0.012
            assert pricing["ram_gb_hourly"] == 0.006
    
    def test_get_server_pricing_fallback(self):
        """Test server pricing fallback when API fails"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("Not found")
            mock_get.return_value = mock_response
            
            api = IonosPricingAPI(api_token="test-token")
            pricing = api.get_server_pricing("de/fra")
            
            # Should return default fallback pricing
            assert pricing["vcpu_hourly"] == 0.01
            assert pricing["ram_gb_hourly"] == 0.005
    
    def test_get_all_pricing_integration(self, mock_api_response):
        """Test complete pricing data fetch"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_get.return_value = mock_response
            
            api = IonosPricingAPI(api_token="test-token")
            pricing_data = api.get_all_pricing("de/fra")
            
            assert pricing_data["region"] == "de/fra"
            assert "compute" in pricing_data
            assert "storage" in pricing_data
            assert "network" in pricing_data
            assert "database" in pricing_data
            assert "kubernetes" in pricing_data


class TestPricingDataIntegration:
    """Integration tests for pricing data with API"""
    
    def test_pricing_data_with_api_enabled(self, mock_api_response):
        """Test pricing data initialization with API enabled"""
        with patch('ionos_finops.pricing.data.IonosPricingAPI') as mock_api_class:
            mock_api = Mock()
            mock_api.validate_api_token.return_value = True
            mock_api.get_all_pricing.return_value = mock_api_response
            mock_api_class.return_value = mock_api
            
            pricing_data = PricingData(
                region="de/fra",
                use_api=True,
                api_token="test-token"
            )
            
            assert pricing_data.use_api is True
            assert pricing_data.api_token == "test-token"
    
    def test_pricing_data_cache_update(self, mock_api_response):
        """Test pricing data cache update functionality"""
        with patch('ionos_finops.pricing.data.IonosPricingAPI') as mock_api_class:
            mock_api = Mock()
            mock_api.validate_api_token.return_value = True
            mock_api.get_all_pricing.return_value = mock_api_response
            mock_api_class.return_value = mock_api
            
            pricing_data = PricingData(
                region="de/fra",
                use_api=True,
                api_token="test-token",
                cache_ttl=0  # Force update
            )
            
            # Should have called API to update
            mock_api.get_all_pricing.assert_called_once_with("de/fra")
    
    def test_manual_pricing_update(self, mock_api_response):
        """Test manual pricing update"""
        with patch('ionos_finops.pricing.data.IonosPricingAPI') as mock_api_class:
            mock_api = Mock()
            mock_api.get_all_pricing.return_value = mock_api_response
            mock_api_class.return_value = mock_api
            
            pricing_data = PricingData(region="de/fra")
            success = pricing_data.update_pricing("test-token")
            
            assert success is True
            mock_api.get_all_pricing.assert_called_once_with("de/fra")


class TestCostCalculatorIntegration:
    """Integration tests for cost calculator with API pricing"""
    
    def test_calculator_with_api_pricing(self, sample_terraform_config):
        """Test cost calculator using API pricing"""
        mock_pricing = {
            "vcpu_hourly": 0.012,
            "ram_gb_hourly": 0.006,
            "storage_ssd_gb_hourly": 0.00012,
            "loadbalancer_hourly": 0.035,
            "ipv4_hourly": 0.004
        }
        
        with patch('ionos_finops.pricing.data.PricingData') as mock_pricing_data:
            mock_instance = Mock()
            mock_instance.get_pricing.return_value = mock_pricing
            mock_instance.region = "de/fra"
            mock_pricing_data.return_value = mock_instance
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
                f.write(sample_terraform_config)
                f.flush()
                
                try:
                    calculator = CostCalculator(
                        region="de/fra",
                        use_api=True,
                        api_token="test-token"
                    )
                    calculator.load_from_terraform(f.name)
                    
                    assert len(calculator.resources) == 3
                    
                    # Check that costs are calculated with API pricing
                    total_cost = calculator.calculate_total_cost()
                    assert total_cost["hourly"] > 0
                    
                finally:
                    Path(f.name).unlink()
    
    def test_calculator_fallback_without_api(self, sample_terraform_config):
        """Test cost calculator fallback when API is not available"""
        with patch('ionos_finops.pricing.data.PricingData') as mock_pricing_data:
            mock_instance = Mock()
            mock_instance.get_pricing.return_value = {
                "vcpu_hourly": 0.01,  # Default pricing
                "ram_gb_hourly": 0.005,
                "storage_ssd_gb_hourly": 0.0001,
                "loadbalancer_hourly": 0.034,
                "ipv4_hourly": 0.003
            }
            mock_instance.region = "de/fra"
            mock_pricing_data.return_value = mock_instance
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
                f.write(sample_terraform_config)
                f.flush()
                
                try:
                    calculator = CostCalculator(region="de/fra")
                    calculator.load_from_terraform(f.name)
                    
                    total_cost = calculator.calculate_total_cost()
                    assert total_cost["hourly"] > 0
                    
                finally:
                    Path(f.name).unlink()


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def test_full_workflow_with_mock_api(self, sample_terraform_config):
        """Test complete workflow from Terraform to cost calculation with API"""
        mock_api_pricing = {
            "region": "de/fra",
            "currency": "EUR",
            "last_updated": "2026-02-25T10:00:00",
            "compute": {"vcpu_hourly": 0.012, "ram_gb_hourly": 0.006},
            "storage": {"storage_ssd_gb_hourly": 0.00012},
            "network": {"loadbalancer_hourly": 0.035, "ipv4_hourly": 0.004},
            "database": {},
            "kubernetes": {},
            "backup": {},
            "autoscaling": {},
            "management": {}
        }
        
        with patch('ionos_finops.pricing.data.IonosPricingAPI') as mock_api_class:
            mock_api = Mock()
            mock_api.validate_api_token.return_value = True
            mock_api.get_all_pricing.return_value = mock_api_pricing
            mock_api_class.return_value = mock_api
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
                f.write(sample_terraform_config)
                f.flush()
                
                try:
                    # Parse Terraform
                    parser = TerraformParser(f.name)
                    resources = parser.parse()
                    assert len(resources) == 3
                    
                    # Calculate costs with API pricing
                    calculator = CostCalculator(
                        region="de/fra",
                        use_api=True,
                        api_token="test-token"
                    )
                    calculator.load_from_terraform(f.name)
                    
                    summary = calculator.get_summary()
                    assert summary["region"] == "de/fra"
                    assert summary["total_resources"] == 3
                    assert summary["total_cost"]["monthly"] > 0
                    
                    # Verify API pricing was used
                    mock_api.get_all_pricing.assert_called()
                    
                finally:
                    Path(f.name).unlink()
    
    def test_error_handling_and_fallback(self, sample_terraform_config):
        """Test error handling and fallback behavior"""
        with patch('ionos_finops.pricing.data.IonosPricingAPI') as mock_api_class:
            mock_api = Mock()
            mock_api.validate_api_token.return_value = False  # Invalid token
            mock_api_class.return_value = mock_api
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
                f.write(sample_terraform_config)
                f.flush()
                
                try:
                    calculator = CostCalculator(
                        region="de/fra",
                        use_api=True,
                        api_token="invalid-token"
                    )
                    calculator.load_from_terraform(f.name)
                    
                    # Should still work with fallback pricing
                    summary = calculator.get_summary()
                    assert summary["total_resources"] == 3
                    assert summary["total_cost"]["monthly"] > 0
                    
                finally:
                    Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
