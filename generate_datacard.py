flist = []

for mMed in [700, 800, 900, 1000, 1100, 1200]:
    for rinv in [0.3,0.5,0.7]:
        for mDark in [20]:
            flist.append({"channel": "s", "mMediator": mMed, "mDark": mDark, "rinv": rinv, "alpha": "peak", "scout": True})

import argparse
import subprocess
#parser = argparse.ArgumentParser(description='Run the SVJ scouting')
#parser.add_argument("--output", type=str, description="Name of the output directory")

import sys

for f in flist:
    # python svj_helper.py --mZprime <mMed> --mDark <mDark> --rinv <rinv> --alpha <alpha>
    # exec the command
    
    cmd = f"python svj_helper.py --mZprime {f['mMediator']} --mDark {f['mDark']} --rinv {f['rinv']} --alpha {f['alpha']} --directory Test/SVJ -n 10000"
    print(f"Executing {cmd}")
    subprocess.call(cmd, shell=True)
    mMed = f['mMediator']
    rInv = f['rinv']
    if (mMed == 700 and rInv== 0.7) or (mMed == 900 and rInv == 0.3):
        # Signal hypotheses used for traning
        cmd = f"python svj_helper.py --mZprime {f['mMediator']} --mDark {f['mDark']} --rinv {f['rinv']} --alpha {f['alpha']} --directory Train/SVJ -n 10000"
        print(f"Executing {cmd}")
        subprocess.call(cmd, shell=True)
    print("Done")

# python svj_helper.py --mZprime 700 --mDark 20  --rinv 0.7 --alpha  peak --directory Delphes_020425_train3 -n 100000
