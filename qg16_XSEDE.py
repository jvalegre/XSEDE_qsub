#! /usr/bin/env python
'''
Submission script adapted for Comet and Bridges HPCs, including
multiple options such as accounts, partitions, n of processors,
memory, etc.
Author: Juan V. Alegre Requena, please report any bugs to juanvi89@hotmail.com
'''
import math
import time
from datetime import datetime, timedelta
from glob import glob
import string
import os
import os.path
import sys
import subprocess
from argparse import ArgumentParser

ACCOUNTS_LIST_COMET = ['cst123','cst128']
ACCOUNTS_LIST_BRIDGES = ['ch5fq3p','ch5pj3p']
PARTITION_LIST_COMET = ['shared','compute','debug']
PARTITION_LIST_BRIDGES = ['RM-shared','RM','RM-small']

def prepare_sh(inp_file, priority="",nproc="",scratch=""):
    # this prepares a queue submiting file with slurm options that will be run later
    inp_file=inp_file.split(".com")[0]
    file=open(inp_file+".com","r")
    keywds=file.readlines()
    file.close()

    if args.cluster == "comet":
        scratch="/oasis/scratch/comet/$USER/temp_project/$SLURM_JOBID"

        sh_s="#!/bin/bash\n\n#SBATCH -t "+str(args.t)+"\n#SBATCH --nodes=1\n#SBATCH --ntasks-per-node=1\n#SBATCH --cpus-per-task="+str(args.n)
        sh_s=sh_s+"\n#SBATCH -p "+args.pcomet
        sh_s=sh_s+"\n#SBATCH --job-name="+inp_file
        sh_s=sh_s+'\n#SBATCH --account='+ args.acomet
        sh_s=sh_s+'\n#SBATCH --mem='+ str(args.mem) +'GB'
        sh_s=sh_s+"\nfile="+inp_file+"\ninpfile=${file}.com\noutfile=${file}.log\n\n"

        sh_s=sh_s+"export MODULEPATH=/share/apps/compute/modulefiles/applications:$MODULEPATH\n"
        sh_s=sh_s+"export GAUSS_SCRDIR="+scratch+"\nset OMP_NUM_THREADS $SLURM_CPUS_ON_NODE\n"
        sh_s=sh_s+"module load gaussian/16.C.01\n"
        sh_s=sh_s+"Homepath=$(pwd)\n"
        sh_s=sh_s+"mkdir $GAUSS_SCRDIR\n"
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

    if args.cluster == "bridges":
        scratch="/pylon5/ch5fq3p/$USER/$SLURM_JOBID"

        sh_s="#!/bin/csh\n#SBATCH -t "+str(args.t)+"\n#SBATCH -N 1"
        sh_s=sh_s+"\n#SBATCH -p "+args.pbridges
        sh_s=sh_s+'\n#SBATCH --mem='+ str(args.mem) +'GB'
        sh_s=sh_s+"\n#SBATCH --job-name="+inp_file+"\n#SBATCH --ntasks-per-node=1"

        sh_s=sh_s+"\n#SBATCH --cpus-per-task="+str(args.n)+'\n#SBATCH --account='+ args.abridges +'\n\n'

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

def launch_job(sh_file):
    # run the ".sh" file with slurm options. It uses sbatch, should work with srun as well.
    sh_file=sh_file.replace(".com","")
    os.system("sbatch "+sh_file)

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(nargs = '*', dest = 'input_file')
    parser.add_argument('-t', type=str, default="47:59:59", help='Walltime for job in format hh:mm:ss')
    parser.add_argument('-n', type=int, default=24, help='Number of cpus to use per node')
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
    parser.add_argument('--mem', type=int, default=60,
                            help='Total memory in GB used')

    args = parser.parse_args()

    for file in args.input_file:

        #default values:
        priority=""
        queue_position=0
        file_name=""
        # a tweak: if you run all works with 24 processors, you can change this to: nproc="24"; it will ensure that nsharedproc will be changed in all inputs to 24
        nproc=""
        error_checking=True
        cont="y"
        scratch=""

        if len(sys.argv)==1:
            print ("usage: "+sys.argv[0]+" input file [options]")
            print ("launch g16 job to the queue for input file. Input file extension must be either '.com' or '.inp'; if it is not given will assume '.com'")
            print ("options:    -np  number of processors; if not given, will attempt to read it from the input file")
            sys.exit()

        if len(sys.argv) > 1:
            i=0
            while i< len(sys.argv):

                if i<len(sys.argv):
                    if sys.argv[i].split(".")[-1]=="com" or sys.argv[i].split(".")[-1]=="inp":
                        file_name=file.split(".")[0]
                    else:
                        if sys.argv[i].isdigit() and not (os.path.isfile("./"+sys.argv[i]+".com") or (os.path.isfile("./"+sys.argv[i]+".inp")) ):
                            nproc=sys.argv[i]
                        else:
                            file_name=file.split(".")[0]
                    i=i+1

        if queue_position!=0:
            priorities=sorted(get_queue_priorities(),reverse=True)
            if queue_position<len(priorities): priority=str(priorities[queue_position-1]+1)
            else: priority=str(priorities[-1]-1)

        if cont=="y":
            prepare_sh (file_name,str(priority),nproc,scratch)
            print ("submitting job: "+file_name.split(".com")[0])
            launch_job(file_name+".sh")
