#!/bin/sh


#script to wrap the generation of backup tar files to catch up

for file in `cat $1`
do
	/group_workspaces/cems2/slstr_cpa/jasmin_scripts/testing/create_tar.sh $file /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/backup/S3C/DPM/
	#echo $file

done
