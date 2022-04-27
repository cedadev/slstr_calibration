#!/bin/sh

#Script to create a daily report on file presence using the report generator script

if [ $# != 1 ]
then
	echo "Usage: JD(or 999 for yesterday"
	exit
fi

if [ $1 = '999' ]
then
	jd=`date -d "now - 1 day" +%j`
else
	jd=$1
fi

hour=0

reporttm=`date +"%y-%m-%dT%H:%M:%S"`
echo -e "\nGenerating report for DPM & ICM  $reporttm"

while [ $hour -lt 24 ]
do

	#pad out the syntax
        if [ $hour -lt 10 ]
        then
                pad_hour=`echo "0"$hour`
        else
                pad_hour=$hour
        fi

	#wrap report generator script
	/group_workspaces/cems2/slstr_cpa/software/slstr_calibration/report_on_transfer.sh /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/S3C/DPM/ $jd $pad_hour /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/transfer_logs/DPM

	/group_workspaces/cems2/slstr_cpa/software/slstr_calibration/report_on_transfer.sh /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/S3C/ICM/ $jd $pad_hour /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/transfer_logs/ICM

	hour=`expr $hour + 1`
done

