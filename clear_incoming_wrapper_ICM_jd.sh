#!/bin/sh


#script to wrap the generation of backup tar files to catch up
#year_day=`date -d "now - 1 day" +"%Y_%j"`
year_day=$1
report_dir=`echo "/group_workspaces/cems2/slstr_cpa/incoming/ICM/daily_manifest/"`
manifest_file_incoming=`echo "${report_dir}/${year_day}_ICM_daily_manifest.txt.report.incoming"`
manifest_file_target=`echo "${report_dir}/${year_day}_ICM_daily_manifest.txt.report.target"`

echo $manifest_file
if [ -f $manifest_file ]
then
	echo "Clearing incoming for $year_day"
	/group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/clear_incoming.sh $manifest_file_incoming $manifest_file_target

fi
