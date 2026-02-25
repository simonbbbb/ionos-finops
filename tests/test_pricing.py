import pytest

from ionos_finops.pricing.data import PricingData


def test_pricing_data_initialization():
    pricing = PricingData(region="de/fra")
    assert pricing.region == "de/fra"
    assert pricing.pricing_data is not None


def test_default_pricing():
    pricing = PricingData()
    data = pricing.pricing_data

    assert "compute" in data or "vcpu_hourly" in pricing.get_pricing("ionos_server")
    assert "storage" in data or "storage_ssd_gb_hourly" in pricing.get_pricing("ionos_volume")


def test_custom_pricing_override():
    custom = {"compute": {"vcpu_hourly": 0.02}}

    pricing = PricingData(custom_pricing=custom)
    all_pricing = pricing.get_pricing("ionos_server")

    assert all_pricing.get("vcpu_hourly") == 0.02


def test_get_pricing_for_resource():
    pricing = PricingData()
    resource_pricing = pricing.get_pricing("ionos_server")

    assert isinstance(resource_pricing, dict)
    assert len(resource_pricing) > 0


def test_get_category_pricing():
    pricing = PricingData()
    compute_pricing = pricing.get_category_pricing("compute")

    assert isinstance(compute_pricing, dict)
