# TES-v0.7 — Frozen synthetic surrogate: executed held-out results

**Evidence cut-off:** 7 November 2026  
**Primary executed source:** [GitHub Actions #42321917693](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42321917693), branch commit `fbfd2ec164dba22dd4cdb6c8934a8a7b54223fc0`.  
**Machine evidence:** [artifact #13553791901](https://github.com/Open-Energy-Methods/sco2-braytonbench/actions/runs/42321917693/artifacts/13553791901) includes frozen hyperparameters, SHA256-bound training/model artifacts, all held-out predictions and structured evaluation report.  
**Source data:** 512 synthetic TES trajectories generated from the v0.6 eight-cell, constant-property, 1-D two-temperature finite-volume bed. Neither physical measurements nor calibrated plant data.  
**Model:** Two HistGradientBoostingRegressor estimators; outlet temperature is predicted in physically normalized coordinates and de-normalized using known initial/hot inlet temperatures; separate model predicts solid SOC.  
**Train/validation-only selection:** Three predeclared candidate settings; lowest validation score selected. The *test* and *OOD* labels were not accessed during fitting or selection.

> **Scientific interpretation:** the ROM is numerically successful as an **in-domain input/output emulator of this eight-cell synthetic bed**. Outside the deliberately shifted flow/temperature envelope, it becomes **less accurate than the simple two-cell physics baseline**. No physical-experiment validation, full cell-state reconstruction, general TES reliability or robust plant control is established.

## 1. Independent split and procedure

| Split | Complete runs | Time records | Access |
|---|---:|---:|---|
| Training | 256 | 4,096 | Fit candidate models |
| Validation | 64 | 1,024 | Rank candidates, freeze configuration |
| Sealed in-domain test | 128 | 2,048 | Open **after** model freeze; no refit |
| Out-of-domain | 64 | 1,024 | Open after freeze; stress test only |

The source v0.6 generator uses deterministic Latin-hypercube seeds and independent full-run IDs, rather than randomly shuffling correlated time rows. Each synthetic trajectory contains eight charging and eight reverse-discharge readings. CSV data and model archives are bound by SHA256 and a versioned schema. Split protection is **procedural**, because the public data files are not encrypted or private.

See [model/selection protocol](08_FROZEN_SPLIT_SURROGATE.md) for input features, transformations, validation objective, library versions and exclusions.

## 2. Validation-only model selection

| Candidate | 64-run validation outlet RMSE (K) | SOC RMSE | Validation selection score |
|---|---:|---:|---:|
| Compact | 5.0444 | 0.01445 | 6.4889 |
| **Balanced (selected)** | **4.2541** | **0.01169** | **5.4229** |
| Smooth | 4.6159 | 0.01354 | 5.9700 |

The declared score is outlet RMSE in K plus 100 times dimensionless SOC RMSE. This rule was selected before test access. The chosen model uses `max_iter=210`, `max_leaf_nodes=31`, `min_samples_leaf=12`, `learning_rate=0.065`, `l2_regularization=0.1` and `random_state=20261107` for each target.

## 3. Frozen in-domain test performance — 128 complete trajectories

| Model | Outlet RMSE (K) | Outlet NRMSE (% of 300 K) | SOC RMSE (fraction) |
|---|---:|---:|---:|
| **Balanced frozen ROM** | **6.1965** | **2.0655** | **0.011619** |
| Two-cell same-physics baseline | 15.0918 | 5.0306 | 0.036980 |
| No-storage persistence | 151.9444 | 50.6481 | 0.509882 |

Additional ROM error details:
- 95th-percentile **complete-run** outlet RMSE: **7.8699 K**.
- 95th-percentile **per-sample** outlet absolute error: **7.9135 K**.
- Median per-sample outlet absolute error: **1.4755 K**.
- Signed mean outlet error: **+0.3433 K**.
- **16 raw normalized bound violations** across the two target channels before explicit clipping to [0,1]. The pipeline records these rather than claiming every raw prediction was physically bounded.

The p95 statistic does not set a maximum error guarantee; rare larger errors can make total RMSE exceed the 95th-percentile magnitude. Each full trajectory is treated as a group, not as 16 independent experiments.

### Predeclared acceptance audit

| Criterion | Outcome |
|---|---|
| Test outlet RMSE ≤ 10 K | **PASS** |
| Test solid SOC RMSE ≤ 0.05 | **PASS** |
| Outlet better than persistence | **PASS** |
| SOC better than persistence | **PASS** |
| Outlet better than two-cell physics | **PASS** |
| SOC better than two-cell physics | **PASS** |

**Six of six passed.** This is an acceptance decision for *synthetic in-domain ROM verification*, not for experimentally measured TES performance.

## 4. OOD negative result — 64 complete trajectories

OOD scenarios intentionally exceed the training envelope, with source inlet temperatures **810–855 K** versus training **500–800 K**, and mass flows **0.105–0.15 kg/s** versus training **0.01–0.10 kg/s**. Other parameters remain within the original synthetic envelope.

| Model | Outlet RMSE (K) | Outlet NRMSE (% of 300 K) | SOC RMSE |
|---|---:|---:|---:|
| Frozen ROM | **14.2522** | 4.7507 | 0.028423 |
| **Two-cell physics** | **6.5965** | **2.1988** | **0.014768** |
| Persistence | 245.9167 | 81.9722 | 0.383050 |

**Critical outcome:** the coarse physically constrained numerical model *outperformed* the learned ROM on these OOD cases by a substantial margin. There were zero raw normalized bound violations in these OOD samples, but boundedness **is not accuracy**.

This is a meaningful negative extrapolation result. Neither increased model complexity nor iterative OOD tuning is justified by it alone: once test/OOD labels are revealed, changing hyperparameters and calling the same cases “sealed” would create leakage. Future OOD work should specify *new* independent run families and a new freeze before proposing an extrapolation-valid model.

## 5. Runtime and replacement limitations

A recorded execution on the GitHub Actions runner measured:
- Full ROM inference over 2,048 test time records: **0.0364 s** (includes Python feature construction).
- Two-cell physical baseline over the same 2,048 test records: **3.697 s**.
- Re-executing the original eight-cell numerical solver on a 12-run, 192-record test subset: **1.323 s**.
- Approximate subset-scaled ROM runtime: **0.00341 s**, giving an illustrative **388×** timing ratio versus eight-cell simulation on that runner.

That last value is a **time-scaling estimate**, not an independently repeated benchmark with matched process startup, file I/O, hardware, batch sizes or energy consumption. The surrogate has no guarantee of operating that fast on a user's computer, nor of replacing the underlying physical conservation calculation.

**Important energy limitation:** The trained ROM produces an *outlet temperature and solid SOC only*. It does not output a full fluid/solid temperature field or a first-law-matched integral of boundary enthalpy. Replacing the conservative TES kernel by this ROM in a coupled Brayton simulation would therefore require an **additional energy-consistent closure**, stability/admissibility analysis and new independent tests. The ROM's output RMSE is not a substitute for a global energy conservation test.

## 6. Exact reproducibility and immutability

Use only the user's own trusted local/CI model artifact: `joblib` deserialization is pickle-based and must not be performed on unknown downloads. The model SHA256 binds its bytes but does not cryptographically attest authorship.

~~~bash
python -m pip install -e '.[test,ml]'

python scripts/tes_generate_synthetic_dataset.py --out evidence/generated/tes_v06

python scripts/tes_surrogate_pipeline.py train \
  --data evidence/generated/tes_v06 \
  --model-dir evidence/generated/tes_v07/frozen

python scripts/tes_surrogate_pipeline.py evaluate \
  --data evidence/generated/tes_v06 \
  --model-dir evidence/generated/tes_v07/frozen \
  --out evidence/generated/tes_v07/evaluation
~~~

The output files are `tes_rom_model.joblib`, `tes_rom_frozen_selection.json`, `tes_rom_holdout_report.json` and `tes_rom_sealed_predictions.csv`. The train and evaluate commands are distinct entry points with a frozen model checksum and source-file hashes. Validation selects the model; the evaluation step **never trains or selects**.

The next research questions are how far such an emulator generalizes to new geometry/material/flow conditions, whether full-state latent ROMs can preserve integral energy, and how to quantify error under real experimental measurement uncertainty. They are **future work**, not hidden completed features.

## 7. Release/governance decision

The observed six in-domain gates support labelling **TES-v0.7 numerical synthetic surrogate** complete **if** the final exact-head CI including new CLI regression is green. The reported OOD failure mode remains an explicit limitation in any public release summary.

The parent package is still **`0.5.0a0`**. This report does not create `1.0.0`, a Zenodo DOI, or any licensed experimental dataset. Separate historic data-rights and qualified independent scientific review gates remain [#27](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/27) and [#28](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/28).

**Do not retrain or adjust candidate settings based on this test report and subsequently claim an untouched test.**
