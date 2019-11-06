#!/bin/sh


#script to wrap the generation of backup tar files to catch up
year_day=`date -d "now - 1 day" +"%Y_%j"`
report_dir=`echo "/group_workspaces/cems2/slstr_cpa/incoming/DPM/daily_manifest/"`
manifest_file=`echo "${report_dir}/${year_day}_DPM_daily_manifest.txt.report.target"`

echo $manifest_file
if [ -f $manifest_file ]
then
	echo "Creating tar backup for $year_day"
	/group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/create_tar.sh $manifest_file /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/backup/S3C/DPM/

fi
