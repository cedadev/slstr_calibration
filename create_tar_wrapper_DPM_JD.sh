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
report_dir=`echo "/group_workspaces/cems2/slstr_cpa/incoming/DPM/daily_manifest/"`
manifest_file=`echo "${report_dir}/${1}_DPM_daily_manifest.txt.report.target"`

echo $manifest_file
if [ -f $manifest_file ]
then
	echo "Creating tar backup for $year_day"
	/group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/create_tar.sh $manifest_file $2

else
	echo "No such file: ${manifest_file}"
fi