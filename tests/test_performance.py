import pytest
import time
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any

from ionos_finops.pricing.calculator import CostCalculator
from ionos_finops.parser.terraform import TerraformParser
from ionos_finops.pricing.data import PricingData


class TestPerformanceBenchmarks:
    """Performance benchmarks for IONOS FinOps"""

    @pytest.fixture
    def large_terraform_config(self):
        """Generate a large Terraform configuration for performance testing"""
        resources = []

        # Generate 100 servers
        for i in range(100):
            resources.append(
                f"""
resource "ionos_server" "server_{i}" {{
    name = "server-{i}"
    cores = {2 + (i % 4)}  # 2-5 cores
    ram = {4 + (i % 8) * 2}  # 4-20 GB RAM
    volume {{
        name = "system-{i}"
        size = {50 + (i % 100)}  # 50-149 GB
        disk_type = "{['SSD', 'HDD'][i % 2]}"
    }}
}}
"""
            )

        # Generate 50 volumes
        for i in range(50):
            resources.append(
                f"""
resource "ionos_volume" "volume_{i}" {{
    name = "data-volume-{i}"
    size = {100 + i * 2}  # 100-198 GB
    disk_type = "{['SSD', 'SSD_Premium', 'HDD'][i % 3]}"
}}
"""
            )

        # Generate 20 load balancers
        for i in range(20):
            resources.append(
                f"""
resource "ionos_loadbalancer" "lb_{i}" {{
    name = "loadbalancer-{i}"
}}
"""
            )

        # Generate 10 database clusters
        for i in range(10):
            resources.append(
                f"""
resource "ionos_pg_cluster" "postgres_{i}" {{
    cores = {2 + (i % 4)}
    ram = {4 + (i % 8) * 2}
    storage_size = {50 + i * 10}
    storage_type = "SSD"
    instances = {1 + (i % 3)}
}}
"""
            )

        return "\n".join(resources)

    @pytest.fixture
    def medium_terraform_config(self):
        """Generate a medium Terraform configuration"""
        resources = []

        # Generate 20 servers
        for i in range(20):
            resources.append(
                f"""
resource "ionos_server" "web_{i}" {{
    name = "web-server-{i}"
    cores = 2
    ram = 4096
    volume {{
        name = "system-{i}"
        size = 50
        disk_type = "SSD"
    }}
}}
"""
            )

        # Generate 10 volumes
        for i in range(10):
            resources.append(
                f"""
resource "ionos_volume" "data_{i}" {{
    name = "data-volume-{i}"
    size = 100
    disk_type = "SSD"
}}
"""
            )

        return "\n".join(resources)

    def test_parsing_performance_large(self, large_terraform_config):
        """Benchmark Terraform parsing performance for large configurations"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(large_terraform_config)
            f.flush()

            try:
                start_time = time.time()
                parser = TerraformParser(f.name)
                resources = parser.parse()
                end_time = time.time()

                parse_time = end_time - start_time

                # Performance assertions
                assert parse_time < 2.0, f"Parsing took too long: {parse_time:.2f}s"
                assert len(resources) == 180, f"Expected 180 resources, got {len(resources)}"

                print(f"✅ Parsed {len(resources)} resources in {parse_time:.3f}s")
                print(f"   Rate: {len(resources)/parse_time:.0f} resources/second")

            finally:
                Path(f.name).unlink()

    def test_parsing_performance_medium(self, medium_terraform_config):
        """Benchmark Terraform parsing performance for medium configurations"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(medium_terraform_config)
            f.flush()

            try:
                start_time = time.time()
                parser = TerraformParser(f.name)
                resources = parser.parse()
                end_time = time.time()

                parse_time = end_time - start_time

                # Performance assertions
                assert parse_time < 0.5, f"Parsing took too long: {parse_time:.2f}s"
                assert len(resources) == 30, f"Expected 30 resources, got {len(resources)}"

                print(f"✅ Parsed {len(resources)} resources in {parse_time:.3f}s")

            finally:
                Path(f.name).unlink()

    def test_cost_calculation_performance_large(self, large_terraform_config):
        """Benchmark cost calculation performance for large configurations"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(large_terraform_config)
            f.flush()

            try:
                calculator = CostCalculator(region="de/fra")

                start_time = time.time()
                calculator.load_from_terraform(f.name)
                summary = calculator.get_summary()
                end_time = time.time()

                calc_time = end_time - start_time

                # Performance assertions
                assert calc_time < 3.0, f"Cost calculation took too long: {calc_time:.2f}s"
                assert summary["total_resources"] == 180
                assert summary["total_cost"]["monthly"] > 0

                print(
                    f"✅ Calculated costs for {summary['total_resources']} resources in {calc_time:.3f}s"
                )
                print(f"   Rate: {summary['total_resources']/calc_time:.0f} resources/second")
                print(f"   Total monthly cost: €{summary['total_cost']['monthly']:.2f}")

            finally:
                Path(f.name).unlink()

    def test_cost_calculation_performance_medium(self, medium_terraform_config):
        """Benchmark cost calculation performance for medium configurations"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(medium_terraform_config)
            f.flush()

            try:
                calculator = CostCalculator(region="de/fra")

                start_time = time.time()
                calculator.load_from_terraform(f.name)
                summary = calculator.get_summary()
                end_time = time.time()

                calc_time = end_time - start_time

                # Performance assertions
                assert calc_time < 0.5, f"Cost calculation took too long: {calc_time:.2f}s"
                assert summary["total_resources"] == 30

                print(
                    f"✅ Calculated costs for {summary['total_resources']} resources in {calc_time:.3f}s"
                )

            finally:
                Path(f.name).unlink()

    def test_pricing_data_loading_performance(self):
        """Benchmark pricing data loading performance"""
        regions = ["de/fra", "de/ber", "gb/lhr", "us/las", "fr/par"]

        start_time = time.time()
        for region in regions:
            pricing_data = PricingData(region=region)
            pricing = pricing_data.get_pricing("ionos_server")
            assert len(pricing) > 0
        end_time = time.time()

        load_time = end_time - start_time
        avg_time = load_time / len(regions)

        # Performance assertions
        assert avg_time < 0.1, f"Pricing loading took too long: {avg_time:.3f}s per region"

        print(f"✅ Loaded pricing for {len(regions)} regions in {load_time:.3f}s")
        print(f"   Average: {avg_time:.3f}s per region")

    def test_output_formatting_performance(self, large_terraform_config):
        """Benchmark output formatting performance"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(large_terraform_config)
            f.flush()

            try:
                calculator = CostCalculator(region="de/fra")
                calculator.load_from_terraform(f.name)
                summary = calculator.get_summary()

                # Test table formatting
                from ionos_finops.output.table import TableFormatter

                table_formatter = TableFormatter()

                start_time = time.time()
                table_output = table_formatter.format(summary)
                end_time = time.time()

                table_time = end_time - start_time

                # Test JSON formatting
                from ionos_finops.output.json import JSONFormatter

                json_formatter = JSONFormatter()

                start_time = time.time()
                json_output = json_formatter.format(summary)
                end_time = time.time()

                json_time = end_time - start_time

                # Test HTML formatting
                from ionos_finops.output.html import HTMLFormatter

                html_formatter = HTMLFormatter()

                start_time = time.time()
                html_output = html_formatter.format(summary)
                end_time = time.time()

                html_time = end_time - start_time

                # Performance assertions
                assert table_time < 1.0, f"Table formatting took too long: {table_time:.2f}s"
                assert json_time < 0.5, f"JSON formatting took too long: {json_time:.2f}s"
                assert html_time < 1.0, f"HTML formatting took too long: {html_time:.2f}s"

                print(f"✅ Formatted outputs for {summary['total_resources']} resources:")
                print(f"   Table: {table_time:.3f}s ({len(table_output)} chars)")
                print(f"   JSON:  {json_time:.3f}s ({len(json_output)} chars)")
                print(f"   HTML:  {html_time:.3f}s ({len(html_output)} chars)")

            finally:
                Path(f.name).unlink()

    def test_memory_usage_large_config(self, large_terraform_config):
        """Test memory usage with large configurations"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(large_terraform_config)
            f.flush()

            try:
                calculator = CostCalculator(region="de/fra")
                calculator.load_from_terraform(f.name)
                summary = calculator.get_summary()

                peak_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = peak_memory - initial_memory

                # Memory assertions (should be reasonable for 180 resources)
                assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB"

                print(f"✅ Memory usage for {summary['total_resources']} resources:")
                print(f"   Initial: {initial_memory:.1f}MB")
                print(f"   Peak: {peak_memory:.1f}MB")
                print(f"   Increase: {memory_increase:.1f}MB")
                print(f"   Per resource: {memory_increase/summary['total_resources']:.2f}MB")

            finally:
                Path(f.name).unlink()

    def test_api_performance_simulation(self):
        """Test API performance with simulated responses"""
        from unittest.mock import Mock, patch
        from ionos_finops.pricing.api import IonosPricingAPI

        mock_pricing = {
            "compute": {"vcpu_hourly": 0.01, "ram_gb_hourly": 0.005},
            "storage": {"storage_ssd_gb_hourly": 0.0001},
            "network": {"loadbalancer_hourly": 0.034},
            "database": {"dbaas_postgres_vcpu_hourly": 0.015},
            "kubernetes": {"k8s_node_vcpu_hourly": 0.01},
        }

        with patch("requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_pricing
            mock_get.return_value = mock_response

            api = IonosPricingAPI(api_token="test-token")

            start_time = time.time()
            pricing_data = api.get_all_pricing("de/fra")
            end_time = time.time()

            api_time = end_time - start_time

            # Performance assertions
            assert api_time < 1.0, f"API call took too long: {api_time:.2f}s"
            assert "compute" in pricing_data

            print(f"✅ API call completed in {api_time:.3f}s")

    def test_concurrent_calculations(self, medium_terraform_config):
        """Test performance of concurrent cost calculations"""
        import threading
        import queue

        results = queue.Queue()

        def worker():
            with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                f.write(medium_terraform_config)
                f.flush()

                try:
                    calculator = CostCalculator(region="de/fra")
                    calculator.load_from_terraform(f.name)
                    summary = calculator.get_summary()
                    results.put(summary)
                finally:
                    Path(f.name).unlink()

        # Run 5 concurrent calculations
        threads = []
        start_time = time.time()

        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        concurrent_time = end_time - start_time

        # Collect results
        summaries = []
        while not results.empty():
            summaries.append(results.get())

        # Performance assertions
        assert len(summaries) == 5, "Not all calculations completed"
        assert (
            concurrent_time < 2.0
        ), f"Concurrent calculations took too long: {concurrent_time:.2f}s"

        print(f"✅ Completed {len(summaries)} concurrent calculations in {concurrent_time:.3f}s")
        print(f"   Average per calculation: {concurrent_time/len(summaries):.3f}s")

    def test_scalability_analysis(self):
        """Analyze scalability with different configuration sizes"""
        resource_counts = [10, 50, 100, 200, 500]
        times = []

        for count in resource_counts:
            # Generate configuration
            resources = []
            for i in range(count):
                resources.append(
                    f"""
resource "ionos_server" "server_{i}" {{
    name = "server-{i}"
    cores = 2
    ram = 4096
    volume {{
        name = "system-{i}"
        size = 50
        disk_type = "SSD"
    }}
}}
"""
                )

            config = "\n".join(resources)

            with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
                f.write(config)
                f.flush()

                try:
                    calculator = CostCalculator(region="de/fra")

                    start_time = time.time()
                    calculator.load_from_terraform(f.name)
                    calculator.get_summary()
                    end_time = time.time()

                    calc_time = end_time - start_time
                    times.append(calc_time)

                finally:
                    Path(f.name).unlink()

        # Analyze scalability
        print(f"✅ Scalability analysis:")
        for i, (count, time_taken) in enumerate(zip(resource_counts, times)):
            rate = count / time_taken
            print(f"   {count:3d} resources: {time_taken:.3f}s ({rate:.0f} resources/sec)")

        # Check that performance scales reasonably (not exponentially worse)
        if len(times) >= 2:
            # Last vs first should not be more than 10x slower despite 50x more resources
            ratio = times[-1] / times[0]
            resource_ratio = resource_counts[-1] / resource_counts[0]
            efficiency = resource_ratio / ratio

            print(f"   Scaling efficiency: {efficiency:.1f}x (higher is better)")
            assert efficiency > 5, f"Poor scaling efficiency: {efficiency:.1f}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
