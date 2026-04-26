# AGENTS.md

## Cursor Cloud specific instructions

This is a pure-Python scientific data-generation pipeline for Semi-Visible Jet (SVJ) particle physics simulations. There are no external pip dependencies — only Python 3 standard library modules (`math`, `argparse`, `subprocess`, `os`) are used.

### Key scripts

- `svj_helper.py` — Core library + CLI for generating a single Pythia8 datacard. Run with: `python svj_helper.py --mZprime 700 --mDark 20 --rinv 0.7 --alpha peak --directory Test/SVJ -n 10000`
- `generate_datacard.py` — Orchestrator that calls `svj_helper.py` for all SVJ signal hypotheses. Run with: `python generate_datacard.py`
- `launch_slurm_jobs.py` — SLURM job launcher for Delphes simulation (requires HPC cluster, cannot run locally).

### Running the application

```bash
python generate_datacard.py
```

This generates Pythia8 datacards into `Train/` and `Test/` directories (18 test + 2 training SVJ datacards). The generated files are already committed; re-running the command reproduces them identically.

### Gotchas

- The `generate_datacard.py` script calls `python svj_helper.py` via `subprocess.call(cmd, shell=True)`. The `python` command must be available (not just `python3`). If missing, create a symlink: `sudo ln -sf /usr/bin/python3 /usr/bin/python`.
- There are no automated tests, no linter config, and no build step in this repository.
- `launch_slurm_jobs.py` requires a SLURM HPC cluster with Singularity/Apptainer — it cannot be run in the cloud VM.
