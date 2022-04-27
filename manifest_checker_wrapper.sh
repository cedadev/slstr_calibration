#!/bin/sh

#This script is to wrap the manifest file checking  FOR THE PREVIOUS DAY and as such is hardwired to the dir structure in the incoming slstr_cpa gws

if [ $# != 1 ]
then
	echo "Usage: <Type DPM|ICM>"
	exit
fi

type=$1

if [ "$type" = "DPM" ]
then
	manifest_file_name=`date -d "now - 1 day" +"%Y_%j_DPM_daily_manifest.txt"`

	manifest=`echo "/gws/nopw/j04/slstr_cpa/incoming/DPM/daily_manifest/"$manifest_file_name`

	if [ -f $manifest ]
	then
        	/gws/nopw/j04/slstr_cpa/software/slstr_calibration/manifest_checker.sh $manifest /gws/nopw/j04/slstr_cpa/incoming/DPM /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/S3C/DPM/ /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/transfer_report/DPM

	else
		echo "No manifest file generated: $manifest"
	fi
fi

if [ "$type" = "ICM" ]
then
        manifest_file_name=`date -d "now - 1 day" +"%Y_%j_ICM_daily_manifest.txt"`

        manifest=`echo "/gws/nopw/j04/slstr_cpa/incoming/ICM/daily_manifest/"$manifest_file_name`

	if [ -f $manifest ]
	then
        	/gws/nopw/j04/slstr_cpa/software/slstr_calibration/manifest_checker.sh $manifest /gws/nopw/j04/slstr_cpa/incoming/ICM /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/S3C/ICM/ /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/transfer_report/ICM

	else
                echo "No manifest file generated: $manifest"
	fi
fi


