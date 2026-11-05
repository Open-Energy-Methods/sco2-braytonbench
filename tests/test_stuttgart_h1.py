"""Offline analytic verification of H1 pipeline; no CoolProp required here."""
from pathlib import Path
import csv
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from stuttgart_h1 import (SOURCE_ANOMALY,nominal_family,holdout_families,
                          gnielinski_smooth,dittus_boelter_heating,evaluate)

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"validation"/"stuttgart"


def artificial_props(key, *args):
    """Analytical cp=1000 J/kg/K, mu=1e-4 Pa.s, k=0.1 W/m/K mock.

    It deliberately DOES NOT reproduce CO2 or any laboratory observation.
    """
    if args[-1] != 'HEOS::CO2':
        raise ValueError('not the declared test fixture fluid')
    if key == 'Hmass':
        return 1000.*args[3]
    if key == 'T':
        return args[3]/1000.
    if key == 'Cpmass':
        return 1000.
    if key == 'VISCOSITY':
        return 1.e-4
    if key == 'CONDUCTIVITY':
        return 0.1
    raise ValueError(key)


def test_analytic_nusselt_pr1_smooth():
    import math
    re=1e5
    f=(0.79*math.log(re)-1.64)**-2
    # When Pr=1, Gnielinski denominator is exactly 1.
    assert gnielinski_smooth(re,1.,100)==pytest.approx((f/8)*(re-1000))
    assert dittus_boelter_heating(re,1.,100)==pytest.approx(.023*re**.8)

@pytest.mark.parametrize('re,pr,xd',[(1500,1,100),(5000,2500,100),(5000,1,5)])
def test_gnielinski_hard_domain_gates(re,pr,xd):
    with pytest.raises(ValueError):
        gnielinski_smooth(re,pr,xd)


def test_nominal_family_split_never_leaks_orientations():
    ids=[r['experiment_id'] for r in csv.DictReader(open(DATA/'experiment_index.csv'))]
    held=holdout_families(ids)
    assert len(held)==4
    for id in ids:
        fam=nominal_family(id)
        for o in ('HB','HM','HT'):
            assert (nominal_family(id.replace('_'+id.split('_')[1]+'_','_'+o+'_')) in held)==(fam in held)


def test_full_intake_quarantine_and_report(tmp_path):
    result=evaluate(DATA/'experiment_index.csv',
                    DATA/'axial_profiles.csv', artificial_props,tmp_path)
    counts=result['input_counts']
    assert counts['experiments']==54
    assert counts['axial_records']==2508
    assert counts['reported_local_htc']==2398
    assert counts['quarantined_experiments']==1
    assert counts['quarantined_htc_records']==50
    assert counts['retained_observed_htc']==2348
    assert any(item['experiment_id']==SOURCE_ANOMALY for item in result['exceptions'])
    rows=list(csv.DictReader(open(tmp_path/'local_predictions.csv')))
    assert rows
    assert not any(row['experiment_id']==SOURCE_ANOMALY for row in rows)
    assert {row['model'] for row in rows}=={'gnielinski_smooth_bulk','dittus_boelter_heating_bulk'}
    assert all(float(row['predicted_htc_w_m2_k'])>0 for row in rows)
    assert all(row['reported_htc_sigma_pct'] for row in rows)
    assert result['models']['gnielinski_smooth_bulk']['split']['held_out']['n']>0
    assert len(result['split']['held_out_families'])==4


def test_full_intake_is_mathematically_deterministic(tmp_path):
    a=evaluate(DATA/'experiment_index.csv',
               DATA/'axial_profiles.csv',artificial_props,tmp_path/'a')
    b=evaluate(DATA/'experiment_index.csv',
               DATA/'axial_profiles.csv',artificial_props,tmp_path/'b')
    assert a['models']==b['models']
    assert a['split']==b['split']
