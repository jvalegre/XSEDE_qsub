# XSEDE_qsub
Script to send jobs to Comet and Bridges on XSEDE. It reads Gaussian com files and uses the memory and number of processors specified in those com files (with %mem and %nproc or %nprocshared keywords).

## Using new accounts or partitions
Right now, the program it's set up for the accounts associated with the Paton group. If you want to use a different account, add it to the lists at the begining of the script (ACCOUNTS_LIST_COMET for Comet accounts and ACCOUNTS_LIST_BRIDGES for Bridges accounts).

Also, if you want to use different partitions, add it to the lists at the begining of the script (PARTITION_LIST_COMET for Comet partitions and PARTITION_LIST_BRIDGES for Bridges partitions.

## Options
\*.com: takes all the com files in your working directory. Individual files can also be defined (i.e. FILENAME.com) 

-t: time. Default: 48 hours

--cluster: specify the cluster to run the calcs in. Options: comet, bridges

--chk: include this if you want to create chk files

--wfn: include this if you want to create wfn files

--acomet and --abridges: account that you are using to send the calculations. Additional accounts can be added

--pcomet and --pbridges: partitions where you want to run the calculations. Options Comet: shared,compute,debug. Options Bridges: RM-shared,RM,RM-small. More options can be added manually.

## Examples of command lines to run the script
python XSEDE_qsub \*.com -t 36:00:00 --cluster comet --acomet cst152 --pcomet shared --chk

\** It's convenient to create aliases depending on the cluster you are using (i.e. for Comet, alias sub="python XSEDE_qsub --cluster comet")
