import argparse

parser = argparse.ArgumentParser(description='Run the SVJ scouting')
parser.add_argument("--input", type=str, help="Name of the input directory with the txt files - Pythia datacards") # Delphes_020425_train2
parser.add_argument("--output", type=str, help="Name of the output directory, in which to save the root files")
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

import os
from time import sleep

for file in os.listdir(args.input):
    if True:#file.endswith(".txt") and "0.3" in file and "900" in file:
        print(file)
        file_id = file.split(".txt")[0]
        file_id_without_part = file_id
        #if not (file_id_without_part.startswith("SVJ_mZprime-900_mDark-20_rinv-0.3") or ("SVJ_mZprime-700_mDark-20_rinv-0.7"))
        if "_part" in file_id:
            file_id_without_part = file_id.split("_part")[0]
        in_file = args.input + "/" + file
        out_folder = args.output + "/" + file_id_without_part
        out_file = out_folder + "/" + file_id + ".root"
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        ftxt = get_slurm_file_text(in_file, out_file, file_id)
        if not os.path.exists("jobs/slurm_files"):
            os.makedirs("jobs/slurm_files")
        if not os.path.exists("jobs/logs"):
            os.makedirs("jobs/logs")
        with open(f"jobs/slurm_files/{file_id}.sh", "w") as f:
            f.write(ftxt)
        print("Wrote to", f"jobs/slurm_files/{file_id}.sh")
        if not args.no_submit:
            os.system(f"sbatch jobs/slurm_files/{file_id}.sh")
    if not args.no_submit:
        sleep(0.3) # For some reason this is needed, otherwise some jobs don't get submitted???

# Launch the slurm jobs to generate the root files:
# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/QCD --output /work/gkrzmanc/jetclustering/data/QCD_test
# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/Delphes_020425_train2 --output /work/gkrzmanc/jetclustering/data/Delphes_020425_train2_PU_PFfix
# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/QCDtrain --output /work/gkrzmanc/jetclustering/data/QCDtrain
# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/Delphes_020425_test_noHM --output /work/gkrzmanc/jetclustering/data/Delphes_020425_test_PU_PFfix







## old commands

# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/Delphes_020425_test --output /work/gkrzmanc/jetclustering/data/Delphes_020425_test_PU
# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/Delphes_020425_train2 --output /work/gkrzmanc/jetclustering/data/Delphes_020425_train2_PU_PFfix
# python launch_slurm_jobs.py --input /work/gkrzmanc/jetclustering/LJP/Delphes_020425_val --output /work/gkrzmanc/jetclustering/data/Delphes_020425_val_PU

#Delphes_020425_test_noHM
