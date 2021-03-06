# Prerequisites:
    (1) Create an account in XSEDE

    (2) Request Gaussian permissions for the Comet and Bridges clusters (send an email to the help desk (it's help@xsede.org as of 2020) requesting the permissions, not through the XSEDE user portal). 

    (3) To connect to the clusters (as of 2020), host names for the SFTP/SSH program or terminal:
    Bridges --> bridges.psc.xsede.org
    Comet --> comet.sdsc.xsede.org
    ** These are not webpages, these are host names to use in SFTP/SSH clients (i.e. WinSCP, Putty, ForkLift, FileZilla...) or in a terminal


# XSEDE_qsub
    Script to send jobs to Comet and Bridges on XSEDE. It reads Gaussian com files and uses the memory and number of processors specified in those com files (with %mem and %nproc or %nprocshared keywords).

## Using new accounts or partitions
    Right now, the program it's set up for the accounts associated with the Paton group. If you want to use a different account, add it to the lists at the begining of the script (ACCOUNTS_LIST_COMET for Comet accounts and ACCOUNTS_LIST_BRIDGES for Bridges accounts).

    Also, if you want to use different partitions, add it to the lists at the begining of the script (PARTITION_LIST_COMET for Comet partitions and PARTITION_LIST_BRIDGES for Bridges partitions.

## Options
    *.com: takes all the com files in your working directory. Individual files can also be defined (i.e. FILENAME.com) 

    -t: time. Default: 48 hours (format: 48:00:00, hh:mm:ss)

    --cluster: specify the cluster to run the calcs in. Options: comet, bridges

    --chk: include this if you want to create chk files

    --wfn: include this if you want to create wfn files

    --acomet and --abridges: account that you are using to send the calculations. Additional accounts can be added

    --pcomet and --pbridges: partitions where you want to run the calculations. Options Comet: shared,compute,debug. Options Bridges: RM-shared,RM,RM-small. More options can be added manually. By default, is less than the max number of processors (24 in Comet and 28 in Bridges) is used, the "shared" and "RM-shared" partitions are used. Otherwise, the "compute" and "RM" partitions are set as default automatically by the script.

## Examples of command lines to run the script
    It's convenient to create aliases depending on the cluster you are using (i.e. for Comet, alias sub="XSEDE_qsub --cluster comet"). To create an alias, edit your .bashrc file. .bashrc is a file that is already created in your home folder and can be edited as a text file, HOWEVER, by default it's hidden in your SFTP/SSH client. You can either change the settings of your client to see hidden files or use the XSEDE terminal and use the 'vim' command to edit the file. After you found the .bashrc file, edit it and add, for example:
    
    alias sub='/PATH/XSEDE_qsub.py --cluster comet'
    
    where PATH is the folder where XSEDE_qsub.py is located. As an example, if XSEDE_qsub.py was in /home/jvalegre/bin/, my alias for Comet would be: 
    
    alias sub='/home/jvalegre/bin/XSEDE_qsub.py --cluster comet'
    
    After you set the alias, you need to (only one time):
    
    (1) In the XSEDE terminal, go to your home folder where .bashrc is and type 'source .bashrc' (to update the content of .bashrc in your current session)
    (2) Go to where the XSEDE_qsub.py script is (in my case, "cd /home/jvalegre/bin") and type 'chmod 777 XSEDE_qsub.py' (this gives you rights to run the script)
    
    After these two steps, you can type "sub" to call the script from any folder (it would be like typing all the sentence you specified in the alias). So, for example, this is how I would call the script with the alias:
    
    The COM files I want to run are in the /home/jvalegre/test/ folder. In the terminal, I should go to that folder first ("cd /home/jvalegre/test/"). Then:
    
    (1) Run the script with: 'sub --acomet cst152 *.com -t 36:00:00 --chk'
    
