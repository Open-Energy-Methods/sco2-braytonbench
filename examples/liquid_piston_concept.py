#!/usr/bin/env python3
"""Generate an illustrative unvalidated liquid-piston PV loop and energy audit."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from dataclasses import fields
from sco2_braytonbench.liquid_piston_concept import LiquidPistonSpec, simulate_liquid_piston


def export(out: Path, spec: LiquidPistonSpec) -> dict:
    cycle = simulate_liquid_piston(spec)
    out.mkdir(parents=True, exist_ok=True)
    trace = out / "illustrative_liquid_piston_pv.csv"
    names = [f.name for f in fields(cycle.points[0])]
    with trace.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=names)
        writer.writeheader()
        for point in cycle.points:
            writer.writerow({f.name: getattr(point, f.name) for f in fields(point)})
    report = cycle.to_json_dict()
    report.pop("points")
    report["trace_csv"] = trace.name
    (out / "illustrative_liquid_piston_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n",
        encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path,
                        default=Path("evidence/generated/liquid_piston_concept"))
    parser.add_argument("--gas-path",
                        choices=["isothermal", "reversible_adiabatic"],
                        default="isothermal")
    args = parser.parse_args()
    report = export(args.out, LiquidPistonSpec(gas_path=args.gas_path))
    for key in ("hydraulic_input_work_j", "hydraulic_recovered_work_j",
                "hysteresis_dissipation_j", "full_cycle_energy_residual_j"):
        print(key+":",report[key])
    print("UNVALIDATED ideal-gas thought experiment, not COMPETENT material evidence")


if __name__ == "__main__":
    main()
