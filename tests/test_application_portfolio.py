"""Portfolio evidence integrity — no fabricated experiments or hidden OOD failure."""
from __future__ import annotations

import csv
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / "docs/portfolio"
EV = PORT / "evidence"


def table(name):
    with (EV/name).open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def test_schumann_source_numbers_and_order():
    rows = table("schumann_grid_20261108.csv")
    assert [int(r["n_cells"]) for r in rows] == [16, 32, 64, 128]
    fluid = [float(r["outlet_abs_error_k"]) for r in rows]
    solid = [float(r["mid_solid_abs_error_k"]) for r in rows]
    assert all(math.isfinite(x) and x > 0 for x in fluid+solid)
    assert all(a > b for a,b in zip(fluid, fluid[1:]))
    assert all(a > b for a,b in zip(solid, solid[1:]))
    assert fluid[-1] == pytest.approx(0.3358202296988111, rel=1e-12)
    assert solid[-1] == pytest.approx(0.5594674789288661, rel=1e-12)


def test_charge_hold_reverse_trace_incomplete_cycle_and_stage_boundaries():
    rows = table("tes_stage_trace_20261108.csv")
    assert len(rows) == 28
    assert [r["mode"] for r in rows] == ["charge"]*10+["hold"]*2+["discharge"]*16
    assert [float(r["t_end_s"]) for r in rows] == list(range(5, 145, 5))
    assert all(0 <= float(r["solid_soc"]) <= 1 for r in rows)
    assert float(rows[-1]["solid_soc"]) == pytest.approx(0.06331736876390663)
    assert float(rows[11]["t_end_s"]) == 60
    assert float(rows[12]["outlet_k"]) > float(rows[11]["outlet_k"])
    prov=(PORT/"EVIDENCE_AND_FIGURE_SOURCES.md").read_text(encoding="utf-8")
    assert "gross efficiency NULL" in prov and "48.060797" in prov


def test_frozen_test_versus_ood_negative_transfer_is_preserved():
    rows = table("tes_frozen_holdout_20261108.csv")
    assert len(rows) == 4
    cases={(r["partition"],r["model"]):r for r in rows}
    assert set(cases)=={
        ("test","frozen_rom"),("test","two_cell_physics"),
        ("ood","frozen_rom"),("ood","two_cell_physics"),
    }
    def rmse(partition, model):
        return float(cases[partition,model]["outlet_rmse_k"])
    assert rmse("test","frozen_rom") == pytest.approx(6.196479021588927)
    assert rmse("ood","frozen_rom") == pytest.approx(14.252178762928107)
    assert rmse("test","frozen_rom") < rmse("test","two_cell_physics")
    assert rmse("ood","frozen_rom") > rmse("ood","two_cell_physics")
    assert all(int(r["complete_runs"]) == (128 if r["partition"]=="test" else 64)
               for r in rows)
    for r in rows:
        assert math.isfinite(float(r["outlet_rmse_k"]))
        assert 0 < float(r["soc_rmse_fraction"]) < 1


@pytest.mark.parametrize("name",[
    "01_schumann_grid_convergence.svg",
    "02_tes_charge_hold_discharge.svg",
    "03_frozen_rom_test_ood.svg",
])
def test_public_svg_is_accessible_and_self_contained(name):
    fp=PORT/"figures"/name
    root=ET.parse(fp).getroot()
    assert root.tag.endswith("svg")
    assert root.attrib.get("viewBox") == "0 0 1100 610"
    assert root.attrib.get("role") == "img"
    assert root.attrib.get("aria-label")
    child_tags={c.tag.split("}")[-1] for c in root}
    assert "title" in child_tags and "desc" in child_tags
    src=fp.read_text(encoding="utf-8")
    assert '<image' not in src and 'href="http' not in src and "<script" not in src
    assert "<polyline" in src or "<rect" in src
    assert "not experimental" in src.lower() or "not laboratory" in src.lower()


def test_application_readme_links_all_research_items_and_limits():
    readme=(PORT/"README.md").read_text(encoding="utf-8")
    for piece in (
        "figures/01_schumann_grid_convergence.svg",
        "figures/02_tes_charge_hold_discharge.svg",
        "figures/03_frozen_rom_test_ood.svg",
        "PROSPECTIVE_EXPERIMENTAL_VALIDATION_PROTOCOL.md",
        "LIQUID_PISTON_CONCEPT.md",
        "14.2522 K", "6.5965 K", "undefined", "NOT",
    ):
        assert piece.lower() in readme.lower(), piece
    top=(ROOT/"README.md").read_text(encoding="utf-8")
    assert "docs/portfolio/README.md" in top


def test_protocol_files_not_misrepresented_as_actual_experiments():
    chan=ROOT/"protocols/tes_prospective/measurement_channels.csv"
    runs=ROOT/"protocols/tes_prospective/run_matrix.csv"
    with chan.open(newline="",encoding="utf-8") as fp:
        sensors=list(csv.DictReader(fp))
    with runs.open(newline="",encoding="utf-8") as fp:
        proposed=list(csv.DictReader(fp))
    assert len(sensors) >= 16
    ids=[s["channel_id"] for s in sensors]
    assert len(ids)==len(set(ids))
    axial=[s for s in sensors if s["channel_id"].startswith("T-AX")]
    assert len(axial)==10
    assert all(s["phase_or_contact"]=="UNRESOLVED" for s in axial)
    assert {s["status"] for s in sensors} <= {"PROPOSED","OPTIONAL_PROPOSED"}
    assert len(proposed) >= 10
    assert all(r["execution_status"]=="NOT_EXECUTED" and
               r["hardware_limits_verified"]=="NO" for r in proposed)
    assert any(r["partition"]=="validation" for r in proposed)
    assert any(r["partition"]=="conditional_ood" for r in proposed)
    protocol=(PORT/"PROSPECTIVE_EXPERIMENTAL_VALIDATION_PROTOCOL.md").read_text("utf-8")
    assert "NOT" in protocol and "uncertainty" in protocol.lower()
    assert "J Σ Jᵀ" in protocol or "covariance" in protocol.lower()
