"""Generate and optionally submit SLURM jobs for Delphes detector simulation.

Each input Pythia datacard (.txt) is simulated --num-runs times, where each run
produces 10k events. For example, use --num-runs 50 for 500k events or
--num-runs 10 for 100k events per datacard.
"""

import argparse
import os
import subprocess
from time import sleep

SLURM_TEMPLATE = """\
#!/bin/bash
#SBATCH --partition={partition}
#SBATCH --account={account}
#SBATCH --mem={mem_mb}
#SBATCH --time={time_limit}
#SBATCH --job-name=Delphes_{job_id}
#SBATCH --error={err_log}
#SBATCH --output={out_log}
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=gkrzmanc@student.ethz.ch

export APPTAINER_TMPDIR=/work/gkrzmanc/singularity_tmp
export APPTAINER_CACHEDIR=/work/gkrzmanc/singularity_cache
# Clear host Pythia env vars so they don't interfere with the container
export PYTHIA8DATA=
export PYTHIA8=
export PYTHIA8_DIR=

BINDINGS="-B /t3home/gkrzmanc/ -B /work/gkrzmanc/ -B /pnfs/psi.ch/cms/trivcat/store/user/gkrzmanc/"

srun singularity exec $BINDINGS --nv \\
    docker://scailfin/delphes-python-centos:latest \\
    DelphesPythia8 delphes_card_CMS_pileup_HV.tcl {in_file} {out_file}
"""


def build_slurm_script(in_file, out_file, job_id, partition="standard",
                        account="t3", mem_mb=25000, time_limit="07:00:00"):
    log_dir = f"jobs/logs/{job_id}"
    return SLURM_TEMPLATE.format(
        partition=partition,
        account=account,
        mem_mb=mem_mb,
        time_limit=time_limit,
        job_id=job_id,
        err_log=f"{log_dir}_err.txt",
        out_log=f"{log_dir}_out.txt",
        in_file=in_file,
        out_file=out_file,
    )


def hypothesis_name(filename):
    """Strip _partN suffix and .txt extension to get the hypothesis name."""
    name = filename.removesuffix(".txt")
    if "_part" in name:
        name = name.rsplit("_part", 1)[0]
    return name


def main():
    parser = argparse.ArgumentParser(
        description="Generate and submit SLURM jobs for Delphes simulation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input", type=str, required=True,
                        help="Input directory containing Pythia datacard .txt files")
    parser.add_argument("--output", type=str, required=True,
                        help="Output directory for the produced ROOT files")
    parser.add_argument("--num-runs", type=int, default=1,
                        help="Number of simulation runs per datacard file "
                             "(each run produces 10k events)")
    parser.add_argument("--no-submit", "-ns", action="store_true", default=False,
                        help="Generate SLURM scripts without submitting them")
    args = parser.parse_args()

    os.makedirs("jobs/slurm_files", exist_ok=True)
    os.makedirs("jobs/logs", exist_ok=True)

    datacard_files = sorted(f for f in os.listdir(args.input) if f.endswith(".txt"))
    if not datacard_files:
        print(f"No .txt datacard files found in {args.input}")
        return

    total_jobs = 0
    for datacard in datacard_files:
        hypo = hypothesis_name(datacard)
        file_id = datacard.removesuffix(".txt")
        in_file = os.path.join(args.input, datacard)

        for run in range(args.num_runs):
            run_suffix = f"_part{run}" if args.num_runs > 1 else ""
            job_id = f"{file_id}{run_suffix}"

            out_dir = os.path.join(args.output, hypo)
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, f"{file_id}{run_suffix}.root")

            script = build_slurm_script(in_file, out_file, job_id)
            script_path = f"jobs/slurm_files/{job_id}.sh"
            with open(script_path, "w") as f:
                f.write(script)

            total_jobs += 1
            if not args.no_submit:
                subprocess.run(["sbatch", script_path], check=True)
                sleep(0.3)

    events_per_file = total_jobs * 10000
    print(f"Generated {total_jobs} SLURM job scripts "
          f"({len(datacard_files)} datacards x {args.num_runs} runs, "
          f"{events_per_file:,} total events)")
    if args.no_submit:
        print("Dry run: jobs were NOT submitted (--no-submit)")


if __name__ == "__main__":
    main()
