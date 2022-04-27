#!/bin/sh


#script to wrap the generation of backup tar files to catch up

for file in `cat $1`
do
	/gws/nopw/j04/slstr_cpa/software/slstr_calibration/create_tar.sh $file /gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/backup/S3C/ICM/
	#echo $file

done
