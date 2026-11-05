# Integration audit — sequential research PR chain

**Date:** 2026-11-05. **Base:** `main` SHA `32ec24cfed47d7822a5665031a0c67ff1693f825`. **Latest stacked research head:** `38842a0489435df7b3df3724d4b562e77c9d142c`. The research head is **38 commits ahead, 0 behind**, spanning **96 files**, **11,221 added / 20 removed lines**. No unrelated `main` commits need conflict reconciliation.

| Order | Draft PR | Contribution | Successful CI run |
|---|---:|---|---:|
| 1 | [#1](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/1) | Reconstructed foundation, property and source identifiability | [41995718964](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/41995718964) |
| 2 | [#6](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/6) | G3 finite WHR source | [42000144494](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42000144494) |
| 3 | [#8](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/8) | G3.1 installed-UA heater | [42003355229](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42003355229) |
| 4 | [#9](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/9) | G3.2 dual heater/cooler UA | [42007026597](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42007026597) |
| 5 | [#10](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/10) | G3.3 reference streams/hydraulics | [42011217580](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42011217580) |
| 6 | [#12](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/12) | G3.4 source QA and input provenance | [42018591734](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42018591734) |
| 7 | [#13](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/13) | G3.5 H1a Stuttgart data and baselines | [42032549353](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42032549353) |
| 8 | [#15](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/15) | G3.5 H1b Bishop/Jackson | [42036923202](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42036923202) |
| 9 | [#16](https://github.com/Open-Energy-Methods/sco2-braytonbench/pull/16) | G3.5 H1c Lei transfer negative result | [42041906147](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42041906147) |

**All nine** source PR heads had green GitHub Actions results and `mergeable=true` at this audit. All were **draft, open, not merged** before consolidation. Some research benchmarks are **negative or partial science findings**; **CI success does not validate industrial physics**.

## Consolidation technique

A dedicated integration branch contains the **existing linear chain of 38 commits** plus source recovery audit; the integration PR targets `main` and should use a **merge commit**, rather than flattening all independent scientific stages into an opaque squash. Do not merge each child's PR into its temporary base: it creates needless divergent merge commits. Once this integrated PR is merged and green on `main`, original stacked draft PRs can be closed **as superseded** with links to the integration merge (not misreported as independently merged).

Before merging check:
- unchanged project research gate disclaimers in README, all model comparisons marked benchmark-specific and not CARBOSOLA validation;
- reproducible full CI, including optional real-CO₂ and numerical mesh/stuttgart suites;
- original Stuttgart CC BY 4.0 attribution intact and nonredistribution of uploaded copyrighted Kim PDF;
- no experimental anomaly STU-001 silently modified;
- no author-sourced Kim 2019 error numbers mislabelled achieved Stuttgart results;
- research schema/correlation coefficients tested and auditable.

**Release remains 0.5.0-alpha/research and NOT certified as an industrial model.** The integration into main is not a Zenodo/DOI release, plant calibration or journal publication.
