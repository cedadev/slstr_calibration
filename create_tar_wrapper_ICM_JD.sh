#!/bin/sh

if [ $# != 2 ]
then
	echo "Usage: <YYYY_JD> <op directory to put tar>"
	exit
fi

if [ ! -d $2 ]
then
	echo "Dir ${2} does not exist!"
	exit
fi

#script to wrap the generation of backup tar files to catch up
#year_day=`date -d "now - 1 day" +"%Y_%j"`
report_dir=`echo "/gws/nopw/j04/slstr_cpa/incoming/ICM/daily_manifest/"`
manifest_file=`echo "${report_dir}/${1}_ICM_daily_manifest.txt.report.target"`

echo $manifest_file
if [ -f $manifest_file ]
then
	echo "Creating tar backup for $year_day"
	/gws/nopw/j04/slstr_cpa/software/slstr_calibration/create_tar.sh $manifest_file $2

else
	echo "No such file: ${manifest_file}"
fi
