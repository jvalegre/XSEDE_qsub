#! /usr/bin/env python
'''
Submission script adapted for Comet and Bridges HPCs, including
multiple options such as accounts, partitions, n of processors,
memory, etc.
Author: Juan V. Alegre Requena, please report any bugs
or suggestions to juanvi89@hotmail.com
'''

import os
from argparse import ArgumentParser

ACCOUNTS_LIST_COMET = ['cst123','cst127','cst128']
ACCOUNTS_LIST_BRIDGES = ['ch5fq3p','ch5pj3p']
PARTITION_LIST_COMET = ['shared','compute','debug']
PARTITION_LIST_BRIDGES = ['RM-shared','RM','RM-small']

def prepare_sh(inp_file):
    # this prepares a queue submiting file with slurm options that will be run later
    if args.cluster == "comet":
        scratch="/oasis/scratch/comet/$USER/temp_project/$SLURM_JOBID"

        sh_s="#!/bin/bash\n\n#SBATCH -t "+str(args.t)+"\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1"
        sh_s=sh_s+"\n#SBATCH --cpus-per-task="+str(nproc)
        partition = args.pcomet
        if nproc == 24 and partition == 'shared':
            partition = 'compute'
        sh_s=sh_s+"\n#SBATCH -p "+partition
        sh_s=sh_s+"\n#SBATCH --job-name="+inp_file
        sh_s=sh_s+'\n#SBATCH --account='+ args.acomet
        sh_s=sh_s+'\n#SBATCH --mem='+ str(mem) +'GB'
        sh_s=sh_s+"\nfile="+inp_file+"\ninpfile=${file}.com\noutfile=${file}.log\n\n"

        sh_s=sh_s+"export MODULEPATH=/share/apps/compute/modulefiles/applications:$MODULEPATH\n"
        sh_s=sh_s+"export GAUSS_SCRDIR="+scratch+"\nset OMP_NUM_THREADS $SLURM_CPUS_ON_NODE\n"
        sh_s=sh_s+"module load gaussian/16.C.01\n"
        sh_s=sh_s+"Homepath=$(pwd)\n"
        sh_s=sh_s+"mkdir $GAUSS_SCRDIR\n\n"
        sh_s=sh_s+"touch $Homepath/$outfile\n"
        sh_s=sh_s+"cp $inpfile $GAUSS_SCRDIR\n"
        sh_s=sh_s+"cd $GAUSS_SCRDIR\n"
        sh_s=sh_s+"\n/opt/gaussian/16.C.01/g16/g16 < $GAUSS_SCRDIR/$inpfile > $Homepath/$outfile\n\n"
        sh_s=sh_s+" echo 'Gaussian Job finished or failed (Good luck!!)'"
        if args.chk == True:
            sh_s=sh_s+"cp $GAUSS_SCRDIR/*.chk $Homepath\n"
        if args.wfn == True:
            sh_s=sh_s+"cp $GAUSS_SCRDIR/*.wfn $Homepath\n"

        sh_file=open(inp_file+".sh","w")
        sh_file.write(sh_s)
        sh_file.close()

    elif args.cluster == "bridges":
        scratch="/pylon5/ch5fq3p/$USER/$SLURM_JOBID"

        sh_s="#!/bin/csh\n#SBATCH -t "+str(args.t)+"\n#SBATCH -N 1"
        partition = args.pbridges
        if nproc == 28 and partition == 'RM-shared':
            partition = 'RM'
        sh_s=sh_s+"\n#SBATCH -p "+partition
        sh_s=sh_s+'\n#SBATCH --mem='+ str(mem) +'GB'
        sh_s=sh_s+"\n#SBATCH --job-name="+inp_file+"\n#SBATCH --ntasks-per-node=1"

        sh_s=sh_s+"\n#SBATCH --cpus-per-task="+str(nproc)+'\n#SBATCH --account='+ args.abridges +'\n\n'

        sh_s=sh_s+"module load gaussian\n"
        sh_s=sh_s+"source $g16root/g16/bsd/g16.login\n"
        sh_s=sh_s+"set echo\n"
        sh_s=sh_s+"setenv GAUSS_SCRDIR $LOCAL\n"
        sh_s=sh_s+"setenv OMP_NUM_THREADS $SLURM_CPUS_ON_NODE\n"
        sh_s=sh_s+"cd $SLURM_SUBMIT_DIR\n"
        sh_s=sh_s+"set JOBNAME="+inp_file+"\n"
        sh_s=sh_s+"set INPUT=${JOBNAME}.com\n\n"
        sh_s=sh_s+"srun g16 < $INPUT > $JOBNAME.log\n\n"
        sh_s=sh_s+"echo 'Gaussian Job finished or failed (Good luck!!)'"

        if args.chk == True:
            sh_s=sh_s+"cp $GAUSS_SCRDIR/*.chk $Homepath\n"
        if args.wfn == True:
            sh_s=sh_s+"cp $GAUSS_SCRDIR/*.wfn $Homepath\n"

        sh_file=open(inp_file+".sh","w")
        sh_file.write(sh_s)
        sh_file.close()

    else:
        print('Specify your cluster with --cluster (i.e. --cluster comet or --cluster bridges)')

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(nargs = '*', dest = 'input_file')
    parser.add_argument('-t', type=str, default="47:59:59", help='Walltime for job in format hh:mm:ss')
    parser.add_argument('--cluster', type=str, default='', help='Cluster used (comet or bridges)')
    parser.add_argument('--chk', action="store_true", default=False, help='Copy .chk files into your home directory after jobs are done')
    parser.add_argument('--wfn', action="store_true", default=False, help='Copy .wfn files into your home directory after jobs are done')
    parser.add_argument('--acomet', type=str, choices=ACCOUNTS_LIST_COMET, default=ACCOUNTS_LIST_COMET[0],
                            help='Account to use for job in Comet')
    parser.add_argument('--abridges', type=str, choices=ACCOUNTS_LIST_BRIDGES, default=ACCOUNTS_LIST_BRIDGES[0],
                            help='Account to use for job in Bridges')
    parser.add_argument('--pcomet', choices=PARTITION_LIST_COMET, default=PARTITION_LIST_COMET[0],
                            help='Partition used in Comet')
    parser.add_argument('--pbridges', choices=PARTITION_LIST_BRIDGES, default=PARTITION_LIST_BRIDGES[0],
                            help='Partition used in Bridges')

    args = parser.parse_args()

    for file in args.input_file:
        # This part recognizes the amount of CPUs for the job specified in the input files
        nproc = 1
        mem = 60
        f=open(file,"r")
        for line in f.readlines()[:15]:
            if line.lower().find('%nproc') > -1:
                nproc = int(line.split('=')[1])
            if line.lower().find('%mem') > -1:
                mem = line.lower().split('=')[1]
                mem = int(mem.split('gb')[0])
        f.close()

        prepare_sh(file.split(".com")[0])

        if nproc == 1:
            print("submitting job: "+file.split(".com")[0]+" with 1 processor.")
        elif nproc > 1:
            print("submitting job: "+file.split(".com")[0]+" with "+str(nproc)+" processors.")
        else:
            print("0 or negative number of processors specified in the input file.")

        os.system("sbatch "+file.split(".com")[0]+".sh")
