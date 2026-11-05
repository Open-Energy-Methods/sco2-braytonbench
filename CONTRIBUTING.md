# Contributing

This is research software. Prefer small, reviewable pull requests and preserve provenance for every physical assumption.

- Always distinguish **source-reported**, **derived**, **synthetic fixture**, and **experimentally validated** evidence.
- Add a regression test for every corrected physics or numerical bug.
- Include units, operating domain and the conservation laws for model contributions.
- Do not claim real-CO2, CARBOSOLA, or hardware validation based on analytic-fixture tests.
- Keep substantial dynamic/control additions behind validated steady-state gates.
- When using AI-assisted development, document the verification performed on the resulting code.

Run `python -m pytest -q` before proposing changes.
