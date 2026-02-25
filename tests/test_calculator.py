import pytest
from ionos_finops.pricing.calculator import CostCalculator
from ionos_finops.resources.compute import IonosServer


def test_calculator_initialization():
    calculator = CostCalculator(region="de/fra")
    assert calculator.region == "de/fra"
    assert len(calculator.resources) == 0


def test_total_cost_calculation():
    calculator = CostCalculator(region="de/fra")
    
    pricing = {
        "vcpu_hourly": 0.01,
        "ram_gb_hourly": 0.005,
        "storage_ssd_gb_hourly": 0.0001
    }
    
    server1 = IonosServer(
        "server1",
        {"cores": 2, "ram": 4, "volume": {"size": 50, "type": "SSD"}},
        pricing
    )
    
    server2 = IonosServer(
        "server2",
        {"cores": 4, "ram": 8, "volume": {"size": 100, "type": "SSD"}},
        pricing
    )
    
    calculator.resources = [server1, server2]
    
    total_cost = calculator.calculate_total_cost()
    
    assert total_cost["hourly"] > 0
    assert total_cost["monthly"] == total_cost["hourly"] * 730
    assert total_cost["yearly"] == total_cost["monthly"] * 12


def test_cost_by_resource_type():
    calculator = CostCalculator(region="de/fra")
    
    pricing = {
        "vcpu_hourly": 0.01,
        "ram_gb_hourly": 0.005,
        "storage_ssd_gb_hourly": 0.0001
    }
    
    server1 = IonosServer("server1", {"cores": 2, "ram": 4, "volume": {"size": 50, "type": "SSD"}}, pricing)
    server2 = IonosServer("server2", {"cores": 2, "ram": 4, "volume": {"size": 50, "type": "SSD"}}, pricing)
    
    calculator.resources = [server1, server2]
    
    costs_by_type = calculator.get_cost_by_resource_type()
    
    assert "ionos_server" in costs_by_type
    assert costs_by_type["ionos_server"]["count"] == 2
    assert costs_by_type["ionos_server"]["monthly"] > 0


def test_detailed_breakdown():
    calculator = CostCalculator(region="de/fra")
    
    pricing = {
        "vcpu_hourly": 0.01,
        "ram_gb_hourly": 0.005,
        "storage_ssd_gb_hourly": 0.0001
    }
    
    server = IonosServer("test-server", {"cores": 2, "ram": 4, "volume": {"size": 50, "type": "SSD"}}, pricing)
    calculator.resources = [server]
    
    breakdown = calculator.get_detailed_breakdown()
    
    assert len(breakdown) == 1
    assert breakdown[0]["name"] == "test-server"
    assert breakdown[0]["type"] == "ionos_server"
    assert "costs" in breakdown[0]
    assert "breakdown" in breakdown[0]["costs"]
