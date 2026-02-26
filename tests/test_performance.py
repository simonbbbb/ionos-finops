"""Performance benchmarks for IONOS FinOps."""

import tempfile
from pathlib import Path

import pytest

from ionos_finops.pricing.calculator import CostCalculator
from ionos_finops.parser.terraform import TerraformParser
from ionos_finops.pricing.data import PricingData


class TestPerformanceBenchmarks:
    """Performance benchmarks for IONOS FinOps."""

    @pytest.fixture
    def medium_terraform_config(self):
        """Generate a medium Terraform configuration."""
        resources = []
        for i in range(20):
            resources.append(
                f'resource "ionos_server" "web_{i}" {{\n'
                f'    name = "web-server-{i}"\n'
                f'    cores = 2\n'
                f'    ram = 4096\n'
                f'    volume {{\n'
                f'        name = "system-{i}"\n'
                f'        size = 50\n'
                f'        disk_type = "SSD"\n'
                f'    }}\n'
                f'}}\n'
            )
        for i in range(10):
            resources.append(
                f'resource "ionos_volume" "data_{i}" {{\n'
                f'    name = "data-volume-{i}"\n'
                f'    size = 100\n'
                f'    disk_type = "SSD"\n'
                f'}}\n'
            )
        return "\n".join(resources)

    def test_parsing_performance_medium(self, medium_terraform_config):
        """Benchmark Terraform parsing performance for medium configurations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(medium_terraform_config)
            f.flush()
            try:
                parser = TerraformParser(f.name)
                resources = parser.parse()
                assert len(resources) == 30
            finally:
                Path(f.name).unlink()

    def test_cost_calculation_performance_medium(self, medium_terraform_config):
        """Benchmark cost calculation performance for medium configurations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(medium_terraform_config)
            f.flush()
            try:
                calculator = CostCalculator(region="de/fra")
                calculator.load_from_terraform(f.name)
                summary = calculator.get_summary()
                assert summary["total_resources"] == 30
            finally:
                Path(f.name).unlink()

    def test_pricing_data_loading_performance(self):
        """Benchmark pricing data loading performance."""
        regions = ["de/fra", "de/ber", "gb/lhr"]
        for region in regions:
            pricing_data = PricingData(region=region)
            pricing = pricing_data.get_pricing("ionos_server")
            assert len(pricing) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
