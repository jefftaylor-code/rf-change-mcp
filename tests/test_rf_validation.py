import pytest
from pydantic import ValidationError

from src.server import (
    CarrierChangeRequest,
    NRAddRequest,
    evaluate_carrier_change,
    evaluate_nr_add,
)


@pytest.mark.parametrize(
    "overrides, expected_decision, expected_reason",
    [
        (
            {},
            "PASS",
            "VALIDATION_PASSED",
        ),
        (
            {
                "nr_arfcn": 650000,
                "existing_nr_arfcns": [640000, 650000],
            },
            "FAIL",
            "DUPLICATE_NR_ARFCN",
        ),
        (
            {
                "band": "n77",
                "bandwidth_mhz": 20,
            },
            "FAIL",
            "BANDWIDTH_OUTSIDE_BOUNDED_RULE",
        ),
        (
            {
                "band": "n71",
                "bandwidth_mhz": 40,
            },
            "FAIL",
            "BANDWIDTH_OUTSIDE_BOUNDED_RULE",
        ),
        (
            {
                "precheck_kpis_available": False,
            },
            "FAIL",
            "PRECHECK_KPIS_MISSING",
        ),
    ],
)
def test_synthetic_nr_add_scenarios(
    base_nr_add_data,
    overrides,
    expected_decision,
    expected_reason,
):
    """Exercise synthetic RF modification scenarios."""

    data = {**base_nr_add_data, **overrides}
    request = NRAddRequest(**data)

    result = evaluate_nr_add(request)

    assert result.decision == expected_decision
    assert expected_reason in result.reason_codes


def test_golden_nr_add_regression(
    base_nr_add_data,
    golden_nr_add_pass,
):
    """Canonical scenario must continue producing the known-good result."""

    request = NRAddRequest(**base_nr_add_data)

    result = evaluate_nr_add(request)

    assert result.model_dump() == golden_nr_add_pass


@pytest.mark.parametrize(
    "invalid_field",
    [
        {"band": "n999"},
        {"nr_arfcn": 0},
        {"site_id": ""},
        {"change_ticket": ""},
    ],
)
def test_invalid_structured_input_fails_closed(
    base_nr_add_data,
    invalid_field,
):
    """Invalid structured inputs must be rejected rather than guessed."""

    data = {**base_nr_add_data, **invalid_field}

    with pytest.raises(ValidationError):
        NRAddRequest(**data)

@pytest.mark.parametrize(
    "overrides, expected_decision, expected_reason",
    [
        (
            {},
            "PASS",
            "VALIDATION_PASSED",
        ),
        (
            {
                "proposed_arfcn": 640000,
            },
            "FAIL",
            "NO_ARFCN_CHANGE",
        ),
        (
            {
                "proposed_bandwidth_mhz": 80,
            },
            "FAIL",
            "BANDWIDTH_CHANGE_OUT_OF_SCOPE",
        ),
        (
            {
                "spectrum_authorized": False,
            },
            "FAIL",
            "SPECTRUM_AUTHORIZATION_MISSING",
        ),
        (
            {
                "neighbor_review_complete": False,
            },
            "FAIL",
            "NEIGHBOR_REVIEW_INCOMPLETE",
        ),
        (
            {
                "rollback_plan_defined": False,
            },
            "FAIL",
            "ROLLBACK_PLAN_MISSING",
        ),
    ],
)
def test_synthetic_carrier_change_scenarios(
    base_carrier_change_data,
    overrides,
    expected_decision,
    expected_reason,
):
    """Exercise synthetic bounded carrier-change scenarios."""

    data = {**base_carrier_change_data, **overrides}
    request = CarrierChangeRequest(**data)

    result = evaluate_carrier_change(request)

    assert result.decision == expected_decision
    assert expected_reason in result.reason_codes
