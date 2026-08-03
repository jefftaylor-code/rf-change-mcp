from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field


mcp = FastMCP(
    "RFDS Validation Prototype",
    instructions=(
        "Prototype MCP server for bounded cellular RF modification validation. "
        "Validation fails closed when required information is missing or "
        "outside the implemented scenario boundaries."
    ),
)


class NRAddRequest(BaseModel):
    """Structured input for a bounded NR carrier-add validation."""

    site_id: str = Field(min_length=1)
    sector_id: str = Field(min_length=1)

    band: Literal["n5", "n41", "n71", "n77"]

    nr_arfcn: int = Field(gt=0)

    bandwidth_mhz: Literal[
        5, 10, 15, 20, 40, 50, 60, 80, 100
    ]

    existing_nr_arfcns: list[int] = Field(default_factory=list)

    precheck_kpis_available: bool

    change_ticket: str = Field(min_length=1)

class CarrierChangeRequest(BaseModel):
    """Structured input for a bounded LTE/NR carrier change."""

    site_id: str = Field(min_length=1)
    sector_id: str = Field(min_length=1)

    technology: Literal["LTE", "NR"]

    current_arfcn: int = Field(gt=0)
    proposed_arfcn: int = Field(gt=0)

    current_bandwidth_mhz: int = Field(gt=0)
    proposed_bandwidth_mhz: int = Field(gt=0)

    spectrum_authorized: bool
    neighbor_review_complete: bool
    precheck_kpis_available: bool
    rollback_plan_defined: bool

    change_ticket: str = Field(min_length=1)

class ValidationResult(BaseModel):
    """Structured result returned by RF validation tools."""

    decision: Literal["PASS", "FAIL"]
    scenario: str
    site_id: str
    sector_id: str
    reason_codes: list[str]
    messages: list[str]


def evaluate_nr_add(request: NRAddRequest) -> ValidationResult:
    """
    Evaluate a bounded NR carrier-add scenario.

    This is intentionally not a full RFDS or 3GPP rules engine.
    Anything outside the explicitly implemented rules fails closed.
    """

    reason_codes: list[str] = []
    messages: list[str] = []

    # Duplicate carrier check.
    if request.nr_arfcn in request.existing_nr_arfcns:
        reason_codes.append("DUPLICATE_NR_ARFCN")
        messages.append(
            f"NR-ARFCN {request.nr_arfcn} already exists on the sector."
        )

    # Prototype-specific bandwidth boundaries.
    low_band = {"n5", "n71"}
    mid_band = {"n41", "n77"}

    if request.band in low_band and request.bandwidth_mhz > 20:
        reason_codes.append("BANDWIDTH_OUTSIDE_BOUNDED_RULE")
        messages.append(
            f"{request.band} bandwidth above 20 MHz is outside "
            "this prototype's supported validation boundary."
        )

    if request.band in mid_band and request.bandwidth_mhz < 40:
        reason_codes.append("BANDWIDTH_OUTSIDE_BOUNDED_RULE")
        messages.append(
            f"{request.band} bandwidth below 40 MHz is outside "
            "this prototype's supported validation boundary."
        )

    # Require evidence for pre-change validation.
    if not request.precheck_kpis_available:
        reason_codes.append("PRECHECK_KPIS_MISSING")
        messages.append(
            "Required pre-change KPI evidence is not available."
        )

    if reason_codes:
        return ValidationResult(
            decision="FAIL",
            scenario="NR_ADD",
            site_id=request.site_id,
            sector_id=request.sector_id,
            reason_codes=reason_codes,
            messages=messages,
        )

    return ValidationResult(
        decision="PASS",
        scenario="NR_ADD",
        site_id=request.site_id,
        sector_id=request.sector_id,
        reason_codes=["VALIDATION_PASSED"],
        messages=[
            "Request is inside the implemented NR-add validation boundary."
        ],
    )

def evaluate_carrier_change(
    request: CarrierChangeRequest,
) -> ValidationResult:
    """
    Evaluate a bounded LTE/NR carrier-change scenario.

    Scope is intentionally narrow:
    - ARFCN change only
    - no simultaneous bandwidth change
    - required engineering evidence must be present

    Anything outside that boundary fails closed.
    """

    reason_codes: list[str] = []
    messages: list[str] = []

    if request.current_arfcn == request.proposed_arfcn:
        reason_codes.append("NO_ARFCN_CHANGE")
        messages.append(
            "Proposed ARFCN is identical to the current ARFCN."
        )

    if request.current_bandwidth_mhz != request.proposed_bandwidth_mhz:
        reason_codes.append("BANDWIDTH_CHANGE_OUT_OF_SCOPE")
        messages.append(
            "Simultaneous bandwidth change is outside this prototype's "
            "bounded carrier-change scenario."
        )

    if not request.spectrum_authorized:
        reason_codes.append("SPECTRUM_AUTHORIZATION_MISSING")
        messages.append(
            "Spectrum authorization evidence is not available."
        )

    if not request.neighbor_review_complete:
        reason_codes.append("NEIGHBOR_REVIEW_INCOMPLETE")
        messages.append(
            "Neighbor-relation impact review is incomplete."
        )

    if not request.precheck_kpis_available:
        reason_codes.append("PRECHECK_KPIS_MISSING")
        messages.append(
            "Required pre-change KPI evidence is not available."
        )

    if not request.rollback_plan_defined:
        reason_codes.append("ROLLBACK_PLAN_MISSING")
        messages.append(
            "Rollback criteria and plan are not defined."
        )

    if reason_codes:
        return ValidationResult(
            decision="FAIL",
            scenario="CARRIER_CHANGE",
            site_id=request.site_id,
            sector_id=request.sector_id,
            reason_codes=reason_codes,
            messages=messages,
        )

    return ValidationResult(
        decision="PASS",
        scenario="CARRIER_CHANGE",
        site_id=request.site_id,
        sector_id=request.sector_id,
        reason_codes=["VALIDATION_PASSED"],
        messages=[
            "Request is inside the implemented carrier-change "
            "validation boundary."
        ],
    )

@mcp.tool()
def server_status() -> dict[str, str]:
    """Return status and scope of the RFDS validation prototype."""

    return {
        "status": "ok",
        "scope": "bounded RF modification validation prototype",
        "mode": "fail-closed",
    }


@mcp.tool()
def validate_nr_add(request: NRAddRequest) -> ValidationResult:
    """
    Validate a bounded NR carrier-add modification scenario.

    The tool checks duplicate carrier configuration, bounded
    band/bandwidth rules, and availability of pre-change KPI evidence.
    """

    return evaluate_nr_add(request)

@mcp.tool()
def validate_carrier_change(
    request: CarrierChangeRequest,
) -> ValidationResult:
    """
    Validate a bounded LTE/NR carrier ARFCN modification.

    The tool requires spectrum authorization, neighbor-impact review,
    pre-change KPI evidence, and a rollback plan. Simultaneous bandwidth
    changes are rejected as outside the implemented boundary.
    """

    return evaluate_carrier_change(request)

if __name__ == "__main__":
    mcp.run()