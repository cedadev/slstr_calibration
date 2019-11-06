#!/bin/sh

#Script to report on an hours worth of contents

reporttm=`date +"%y-%m-%dT%H:%M:%S"`

if [ $# != 4 ]
then
	echo -e "Usage: basedir jd hour loglocation"
	exit
fi

basedir=$1
jd=$2
hour=$3
logloc=$4


year="2015"

targetdir=`echo $basedir"/"$jd"/"$hour`

reportlog=`echo $logloc"/"$jd"_"$hour"_log.txt"`

#clear old report..
if [ -f $reportlog ]
then
	echo -e "Reportfile at $reportlog already exists.. removing it!"
	rm -f >> $reportlog
else
	echo -e "Creating reportfile at $reportlog"
fi

#number_dirs_for_hour=`find $targetdir -type d | wc -l`

missing_dir_num=0
missing_file_num=0
#Missing directories - work out what directories are missing
cnt=0

echo -e "DATA REPORT FOR: $targetdir ($reporttm)\n" > $reportlog

#check a data directory exists for this target dir
if [ ! -d $targetdir ]
then
	echo -e "MISSING DIRECTORY: $targetdir (not created yet?)" >> $reportlog
	exit
fi

while [ $cnt -lt 60 ]
do
	#pad out the syntax
	if [ $cnt -lt 10 ]
	then
		min=`echo "0"$cnt`
	else
		min=$cnt
	fi

	#check whether directory exists
	mindir=`echo $targetdir"/"$min`
	if [ ! -d $mindir ]
	then
		echo -e "MISSING DIRECTORY: $jd/$hour/$min not present under $basedir" >> $reportlog
		missing_dir_num=`expr $missing_dir_num + 1`
	else
	
		#if the directory exists check that there is data in there...
		expected_filename=`echo $mindir"/"$year"_"$jd"_"$hour"_"$min"_~000.ArcRaw"`
	        expected_filename_md5=`echo $expected_filename".md5"`

        	if [ ! -f $expected_filename ]
        	then
                	echo -e "MISSING FILE: $expected_filename" >> $reportlog
        	fi
		
		if [ ! -f $expected_filename_md5 ]
                then
                        echo -e "MISSING FILE: $expected_filename_md5" >> $reportlog
                fi

	fi
	cnt=`expr $cnt + 1`
done
