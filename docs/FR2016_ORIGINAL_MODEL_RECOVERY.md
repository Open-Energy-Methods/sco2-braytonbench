# Friedman–Rapp (2016) — original EES model recovery

**Status: original EES program and full Table 3 state-point data NOT recovered (2026-11-05).** Searches of the public 2016 symposium archive, public code search and scholarly/software indexes did not identify an author-released `.EES` file or tabulated Figure 4 states. This is a bounded negative search result, not proof that the files do not exist. The user-supplied 21-page paper PDF contains **zero embedded attachments**.

## Original records

- [Friedman & Rapp, 2016, Paper 051](https://www.sco2symposium.com/papers2016/SystemModeling/051paper.pdf)
- [Conference presentation 051pres](https://sco2symposium.com/papers2016/SystemModeling/051pres.pdf)
- [2016 proceedings archive](https://www.sco2symposium.com/papers2016.shtml)

### Published evidence verified

**Paper §III.B, p. 9** describes approximately **400 EES equations**, including a PWR source, secondary CO₂ cycle and tertiary cooler; **30** recuperator segments and **10** IHX segments; iterative property calls and initialization; and an EES thermodynamic property library using an **IIR reference state**. The associated presentation additionally reports **20** precooler sections. The authors compare their EES library against REFPROP 9.1: typical agreement was close, but near-critical discrepancies reportedly approached **1% in enthalpy** and **0.8% in entropy**. Do not interpret the reference-state-dependent absolute enthalpy/entropy values as directly comparable to default CoolProp without matching reference conventions.

**Figure 4, p. 10** includes numbered CO₂ states **1–18**, PWR states **P1–P3**, cooling states **C1/C2**, a **compressor turbine and separate main turbine**, a compressor motor, generator, and flow labels FM1–FM4. In the published parametric studies (§III.B), **FM3=FM4=0**, compressor and main turbine efficiencies both 90%, and paper states that the full model informed realistic piping/thermal-loss parameters. The authors explicitly defer results using *all capabilities* of the Figure 4 model to later work. It is thus important to determine whether Table 3 results came from the detailed 400-equation calculation or from a reduced calculation with inputs derived from it.

**Paper Table 3, p. 14** reports 100.20 MW supplied heat, 38.08 MW turbine work, 13.65 MW compressor work, 75.80 MW cooler rejection with T1=550 K, P1=30 MPa, normalized cycle low T=1.0 and low P=1.13. These aggregate values do not identify individual branch powers, state properties, mass flows, or complete geometry. Existing BraytonBench comparisons must remain labelled **conceptual-cycle, not original EES replication**.

## Additional lead — 2017 Friedman-authored thermodynamics chapter

Peter Friedman also coauthored a chapter with M. Anderson titled [*Thermodynamics*](https://doi.org/10.1016/B978-0-08-100804-1.00003-7) (pp. 41–66) in the 2017 Woodhead Publishing volume *Fundamentals and Applications of Supercritical Carbon Dioxide Based Power Cycles*. Its publisher abstract describes example simple-recuperated and recompression cycle analyses. The accessible abstract **does not establish** that the book reproduces the 2016 Figure 4 EES model, contains its state table, or offers downloadable source. The chapter is a **secondary literature lead**, not a recovered dataset. Ask the corresponding author whether the chapter includes a relevant tabulation or whether the same reference case is discussed in a publicly available appendix.

## Author request — preferred tiers

1. **Best case:** a publication-cleared version of the Table 3 EES calculation, including relevant functions, constants, EES version, property settings, and model mode. No protected, confidential, naval-specific or export-controlled content is requested.
2. **If source unavailable:** an unclassified/cleared export of the Table 3 **state table** with Figure 4 point labels (1–18, and P/C labels only where releasable): P, T, h, s, density and `mdot` with units; separate compressor/main turbine shaft work, compressor motor power, generator/electrical efficiencies, FM1–FM4 flow rates, branch flow splits, and IHX/recuperator/cooler heat duties and UA/effectiveness.
3. **Minimum clarifications:** whether Table 3 represents full Figure 4 or a simplified run; which exact states define `P_low` and `T_low`; Figure 4 compressor-turbine mass/shaft split when bypasses are zero; EES version and IIR property reference configuration; whether associated detailed-paper follow-up/source data may be shared.

Blank `data_requests/fr2016_table3_reference_template.csv` is a **request schema only**, not a fabricated dataset.

## Validation and permissions protocol

If an author responds, record date, provenance, source version and permission to use/publish; quarantine any nonpublic material until permission is clear. Compare reported **specific enthalpy differences and entropy differences** across state transitions under consistent fluid reference conventions; reconstruct the 18-point mass/pressure/energy ledger and branch power accounting; then separately test the existing conceptual 12-state model.

If only numerical state points are obtained, declare a *state-point reproduction* after checking, **not** a source-code-equivalent EES reproduction. If no shareable data are available, keep G2 **source-identifiability blocked**; do not tune arbitrary parameters to match Table 3 efficiency.

**No correspondence sent by this repository change.** The 2016 publication lists two original work addresses for the authors; present deliverability has not been independently verified.
