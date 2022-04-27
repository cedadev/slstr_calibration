#!/bin/sh


#script to wrap the generation of backup tar files to catch up
year_day=`date -d "now - 1 day" +"%Y_%j"`
report_dir=`echo "/gws/nopw/j04/slstr_cpa/incoming/ICM/daily_manifest/"`
manifest_file=`echo "${report_dir}/${year_day}_ICM_daily_manifest.txt.report.target"`

echo $manifest_file
if [ -f $manifest_file ]
then
	echo "Creating tar backup for $year_day"
	/gws/nopw/j04/slstr_cpa/software/slstr_calibration/create_tar.sh $manifest_file /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/backup/S3C/ICM/

fi
