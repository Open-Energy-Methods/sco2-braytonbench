# TES-v0.7 — leakage-controlled synthetic reduced-order surrogate

**Scientific status:** this module learns the behaviour of the repository's
synthetic **eight-cell, constant-property, 1-D two-temperature sensible packed-bed solver**. It does **not** infer experimental data, validate a TES installation, simulate liquid-piston mechanics, represent CARBOSOLA/CIC energiGUNE, or predict full dynamic CO₂ pressure/rotor inventories.

**Dependency isolation:** install the optional `ml` extra (NumPy, scikit-learn, joblib); ordinary thermodynamics and TES solvers remain independent of machine-learning dependencies.

## 1. Dataset and holdout governance

The deterministic v0.6 generator provides exactly **512 independent full schedules** with eight charge and eight reverse-flow discharge readouts per schedule:

| Partition | Complete runs | Records | Used for |
|---|---:|---:|---|
| Train | 256 | 4096 | Fit surrogate coefficients/trees |
| Validation | 64 | 1024 | Choose hyperparameters, no test feedback |
| Test | 128 | 2048 | **One-time, frozen model selection** in-domain evaluation |
| OOD | 64 | 1024 | Extrapolation diagnostic only, never selection |

The test/OOD CSVs are **not opened during training**; the pre-existing generator manifest's SHA256 fields may be copied, which does not disclose target labels. Training is a separate process from evaluation. The training stage writes a model checksum and a **frozen hyperparameter-selection JSON** before the evaluation command is invoked. The evaluation stage refuses to run if source data or model bytes differ.

The CSVs are public scientific artifacts, so "sealed" is procedural, not a cryptographic secret. Whole trajectories, not individual correlated time rows, define the partitions.

## 2. Model and physically scaled features

Two deterministic `HistGradientBoostingRegressor` models predict:

\[
\theta_\mathrm{out}=\frac{T_\mathrm{out}-T_\mathrm{initial}}
 {T_\mathrm{hot,inlet}-T_\mathrm{initial}},\quad
SOC_s=\frac{\sum_iC_{s,i}(T_{s,i}-T_\mathrm{initial})}
 {\sum_iC_{s,i}(T_\mathrm{hot,inlet}-T_\mathrm{initial})}.
\]

The parameters supplied *before solving* a complete prescribed run are mode, phase fraction, charge/discharge turnover duration, flow and interphase conductance. An adimensional source–bed NTU and time-normalized interactions are formed from the **declared fixed 1-m length, 0.1-m² bulk area and 1000-J/(kg K) fluid cp**. No true outlet, solid SOC, boundary energy or first-law residual is included in any feature. The full **future schedule** is specified in the input, making this an offline schedule predictor, **not** a causal adaptive controller.

For constant properties and a fixed geometry, scaling by the known initial-to-hot span is physically justified by the linear temperature equations. This does not validate temperature dependence at actual high-temperature conditions.

The selected model is from **three declared candidates** (compact, balanced, smooth), chosen on validation using:

\[
S_\mathrm{val}=RMSE(T_\mathrm{out},K)+100\ RMSE(SOC_s).
\]

The first term is in K, the second has a declared 100 K scale. This is a model-selection convention, not an objective based on measured plant costs. No further hyperparameter or feature change should be made after the holdout test results are revealed without explicitly retiring the previous holdout and declaring a new one.

## 3. Baselines, final evidence and audit

The frozen model is compared **at exactly the same test run IDs** against:

1. **No-storage persistence:** outlet remains at initial bed temperature, solid SOC remains zero. Weak but transparent.
2. **Coarse two-cell physics:** the same physically conservative solver with N=2; the target is the N=8 generated result. This tests whether the learned reduced model is more useful than simply coarsening the numerical mesh.

Report **physical** outlet RMSE in K, normalized RMSE as percent of the declared 300 K design span, solid SOC RMSE, 95th-percentile complete-run outlet RMSE, percentile of per-sample absolute error, median error, signed bias and raw normalized bound violations. Prediction postprocessing explicitly clips to [0,1] and counts each **pre-clipping** violation. A clipped model is not automatically admissible beyond the source PDE's range.

Predeclared in-domain acceptance thresholds (see tracked [issue #36](https://github.com/Open-Energy-Methods/sco2-braytonbench/issues/36)):

- Outlet RMSE ≤ **10 K**.
- Solid SOC RMSE ≤ **0.05** (absolute fraction).
- Both metrics better than both persistence and the two-cell physics baseline.

Every criterion is reported separately as pass/fail, even if the model fails. **OOD performance has no acceptance threshold** and is separately reported as an extrapolation stress test, not a validation.

The evaluation reports wall-clock training/inference/two-cell times and a small N=8 reference-run timing sample. These times are **environment dependent** and are not evidence of universal hardware speedup.

## 4. Build, train, freeze, evaluate and reproduce

From the exact commit containing TES-v0.6 and TES-v0.7:

~~~bash
python -m pip install -e '.[test,ml]'
python -m pytest -q tests/test_tes_dataset.py tests/test_tes_surrogate.py

python scripts/tes_generate_synthetic_dataset.py \
    --out evidence/generated/tes_v06

python scripts/tes_surrogate_pipeline.py train \
    --data evidence/generated/tes_v06 \
    --model-dir evidence/generated/tes_v07/frozen

# This is an independently launched stage. It cannot retrain or
# change the model selected on validation.
python scripts/tes_surrogate_pipeline.py evaluate \
    --data evidence/generated/tes_v06 \
    --model-dir evidence/generated/tes_v07/frozen \
    --out evidence/generated/tes_v07/evaluation
~~~

Files produced:

- `tes_rom_model.joblib` — trusted-model artifact, two regressors.
- `tes_rom_frozen_selection.json` — candidate validation results, selected hyperparameters, exact data/file hashes, model checksum and untouched-test declaration.
- `tes_rom_sealed_predictions.csv` — **both** independent holdouts with true/surrogate/coarse-temperature and SOC results, exact split/run identifiers.
- `tes_rom_holdout_report.json` — all numerical errors, OOD diagnostics, physical flags, timings and predeclared success/failure booleans.

**Security:** `joblib` uses Python pickle. Never load a model file from an untrusted third party. The SHA256 in this repo detects accidental alteration; it is **not** an external signature or proof of publication authorization.

## 5. Scope and scientific risks

- The surrogate imitates a solver with **N=8**, not the N=128 grid-converged Schumann study or an actual experimental packed bed.
- There is no input-dependent flow pressure loss, PCM enthalpy curve, thermal leakage, wall stresses or changing fluid cp; the training data have no direct measurement uncertainty.
- A reduced model can have lower RMSE than N=2 without preserving the PDE's detailed local/global energy-balance identity. This surrogate predicts only outlet T and bulk solid SOC, **not** the full cell states or boundary heat. It must not replace the conservative solver inside a closed energy-ledger control loop without additional constraint checks.
- The OOD branch intentionally changes flow and inlet temperature beyond the training envelope, but its actual dimensionless NTU may still overlap the training range; passing that particular OOD set is not a universal extrapolation guarantee.
- If the test thresholds fail, preserve the result as a negative outcome. Do not relabel a sealed test as validation to justify iterative retuning.

**Release status:** This is an internal TES-v0.7 **research milestone**, not a claim that the parent package version is 1.0.0 or that scientific independent review/data-rights gates are cleared.
