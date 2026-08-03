import pytest


@pytest.fixture
def base_nr_add_data() -> dict:
    """Canonical synthetic NR-add scenario used by multiple tests."""
    return {
        "site_id": "SEA001",
        "sector_id": "A",
        "band": "n77",
        "nr_arfcn": 650000,
        "bandwidth_mhz": 100,
        "existing_nr_arfcns": [640000],
        "precheck_kpis_available": True,
        "change_ticket": "MOD-TEST-001",
    }


@pytest.fixture
def golden_nr_add_pass() -> dict:
    """Expected result for the canonical known-good NR-add scenario."""
    return {
        "decision": "PASS",
        "scenario": "NR_ADD",
        "site_id": "SEA001",
        "sector_id": "A",
        "reason_codes": ["VALIDATION_PASSED"],
        "messages": [
            "Request is inside the implemented NR-add validation boundary."
        ],
    }

@pytest.fixture
def base_carrier_change_data() -> dict:
    """Canonical synthetic bounded carrier-change scenario."""
    return {
        "site_id": "SEA002",
        "sector_id": "B",
        "technology": "NR",
        "current_arfcn": 640000,
        "proposed_arfcn": 650000,
        "current_bandwidth_mhz": 100,
        "proposed_bandwidth_mhz": 100,
        "spectrum_authorized": True,
        "neighbor_review_complete": True,
        "precheck_kpis_available": True,
        "rollback_plan_defined": True,
        "change_ticket": "MOD-TEST-002",
    }