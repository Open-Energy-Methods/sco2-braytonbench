# TES-v1.0 — Release decision register and no-go controls

**Current decision: NOT AUTHORIZED FOR FORMAL v1.0 RELEASE.**
This register is a public audit checklist, not a certificate of rights, independent peer review or approval to tag. The integrated baseline remains parent software v0.5.0a0. The repository development branch may carry the candidate's research report and expanded tests without declaring a public release.

## A. Decision records

| Gate | Evidence or completion needed | Current status |
|---|---|---|
| G01. TES kernel + Schumann mathematical verification | Independent analytic fixture, signed mass/thermal ledger, spatial and temporal refinement | IMPLEMENTED; automation recorded, no human sign-off |
| G02. Multistage and one-pass coupling | Actual fluid+solid state returns, dimensional J/W separation, ideal and pinned CO₂ smoke | IMPLEMENTED; software checks not physical validation |
| G03. Frozen synthetic surrogate | 512-run split integrity, selected-only validation, recorded test and negative OOD, output-only bounds | IMPLEMENTED; negative OOD and 16 raw bound violations disclosed |
| G04. TES-v0.8 physical/numerical sensitivity | N=96/192 quality-service comparison, separate OAT, factorial, grade and model limitations | IMPLEMENTED; model-form uncertainty not quantified |
| G05. TES-v0.9 distribution and evidence | 3.10/3.11/3.12 isolated wheel/sdist replay, archive rights exclusions, source/evidence hashes | IMPLEMENTED at merged TES-v0.9 SHA 46db32e6e9a45bdfeb645aa6e0599380cb9bc9e4; recheck release head |
| G06. TES-v1.0 consolidated research report | Integrated equations, source-differentiated metrics, confidence limits, negative results | DRAFTED FOR EXTERNAL REVIEW, not independent approval |
| G07. Supplementary model-invariance/failure-injection tests | Independent affine/geometric scaling, exergy, grade and tamper checks | CANDIDATE CODE; requires exact-head CI |
| G08. Data redistribution and history review | Rights-steward decision on publisher-derived original/normalized data, historical public Git | **BLOCKED — #27 OPEN** |
| G09. Qualified independent reviewers | Actual named independent thermodynamics and scientific-software reviewer identity, dated report, exact SHA and disposition | **BLOCKED — #28 OPEN** |
| G10. Exact-final-source head verification | All CI jobs and fresh distribution artifacts pass on intended source | **PENDING RELEASE-CANDIDATE FREEZE** |
| G11. Explicit parent release approval | Maintainer/steward authorizes tag/version change and checks final review/rights | **NOT GRANTED** |
| G12. DOI/archiving | Only after agreed v1.0 tag/version/review, appropriate deposit scope/license | **NOT CREATED** |

## B. Minimum formal release package

A candidate that *might* later be considered for formal software v1.0 consists of:

1. Exact Git commit of scientific source and auditable changelog/README/CITATION metadata.
2. Entire docs/tes/01–15 sequence, with the consolidated report and independent human reviewer outcome.
3. Candidate source-file SHA256 ledger and both wheel/sdist source archive checksums, without uncleared NIST-derived CSV or restricted third-party media.
4. Reproducible TES-v0.3 Schumann/grid, v0.6 independent trajectory partitions, v0.7 frozen in-domain/OOD, v0.8 grade/uncertainty and v0.9 clean-install replay evidence from an appropriate exact source commit.
5. Legally and scientifically reviewed data-provenance decisions, each tied to precise reuse scope and version.
6. External reviewer(s) actual signed findings and maintainer's documented release decision.

This package is a pre-release set of requirements, **not evidence that they have already been satisfied**.

## C. Classification policy

**Acceptable until independent approval:** "Synthetic 1-D two-temperature TES model with mathematically checked conservation, analytic Schumann inlet-step comparison, reproducible storage cycles, open-stream Brayton interface, leakage-controlled 512-run synthetic surrogate with negative OOD comparison and deterministic sensitivity studies."

**Not acceptable:** "CIC energiGUNE/CARBOSOLA/HZDR experimentally validated TES", "pressure/mass dynamic CO₂ digital twin", "validated TES power-dispatch controller", "generalizable OOD conservative ROM", "measured 0.31% industrial TES efficiency", "the NIST ThermoML 49-point extracted table is freely redistributable under BSD", "independently peer-reviewed by researchers", "v1.0 DOI issued".

If there is conflicting software evidence, negative out-of-domain findings, changed equations or moved source SHA, use **CHANGES REQUIRED / HOLD**, not automatic approval. Fail closed on file/hash, rights or human-review mismatches.

## D. Next real human actions

- Obtain independent rights review of historic Mantilla ThermoML extraction/redistribution (issue #27), including public Git history exposure, not just wheel/sdist contents.
- Send the reviewer packet (docs/tes/14_EXTERNAL_REVIEW_PACKET.md) to actual qualified independent thermo/numerical and scientific-software reviewers (issue #28); record dates and verified identities only after genuine participation.
- Resolve reviewer findings, regenerate the candidate ledger on exact final commit and recheck post-merge main actions.
- Only then decide if a formal parent software release is desirable; changing 0.5.0a0, creating v1.0 tags or depositing Zenodo is a separate explicit maintainer action.

**Verifiable current status:** Candidate engineering/self-audit can be integrated as an alpha milestone after CI; release promotion remains BLOCKED.
