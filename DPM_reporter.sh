#!/bin/sh

#Script to wrap catchup report generation on 
#/gws/nopw/j04/slstr_cpa/software/slstr_calibration/manifest_checker.sh /gws/nopw/j04/slstr_cpa/incoming/DPM/daily_manifest/2015_059_DPM_daily_manifest.txt /gws/nopw/j04/slstr_cpa/incoming/DPM /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/FM02/DPM /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/transfer_report/DPM

for manifest_file in `cat $1`
do

	/gws/nopw/j04/slstr_cpa/software/slstr_calibration/manifest_checker.sh ${manifest_file} /gws/nopw/j04/slstr_cpa/incoming/DPM /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/S3C/DPM /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/transfer_report/DPM

done
