#!/bin/sh

#Script to find files  from last 10 minutes - this job to be run EVERY MINUTE

#NOTE: this is a wrapper script to move_data_from_incoming.sh - this will look and check for md5 files

if [ $# != 3 ]
then
        echo "Usage: SourceDir DestinationDir move[True|False]"
        exit
fi

#jd=`date +%j`
#hour=`date +%H`
#min=`date +%M`
source_dir=$1
destination=$2
move=$3

#year=`date +%Y`

#year="2015"
for minute in 20 19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1
do
	datestring=`date -d "now - $minute  minutes" +"%Y_%j_%H_%M"`
	exp_filename=`echo $datestring"_~000.ArcRaw"`
	exp_filename_path=`echo "$source_dir/$exp_filename"`
	
	#perform move only if flag arguement is set
        if [ $move = "True" ]
        then
                #echo "$file to $destination"
                /gws/nopw/j04/slstr_cpa/software/slstr_calibration/move_data_from_incoming.sh $exp_filename_path $destination
        else
                echo -e "Looking for file: $exp_filename_path"
        fi
done
