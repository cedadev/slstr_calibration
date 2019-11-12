#!/bin/bash

export model=$1

export config_file=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_level0_$model'.cfg'
export lockfile=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/level0_data/level0_lock.txt
export output_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/level0_data/
export log_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/level0_data/logs/

echo [default] >$config_file
echo #general connection details etc >>$config_file
echo ftp_host: ftp.acri-cwa.fr >>$config_file
echo ftp_user: ftp_s3mpc-SL0-${model:(-1)} >>$config_file
if [ $model == S3A ]
then
  echo ftp_pw: 'usfTG654$*'  >>$config_file
fi
if [ $model == S3B ]
then
  echo ftp_pw: 'zzfTD54!%'  >>$config_file
fi
echo check_days: False >>$config_file
echo check_days_num: 50 >>$config_file
echo log_dir: $log_dir >>$config_file
echo email_alerts:  >>$config_file
echo lockfile: $lockfile >>$config_file
echo >>$config_file

for days_ago in {0..8}
do
   export month=`date -d $days_ago' days ago' +%m`
   export year=`date -d $days_ago' days ago' +%Y`
   export day=`date -d $days_ago' days ago' +%d`
   echo [L0_MPC0$days_ago] >>$config_file
   echo ftp_server_path: /$year$month$day >>$config_file
   echo product_base: $model'_SL_0_.*LN2_O_NT.*' >>$config_file
   echo local_path: $output_dir >>$config_file
   echo >>$config_file
done

