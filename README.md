# UTP Master Manifest Build

Document Reference: UTP-SPEC-2026-V6.0
Source: `Page_1_____Unified_Triality_Pipeline_Master_Reposi_261002_223529_28_l314.pdf`
("Unified Triality Pipeline Master Repository Manifest", released October 2, 2026)

# Authors - Arthur Leroy Jones
# Author UCT Theory - Michael 
# Independent Researcher - Abby Davis

---

## What this is

A working repository assembled from the code blocks in the Master Repository
Manifest. The manifest describes a `triality_pipeline` package layout
(`src/triality_pipeline/...`) with a central orchestrator (`src/main.py`),
which is a **different layout from the existing Triality-Pipeline- repo**
(flat `src/*.py` + `master_pipeline_*` runners). This build is kept separate
on purpose: it is the manifest's blueprint compiled and validated, not a
replacement for the existing repo.

## Layout

```
├── setup.py
├── requirements.txt
├── deploy.sh                            # Converged venv + dependency deployment script
├── cron_archive.sh                      # Nightly CSV→Parquet→Glacier cron wrapper (see note)
├── adam_core.js                         # Adam optimizer JS engine (complete, validated)
├── adam_dashboard.html                  # Dashboard UI wireframe (loads adam_core.js)
├── .github/workflows/python-ci.yml
├── src/
│   ├── main.py                          # Central execution hub / orchestrator
│   └── triality_pipeline/
│       ├── error_mitigation/
│       │   ├── zne_extrapolation.py     # Zero-Noise Extrapolation (Richardson, r=1/r=3)
│       │   ├── stabilizers.py           # Distance-3 rotated surface-code lattice
│       │   └── decoder.py               # Syndrome decoder loop
│       ├── ml/qcnn_layers.py            # QCNN convolution + pooling filters
│       ├── geometry/grassmannian.py     # Positive Grassmannian / Amplituhedron
│       └── biology/
│           ├── hydration_filters.py     # Neuronal hydration-shell dielectric buffer
│           └── antenna_resonance.py     # DNA fractal antenna resonance
└── tests/
    ├── test_qec.py
    ├── test_biology.py
    └── test_antenna.py
```

## Build repairs (all marked inline in the code)

PDF extraction mangles code (split tokens, lost line breaks), and the manifest
itself left gaps. Every deviation from the source text is tagged:

- **[ADDED]** — `__init__.py` files for the package and all five subpackages.
  The manifest never provided them, but `setup.py` uses
  `find_packages(where="src")` and `src/main.py` imports
  `triality_pipeline.*`, so the package cannot import without them.
- **[ADDED]** — `if __name__ == "__main__":` driver in `src/main.py`. The
  manifest gave the hub no entry point, yet its own CI workflow runs
  `python src/main.py`.
- **[RECONSTRUCTED]** — the tail of `TrialityPipelineOrchestrator.execute_pipeline_cycle`.
  The manifest source truncated mid-dictionary (`"resolved_signal_a...`). The
  return dict was completed from the variables already computed in the method.
- **[RECONSTRUCTED]** — `keep_indices == [0]` / `== [1]` targets in
  `execute_partial_trace_pooling` (qcnn_layers.py). The source lost the
  comparison values; restored from the call site (`keep_indices=[0]`) and the
  trace-axis layout.
- **[RECONSTRUCTED]** — the `-` operator in
  `permittivity_differential = self.bulk_water_dielectric - effective_permittivity`
  (hydration_filters.py). The operator was lost in the source; a difference is
  the only reading consistent with the variable name and formula.
- **[REPAIRED]** — `requirements.txt`: `pytestcov` → `pytest-cov` (not a real
  PyPI package; `pip install` failed on it, and setup.py already spells it
  `pytest-cov`).
- **[REPAIRED]** — `src/main.py` sys.path fix: the manifest appended the repo
  root, under which `triality_pipeline` is not importable in the src layout.
  Now appends `src/` so `python src/main.py` works without an install.
- **[REPAIRED]** — `.github/workflows/python-ci.yml`: the manifest's run
  commands used `src/error_mitigation/...` paths, which don't exist in its own
  layout; corrected to `src/triality_pipeline/...`.

## Validation results

- `py_compile` on all 16 Python files: clean.
- All 7 module `__main__` self-checks: **pass**.
- `python src/main.py` end-to-end sweep: **exit 0**.
  - QEC enabled, 8.5% injected noise → hydration buffer absorbs it to ~0
    residual → mitigated signal 1.00000 → discord **0.74100 bits**, telic
    alignment 95.60%, QCNN pooled trace 1.00000.
  - QEC bypassed → mitigated signal 0.33181 → discord **0.00005 bits**.
- `pytest tests/`: **14 passed, 1 failed**.
  - FAIL: `test_dark_capacity_overflow_logic[0.15-1.0]`. The hydration
    module's shielding (~165 dB/nm attenuation) drives the residual noise to
    ~1e-19 for any input, so `buffered_residual_phase_noise` never exceeds
    the 0.05 overflow threshold and the flag never trips — but the test
    expects overflow at σ=0.15. The module and the test contradict each other
    as written; both kept verbatim. Decide which one should change.

## Known source-level caveats (not repaired — flagged only)

- `decoder.py` is labeled "Minimum Weight Perfect Matching" but implements a
  shared-stabilizer intersection heuristic, not MWPM.
- The 0.74100 / 0.00014 discord constants are the mock-telemetry benchmark
  constants (per v5.2-rev4 §1), used here as hardcoded branch constants.
- The ZNE formula is `E(0) = E(1) + (E(1) − E(3)) / 8` — LJ's `/8` variant from
  his source docs (the three-way formula decision remains open).
- `setup.py` credits only Arthur Leroy Jones (JTechHound) with a placeholder
  email and an MIT-license classifier, but no LICENSE file was in the
  manifest. The author block above follows LJ's standing attribution.
- The manifest's "Fully Operational" checklist claims `CONTRIBUTING.md` is
  deployed; no such file exists in the manifest or here.

## Run it

```bash
pip install -r requirements.txt
pip install -e .
python src/main.py            # full orchestration sweep
pytest -v tests/              # regression suite (see the 1 known failure above)
```

## Deployment script

`deploy.sh` is the **reconciled/converged** version (from the Adam widget
pack, 2026-10-03, §2). It merges the two divergent library sets into one
matrix, regenerates `requirements.txt` from it, and installs everything —
resolving the earlier mismatch between `deploy.sh` and `requirements.txt`
noted below. Verified: `bash -n` clean, full run exits 0, generated
`requirements.txt` matches the repo's.

Notes on the converged version:

- It supersedes the first `deploy.sh` (no more NI-VISA `ldconfig` check, no
  final integrity-check step — the source dropped both).
- `requirements.txt` is now lower-bound-only (the original manifest's
  `<=x.y.z` upper pins are gone) and no longer lists `pytest-cov`.
- One ambiguity: `pytest-cov` was in the manifest's original requirements
  and in `setup.py`'s test extras; the converged matrix omits it. Re-add it
  if you want coverage in CI.

## Adam dashboard widget

`adam_dashboard.html` + `adam_core.js`: the dashboard is now **complete**.
The third payload restructured it into a UI wireframe plus an out-of-band
engine with all closing tags intact. Validated: `node --check` clean, HTML
has no tag errors, every JS element reference resolves, and a 300-step
headless run executes with zero non-finite losses (loss 0.61162 → 0.52500,
damping exactly `exp(−σ/0.053)`). Behavior note: under the mock-gradient
field both parameters settle at the [0, π] lower clamp — that's the toy
landscape's fixed point, functioning as the source specifies.

Repairs from extraction (all marked in the files): restored hyphens in
getElementById targets to match the HTML ids; restored three lost
operators — `theta = theta - (alpha/...)`, `(1.0 - Math.pow(beta2, step))`,
`clientHeight - 40` — each recovered from the parallel line that retained
it (without the first, the line parses as a call to `theta()` and throws on
the first click). Sign convention: this version uses **standard additive**
Adam (`m = βm + (1−β)g`), explicitly marked "FIX ... matching Python rev4
specs" — the earlier minus-sign convention is reversed here, consistent
with the rev4 review.

## Nightly archive wrapper

`cron_archive.sh` (from the "Automated AWS Cloud Upload Cron Wrapper"
component pack, 2026-10-03) gates on `deploy.sh`'s `.venv`, idles cleanly
when `hot_tier/` is empty, and otherwise recompiles CSVs to Parquet and
pushes them to an S3/Glacier bucket. Verified: `bash -n` clean; missing-venv
→ exit 1; empty hot tier → exit 0.

Caveat: its Python steps import `DataManagementPlanArchiveEngine` and
`CloudArchiveStorageManager` from `pipeline_unified` — those classes exist
nowhere in his codebase (checked this repo and the utp-v5 branch). Confirmed
live: the archiving step raises `ModuleNotFoundError`. Those two engines
still need to be written before the cron job does anything beyond idling.

**Update 2026-10-03:** the gap-resolution pack supplied both classes and
they are now appended to the utp-v5 branch's `pipeline_unified.py`
(transcribed verbatim; imports aliased to avoid rebinding module names).
`archive_csv_to_parquet` validated live: CSV → SNAPPY parquet, `#` header
metadata preserved, hot file removed, missing file → `False`; the v5 harness
still exits 0. One design note: `CloudArchiveStorageManager` builds the S3
client eagerly in `__init__`, so a machine with no AWS credentials raises at
construction time instead of failing gracefully at upload — consider lazy
client construction if the cron job must idle cleanly without AWS.

## Roadmap (from the manifest, not yet built)

- `src/geometry/time_crystals.py` — Floquet / time-translation symmetry tracking
- `src/ml/routing_module.py` — multi-terminal geodesic multiplexer
