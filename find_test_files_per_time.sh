#!/bin/sh

#Script to find files based on a given hour minute etc

#NOTE - if an "A" is supplied instead of a number for JD, hour or minute this will be treated as a wildcard


######### FUNCTIONS ##########


########## MAIN ##############
if [ $# != 8 ]
then
	echo "Usage: Year JD Hour Min SourceDir DestinationDir move[True|False] <log dir)"
	exit
fi

year=$1
jd=$2
hour=$3
min=$4
source_dir=$5
destination=$6
move=$7
logdir=$8

#year="2015"

search_string=`echo $year"_"$jd"_"$hour"_"$min`
search_string=`echo $search_string | sed 's/A/\*/g'`
search_string=`echo $search_string"*.ArcRaw"`
echo $search_string

echo "Searching for files with pattern: $search_string"
#files_to_move=`find $source_dir -name ${search_string} -print`

for file in `find $source_dir -name ${search_string} -print`
do

	#perform move only if flag arguement is set
	if [ $move = "True" ]
	then
		#echo "$file to $destination"
		/group_workspaces/cems2/slstr_cpa/software/slstr_calibration/move_data_from_incoming.sh $file $destination $logdir
	else
		echo -e "Found file: $file"	
	fi
done
