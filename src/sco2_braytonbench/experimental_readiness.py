"""WP4 prospective measurement readiness and conservative metrology utilities.

This module contains NO CARBOSOLA instrumentation inventory, calibration
certificate, plant measurements or experimental authorization. Its schemas
are deliberately designed to fail closed rather than invent evidence.

Only the *linearized constant-cp sensible heat duty* estimator has
uncertainty propagation. Real CO2 enthalpy uncertainty requires a
separate EOS/covariance and phase-domain treatment.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from math import isfinite, sqrt
from pathlib import Path
from typing import Iterable

from .properties import DomainError


REGISTER_FIELDS = (
    "tag_id", "quantity", "unit", "location", "priority", "availability",
    "measurement_basis", "calibration_status", "time_sync_status", "notes",
)
MATRIX_FIELDS = (
    "case_id", "stage", "load_pattern", "required_tags", "repetition",
    "observable", "acceptance_gate", "approval_status", "data_class", "notes",
)
UNCERTAINTY_FIELDS = (
    "tag_id", "unit", "u_standard", "basis", "reference_id", "status",
)
SAMPLE_FIELDS = (
    "run_id", "time_s", "tag_id", "value", "unit", "quality_flag",
)
APPROVED_UNITS = {
    "s", "K", "Pa", "kg/s", "J/kg", "J/(kg K)", "W", "W/K", "N*m",
    "rad/s", "1", "Hz", "J/K", "m3/s",
}


def _finite(value: float, label: str, *, strictly_positive=False) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value)
            or (value <= 0 if strictly_positive else value < 0)):
        raise DomainError(f"{label} must be finite and "
                          f"{'positive' if strictly_positive else 'nonnegative'}")
    return float(value)


def _read_csv(path: str | Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with Path(path).open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if tuple(reader.fieldnames or ()) != fields:
            raise DomainError(
                f"wrong CSV schema for {path}: expected {','.join(fields)}"
            )
        records = list(reader)
    if not records:
        raise DomainError(f"empty experiment CSV: {path}")
    for index, record in enumerate(records, 2):
        if None in record or any(value is None for value in record.values()):
            raise DomainError(f"malformed CSV fields at line {index}")
    return records


@dataclass(frozen=True)
class MeasurementChannel:
    tag_id: str
    quantity: str
    unit: str
    location: str
    priority: str
    availability: str
    measurement_basis: str
    calibration_status: str
    time_sync_status: str
    notes: str

    def __post_init__(self) -> None:
        if not self.tag_id or not self.quantity or not self.location:
            raise DomainError("sensor tag, quantity and location are required")
        if self.unit not in APPROVED_UNITS:
            raise DomainError(f"unsupported SI unit for {self.tag_id}: {self.unit}")
        if self.priority not in {"required", "recommended", "conditional"}:
            raise DomainError(f"invalid sensor priority {self.tag_id}")
        if self.availability not in {"unconfirmed", "installed", "unavailable"}:
            raise DomainError(f"invalid sensor availability {self.tag_id}")
        if self.measurement_basis not in {
            "direct", "derived", "command", "equipment_metadata"
        }:
            raise DomainError(f"invalid measurement basis {self.tag_id}")
        if self.calibration_status not in {
            "unconfirmed", "current", "expired", "not_applicable"
        }:
            raise DomainError(f"invalid calibration status {self.tag_id}")
        if self.time_sync_status not in {
            "unconfirmed", "verified", "failed", "not_applicable"
        }:
            raise DomainError(f"invalid timing status {self.tag_id}")


def load_sensor_register(path: str | Path) -> dict[str, MeasurementChannel]:
    result: dict[str, MeasurementChannel] = {}
    for row in _read_csv(path, REGISTER_FIELDS):
        channel = MeasurementChannel(**row)
        if channel.tag_id in result:
            raise DomainError(f"duplicate sensor tag {channel.tag_id}")
        result[channel.tag_id] = channel
    return result


def load_test_matrix(
    path: str | Path, register: dict[str, MeasurementChannel]
) -> list[dict[str, str]]:
    rows = _read_csv(path, MATRIX_FIELDS)
    known: set[str] = set()
    for row in rows:
        case_id = row["case_id"]
        if not case_id or case_id in known:
            raise DomainError(f"missing/duplicate case identifier: {case_id}")
        known.add(case_id)
        if row["stage"] not in {"desk", "steady", "dynamic", "validation"}:
            raise DomainError(f"unknown test stage: {case_id}")
        if row["approval_status"] not in {
            "not_requested", "pending", "approved", "rejected"
        }:
            raise DomainError(f"invalid approval status: {case_id}")
        if row["data_class"] != "proposed":
            raise DomainError(
                f"WP4 design matrix is prospective, not measured: {case_id}"
            )
        required = row["required_tags"].split(";")
        if not required or any(not x or x not in register for x in required):
            raise DomainError(f"unknown/missing sensor tag in case {case_id}")
        if len(required) != len(set(required)):
            raise DomainError(f"duplicate sensor requirement in {case_id}")
        if not row["acceptance_gate"] or not row["observable"]:
            raise DomainError(f"missing prospective acceptance gate: {case_id}")
    return rows


@dataclass(frozen=True)
class ChannelUncertainty:
    tag_id: str
    unit: str
    u_standard: float | None
    basis: str
    reference_id: str
    status: str


def load_uncertainty_register(
    path: str | Path, sensors: dict[str, MeasurementChannel]
) -> dict[str, ChannelUncertainty]:
    result: dict[str, ChannelUncertainty] = {}
    for row in _read_csv(path, UNCERTAINTY_FIELDS):
        tag = row["tag_id"]
        if tag not in sensors or tag in result:
            raise DomainError(f"unknown or duplicate uncertainty tag: {tag}")
        if row["unit"] != sensors[tag].unit:
            raise DomainError(f"unit mismatch in uncertainty record {tag}")
        status = row["status"]
        if status not in {"unconfirmed", "confirmed", "not_applicable"}:
            raise DomainError(f"invalid uncertainty status {tag}")
        raw = row["u_standard"].strip()
        if status == "confirmed":
            if not raw or not row["reference_id"].strip():
                raise DomainError(
                    f"confirmed uncertainty requires numerical u and provenance: {tag}"
                )
            try:
                u = float(raw)
            except ValueError as exc:
                raise DomainError(f"invalid uncertainty number {tag}") from exc
            _finite(u, f"u({tag})", strictly_positive=True)
            if row["basis"] not in {"type_A", "type_B", "combined"}:
                raise DomainError(f"uncertainty basis missing: {tag}")
        else:
            if raw:
                raise DomainError(
                    f"unverified uncertainty cannot assert value: {tag}"
                )
            u = None
        result[tag] = ChannelUncertainty(
            tag_id=tag, unit=row["unit"], u_standard=u, basis=row["basis"],
            reference_id=row["reference_id"], status=status
        )
    return result


@dataclass(frozen=True)
class SensibleDutyUncertainty:
    """One-standard-deviation linearized constant-cp source duty estimate."""

    heat_rate_w: float
    combined_standard_uncertainty_w: float
    relative_standard_uncertainty: float | None
    variance_w2: float


def sensible_duty_uncertainty(
    mass_flow_kg_s: float,
    cp_j_kg_k: float,
    inlet_temperature_k: float,
    outlet_temperature_k: float,
    *,
    u_mass_flow_kg_s: float,
    u_cp_j_kg_k: float,
    u_inlet_temperature_k: float,
    u_outlet_temperature_k: float,
    inlet_outlet_temperature_correlation: float = 0.,
) -> SensibleDutyUncertainty:
    """GUM first-order propagation with explicitly correlated temperatures.

    q = m*cp*(Tin-Tout). The stated uncertainties are *standard*
    uncertainties (k=1), not manufacturer maximum errors. Flow and cp
    are assumed mutually independent and independent of temperatures.
    Only the Tin/Tout cross-covariance is modelled. See JCGM 100:2008.

    This is unsuitable for strongly non-linear near-critical CO2 enthalpy
    calculations or unquantified common calibration uncertainty.
    """
    m = _finite(mass_flow_kg_s, "m", strictly_positive=True)
    cp = _finite(cp_j_kg_k, "cp", strictly_positive=True)
    ti = _finite(inlet_temperature_k, "Tin", strictly_positive=True)
    to = _finite(outlet_temperature_k, "Tout", strictly_positive=True)
    um = _finite(u_mass_flow_kg_s, "u(m)")
    ucp = _finite(u_cp_j_kg_k, "u(cp)")
    uti = _finite(u_inlet_temperature_k, "u(Tin)")
    uto = _finite(u_outlet_temperature_k, "u(Tout)")
    rho = inlet_outlet_temperature_correlation
    if (isinstance(rho, bool) or not isinstance(rho, (int, float))
            or not isfinite(rho) or not -1 <= rho <= 1):
        raise DomainError("temperature uncertainty correlation must be [-1,1]")
    dt = ti - to
    q = m * cp * dt
    # Partial derivatives: dq/dm=cp*dT, dq/dcp=m*dT,
    # dq/dTin=m*cp and dq/dTout=-m*cp.
    var = ((cp*dt*um)**2 + (m*dt*ucp)**2
           + (m*cp)**2 * (
               uti**2 + uto**2 - 2*rho*uti*uto
           ))
    if not all(isfinite(x) for x in (q, var)):
        raise DomainError("nonfinite heat duty or uncertainty propagation")
    # Roundoff-safe for perfect common-mode temperature calibration.
    if var < -1e-10*max((m*cp)**2*(uti**2+uto**2), 1.):
        raise DomainError("negative heat-rate variance")
    var = max(var, 0.)
    u = sqrt(var)
    if not isfinite(u):
        raise DomainError("nonfinite heat-rate standard uncertainty")
    return SensibleDutyUncertainty(
        heat_rate_w=q,
        combined_standard_uncertainty_w=u,
        relative_standard_uncertainty=u/abs(q) if q else None,
        variance_w2=var,
    )


@dataclass(frozen=True)
class SensitivityRank:
    rank: int
    parameter_count: int
    experiment_count: int
    full_column_rank: bool


def local_sensitivity_rank(
    rows: Iterable[Iterable[float]], *, relative_pivot_tol: float = 1e-9
) -> SensitivityRank:
    """Column-scaled local Jacobian rank; never claims global identifiability.

    Inputs should be dimensionlessly scaled *by the caller* for observable
    uncertainty/weights and local parameter perturbations. Column norm
    scaling here prevents a simple unit change from altering rank.
    """
    _finite(relative_pivot_tol, "pivot tolerance", strictly_positive=True)
    if relative_pivot_tol >= 0.1:
        raise DomainError("pivot tolerance is too coarse")
    a = [list(row) for row in rows]
    if not a or not a[0]:
        raise DomainError("empty experimental sensitivity matrix")
    n = len(a[0])
    if any(len(row)!=n for row in a):
        raise DomainError("ragged sensitivity matrix")
    if any(not isinstance(x, (float,int)) or isinstance(x,bool)
           or not isfinite(x) for row in a for x in row):
        raise DomainError("nonfinite or nonnumeric sensitivity matrix")
    # Entirely zero columns signal an *unobservable parameter*.
    norms = [sqrt(sum(row[j]**2 for row in a)) for j in range(n)]
    if not all(isfinite(v) for v in norms):
        raise DomainError("unrepresentable sensitivity norms")
    for row in a:
        for j, norm in enumerate(norms):
            row[j] = row[j]/norm if norm else 0.
    pivot_row = 0
    for col in range(n):
        maximum = max(range(pivot_row, len(a)),key=lambda r:abs(a[r][col])) if pivot_row<len(a) else None
        if maximum is None or abs(a[maximum][col]) <= relative_pivot_tol:
            continue
        a[pivot_row], a[maximum] = a[maximum], a[pivot_row]
        pivot = a[pivot_row][col]
        for row_idx in range(pivot_row+1,len(a)):
            factor = a[row_idx][col]/pivot
            for j in range(col,n):
                a[row_idx][j]-=factor*a[pivot_row][j]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return SensitivityRank(
        rank=pivot_row,
        parameter_count=n,
        experiment_count=len(a),
        full_column_rank=pivot_row == n
    )


def validate_long_series(
    path: str | Path,
    register: dict[str, MeasurementChannel],
    *,
    expected_run_id: str,
    max_gap_s: float | None = None,
) -> dict[str, object]:
    """Validate typed long-format samples, not infer sensor calibrations.

    OK means a present finite sample, not a physically valid measurement.
    MISSING is explicit with a blank value; REJECTED is explicitly unusable.
    The flag does not itself certify timestamp alignment or metrology.
    """
    if not expected_run_id:
        raise DomainError("run identifier required")
    if max_gap_s is not None:
        _finite(max_gap_s, "maximum sample gap", strictly_positive=True)
    rows = _read_csv(path, SAMPLE_FIELDS)
    last: dict[str, float] = {}
    counts = {"OK":0, "MISSING":0, "REJECTED":0}
    gaps: list[str] = []
    seen: set[tuple[str, float]] = set()
    for idx, row in enumerate(rows, 2):
        if row["run_id"] != expected_run_id:
            raise DomainError(f"wrong run ID at row {idx}")
        tag=row["tag_id"]
        if tag not in register:
            raise DomainError(f"unknown sensor {tag} at row {idx}")
        if row["unit"] != register[tag].unit:
            raise DomainError(f"unit mismatch for {tag} at row {idx}")
        try:
            t = float(row["time_s"])
        except ValueError as exc:
            raise DomainError(f"invalid sample timestamp row {idx}") from exc
        _finite(t, "sample timestamp")
        key=(tag,t)
        if key in seen:
            raise DomainError(f"duplicate timestamp for {tag}: {t}")
        seen.add(key)
        if tag in last and t<=last[tag]:
            raise DomainError(f"out-of-order samples for {tag}")
        if (max_gap_s is not None and tag in last
                and t-last[tag]>max_gap_s):
            gaps.append(tag)
        last[tag]=t
        flag=row["quality_flag"]
        if flag not in counts:
            raise DomainError(f"unknown sample quality flag at row {idx}")
        value=row["value"].strip()
        if flag=="MISSING":
            if value:
                raise DomainError(f"missing value must be blank row {idx}")
        elif not value:
            raise DomainError(f"numeric sample required row {idx}")
        else:
            try:
                sample=float(value)
            except ValueError as exc:
                raise DomainError(f"nonnumeric sensor sample row {idx}") from exc
            if not isfinite(sample):
                raise DomainError(f"nonfinite sensor sample row {idx}")
            if flag=="OK" and register[tag].unit=="K" and sample<=0:
                raise DomainError(f"nonphysical Kelvin sample row {idx}")
        counts[flag] += 1
    return {
        "run_id":expected_run_id,"sample_rows":len(rows),
        "channels_seen":len(last),
        "quality_counts":counts,
        "max_gap_violations":sorted(set(gaps)),
        "evidence_class":"input_format_QC_only_NOT_calibration_or_validation",
    }


def experimental_readiness_gate(
    required_tags: Iterable[str],
    sensors: dict[str, MeasurementChannel],
    uncertainties: dict[str, ChannelUncertainty],
    *,
    approved_run_authorization: bool = False,
    verified_data_provenance: bool = False,
) -> dict[str, object]:
    """A strict checklist, not legal/safety approval or test-rig authorization."""
    blockers: list[str] = []
    if not approved_run_authorization:
        blockers.append("formal facility run authorization not verified")
    if not verified_data_provenance:
        blockers.append("measured data provenance not independently verified")
    for tag in required_tags:
        if tag not in sensors:
            blockers.append(f"{tag}: absent from sensor register")
            continue
        channel=sensors[tag]
        if channel.availability!="installed":
            blockers.append(f"{tag}: availability not verified installed")
        if channel.measurement_basis=="direct" and channel.calibration_status!="current":
            blockers.append(f"{tag}: current calibration not verified")
        if channel.time_sync_status not in {"verified","not_applicable"}:
            blockers.append(f"{tag}: time synchronization not verified")
        u=uncertainties.get(tag)
        if (u is None or (
            channel.measurement_basis=="direct"
            and (u.status!="confirmed" or u.u_standard is None))):
            blockers.append(f"{tag}: standard uncertainty not confirmed")
    return {
        "ready_for_measured_validation":not bool(blockers),
        "blockers":blockers,
        "required_tag_count":len(set(required_tags)),
    }
