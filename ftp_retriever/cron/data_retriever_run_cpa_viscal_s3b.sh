#!/bin/sh

#/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_viscal_s3b.cfg   -ve >/dev/null 2>&1

#/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/make_mpc_viscal_config.sh S3B

#/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_viscal_S3B.cfg   -ve >/dev/null 2>&1

for days_ago in {0..5}
do
   export month=`date -d $days_ago' days ago' +%m`
   export year=`date -d $days_ago' days ago' +%Y`
   export day=`date -d $days_ago' days ago' +%d`
   /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/download_viscal.sh S3B $year $month $day
done
