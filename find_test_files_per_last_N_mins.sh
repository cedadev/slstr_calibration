#!/bin/sh

#Script to find files  from last N minutes before runtime - this job to be run EVERY MINUTE

#NOTE: this is a wrapper script to move_data_from_incoming.sh - this will look and check for md5 files

if [ $# != 5 ]
then
        echo "Usage: SourceDir DestinationDir timeGap(mins before NOW) move[True|False] <log directory>"
        exit
fi


#jd=`date +%j`
#hour=`date +%H`
#min=`date +%M`
source_dir=$1
destination=$2
gap=$3
move=$4
logdir=$5

#year=`date +%Y`

#year="2015"
count=0
mincount=$gap
while [ $mincount -ne 1  ]
do
	mincount=`expr $gap - $count`

	datestring=`date -d "now - $mincount  minutes" +"%Y_%j_%H_%M"`
	exp_filename=`echo $datestring"_~000.ArcRaw"`
        exp_filename_path=`echo "$source_dir/$exp_filename"`

        #perform move only if flag arguement is set
        if [ $move = "True" ]
        then
                #echo "$file to $destination"
                /group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/move_data_from_incoming.sh $exp_filename_path $destination $logdir
        else
                echo -e "Looking for file: $exp_filename_path"
        fi

	count=`expr $count + 1`

done
