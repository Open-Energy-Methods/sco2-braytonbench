"""Kim 2019 original-source registry verification (not model validation)."""
import json
import math
from pathlib import Path
import pytest

DOC=Path(__file__).resolve().parents[1]/"data"/"reference"/"kim2019_coefficients.json"
D=json.loads(DOC.read_text(encoding="utf-8"))

def test_source_sha_and_nonredistribution():
    assert D["source"]["original_pdf_sha256"]=="8407a94d23a048cc8e3c1889296108b4da0d812bba6cd8ec91a13a3babb47651"
    assert "NOT rehosted" in D["source"]["copyright_notice"]

def test_empirical_table4_source_coefficients_are_complete():
    m=D["coefficients"]["empirical"]
    assert m["top"]["c1"]==pytest.approx(1.14)
    assert m["top"]["n"]==pytest.approx([-.50,-.36,.54,.83,-3.48e-14,.52])
    assert m["top"]["c2"]==pytest.approx(7.05)
    assert m["top"]["m"]==pytest.approx([-.30,-.55,-14.64,3.52e-6,-8.23e-11,-5.35])
    assert m["bottom"]["c1"]==pytest.approx(.11)
    assert m["bottom"]["n"]==pytest.approx([-.15,-.41,.26,.54,-4.12e-4,.63])
    assert m["bottom"]["c2"]==pytest.approx(19.)
    assert m["bottom"]["m"]==pytest.approx([-.33,-.14,-.40,3.98e-6,-3.55e-5,-.88])

def test_semi_empirical_table4_and_source_context():
    m=D["coefficients"]["semi_empirical"]
    assert m["top"]["c1"]==pytest.approx(2.56)
    assert m["bottom"]["c1"]==pytest.approx(4.06e-4)
    assert m["top"]["c2"]==pytest.approx(9.89e2)
    assert m["bottom"]["c2"]==pytest.approx(2.08)
    assert m["top"]["n"]==pytest.approx([13/24,1/3,1/3,1/3,-2/3,1])
    assert m["top"]["m"]==pytest.approx([-.25,-.15,-.5,.35,-.15,-.6])
    e=D["source_experimental_envelope"]
    assert e["postech"]["tube_inner_diameter_m"]==pytest.approx(.00775)
    assert e["validation"]["points_total"]==e["validation"]["postech_points"]+e["validation"]["Adebiyi_Hall_points"]==620
    assert e["validation"]["excluded_x_over_d_below"]==10

def test_original_table6_is_not_a_stuttgart_result():
    e=D["original_paper_error_percent"]
    assert [e["empirical"][x] for x in ("top","bottom")]==[10.0,10.44]
    assert e["Lei_on_original_data"]["top"]==pytest.approx(381.45)
    assert "Stuttgart" in " ".join(D["explicit_limits"])

def test_model_forms_preserve_reciprocal_and_quadrature():
    assert D["model_forms"]["inverse_Nu_nc"].startswith("c2 *")
    assert D["model_forms"]["Nu_mixed"]=="sqrt(Nu_fc**2 + Nu_nc**2)"
    for mode in ("empirical","semi_empirical"):
        for orientation in ("top","bottom"):
            x=D["coefficients"][mode][orientation]
            assert len(x["n"])==len(x["m"])==6
            assert math.isfinite(x["c1"]) and math.isfinite(x["c2"])
