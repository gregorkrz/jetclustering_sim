# JetClustering_sim

Simulation of datasets accompanying the [IRC-Safe Jet Clustering With Transformers](https://github.com/gregorkrz/jetclustering) repository.


## Generating the SVJ data cards

```python generate_datacard.py```

The cards will be placed in Train and Test directories. Only two signal hypotheses are used for training.

## Generating SLURM job files and submitting the jobs

Use `launch_slurm_jobs.py` to generate and submit DelphesPythia8 jobs from Pythia
datacards. Each run processes one datacard and produces one ROOT output file.

### CLI

```bash
python3 launch_slurm_jobs.py \
  --input <path_to_datacards> \
  --output <path_to_output_root_files> \
  --detector CMS \
  --num-runs 50
```

### Main options

- `--detector {CMS,ATLAS}`: choose Delphes detector card
  - `CMS` -> `delphes_card_CMS_pileup_HV.tcl`
  - `ATLAS` -> `delphes_card_ATLAS_pileup_HV.tcl`
- `--num-runs N`: launch N independent runs per datacard
  - each run now receives a distinct `Random:seed`, so outputs are statistically
    independent rather than repeated event sequences
- `--no-submit` (`-ns`): dry-run mode (generate SLURM scripts without `sbatch`)

### Recommended usage for cross-detector studies

Keep detector outputs in separate directories:

```bash
# CMS sample production
python3 launch_slurm_jobs.py --input Train --output /path/to/out_cms --detector CMS --num-runs 50

# ATLAS sample production
python3 launch_slurm_jobs.py --input Train --output /path/to/out_atlas --detector ATLAS --num-runs 50
```

Both detector cards are configured to write compatible high-level branches
(`Jet`, `GenJet`, `MissingET`, `ScalarHT`, `Rho`, `ParticleFlowCandidate`,
`Vertex`), so downstream analysis code can use the same feature extraction
pipeline with minimal or no branch remapping.

## Demonstrating robustness across experimental setups

To show that QCD vs SVJ discrimination generalizes across detector assumptions:

1. **Within-detector baselines**
   - Train/evaluate on CMS only.
   - Train/evaluate on ATLAS only.
2. **Cross-detector transfer**
   - Train on CMS, test on ATLAS.
   - Train on ATLAS, test on CMS.
3. **Merged training**
   - Train on a mixed CMS+ATLAS dataset and evaluate on each detector separately.
4. **Fairness controls**
   - Keep physics generation settings identical across detectors.
   - Match event counts and class balance (QCD/SVJ) per split.
   - Report the same metrics (ROC AUC, SIC/significance improvement, calibrated
     working points) for all comparisons.

## References

SVJ data card taken from: https://github.com/cms-svj/SVJProduction/blob/Run2_UL/python/svjHelper.py
