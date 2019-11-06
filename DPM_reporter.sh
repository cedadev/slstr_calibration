#!/bin/sh

#Script to wrap catchup report generation on 
#/group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/manifest_checker.sh /group_workspaces/cems2/slstr_cpa/incoming/DPM/daily_manifest/2015_059_DPM_daily_manifest.txt /group_workspaces/cems2/slstr_cpa/incoming/DPM /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/FM02/DPM /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/transfer_report/DPM

for manifest_file in `cat $1`
do

	/group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/manifest_checker.sh ${manifest_file} /group_workspaces/cems2/slstr_cpa/incoming/DPM /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/S3C/DPM /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/transfer_report/DPM

done
