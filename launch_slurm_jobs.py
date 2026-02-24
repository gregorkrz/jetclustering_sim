import argparse
import os
from time import sleep

parser = argparse.ArgumentParser(description='Run the SVJ scouting')
parser.add_argument("--input", type=str, help="Name of the input directory with the txt files - Pythia datacards (e.g. Train/ or Test/)")
parser.add_argument("--output", type=str, help="Name of the output directory, in which to save the root files")
parser.add_argument("--njobs", "-N", type=int, default=1, help="Number of SLURM jobs to launch per txt file")
parser.add_argument("--no-submit", "-ns", action="store_true", default=False, help="Do not submit jobs")
args = parser.parse_args()


def get_slurm_file_text(in_file, out_file, file_id):
    # file_id is basically in_file without the .txt ending
    bindings = "-B /t3home/gkrzmanc/ -B /work/gkrzmanc/  -B /pnfs/psi.ch/cms/trivcat/store/user/gkrzmanc/ "
    partition = "standard"
    account = "t3"
    d = "jobs/logs/{}".format(file_id)
    err = d + "_err.txt"
    log = d + "_log.txt"
    file = f"""#!/bin/bash
#SBATCH --partition={partition}           # Specify the partition
#SBATCH --account={account}               # Specify the account
#SBATCH --mem=25000                   # Request 10GB of memory
#SBATCH --time=07:00:00               # Set the time limit to 1 hour
#SBATCH --job-name=Delphes_{file_id}  # Name the job
#SBATCH --error={err}         # Redirect stderr to a log file
#SBATCH --output={log}         # Redirect stderr to a log file
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=gkrzmanc@student.ethz.ch
export APPTAINER_TMPDIR=/work/gkrzmanc/singularity_tmp
export APPTAINER_CACHEDIR=/work/gkrzmanc/singularity_cache
# Otherwise your env vars can mess with the singularity container for some reason
export PYTHIA8DATA=
export PYTHIA8=
export PYTHIA8_DIR=
srun singularity exec {bindings}  --nv docker://scailfin/delphes-python-centos:latest DelphesPythia8 delphes_card_CMS_pileup_HV.tcl {in_file} {out_file}
    """
    return file

os.makedirs("jobs/slurm_files", exist_ok=True)
os.makedirs("jobs/logs", exist_ok=True)

for root, dirs, files in os.walk(args.input):
    dirs.sort()
    for file in sorted(files):
        if not file.endswith(".txt"):
            continue
        print(file)
        file_id = file.split(".txt")[0]
        file_id_without_part = file_id
        if "_part" in file_id:
            file_id_without_part = file_id.split("_part")[0]
        in_file = os.path.join(root, file)
        rel_path = os.path.relpath(root, args.input)
        for job_idx in range(1, args.njobs + 1):
            job_file_id = f"{file_id}_{job_idx}"
            out_folder = os.path.join(args.output, rel_path, file_id_without_part)
            out_file = os.path.join(out_folder, f"{file_id}_{job_idx}.root")
            os.makedirs(out_folder, exist_ok=True)
            ftxt = get_slurm_file_text(in_file, out_file, job_file_id)
            with open(f"jobs/slurm_files/{job_file_id}.sh", "w") as f:
                f.write(ftxt)
            print("Wrote to", f"jobs/slurm_files/{job_file_id}.sh")
            if not args.no_submit:
                os.system(f"sbatch jobs/slurm_files/{job_file_id}.sh")
                sleep(0.3)

# Launch the slurm jobs to generate the root files:
# python launch_slurm_jobs.py --input Train --output /work/gkrzmanc/jetclustering/data/Train -N 10
# python launch_slurm_jobs.py --input Test --output /work/gkrzmanc/jetclustering/data/Test -N 10
