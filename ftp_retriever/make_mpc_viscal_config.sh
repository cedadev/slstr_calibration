#!/bin/bash

export model=$1

export config_file=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_viscal_$model'.cfg'
export lockfile=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/vsc_ax/viscal_lock.txt
export output_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/vsc_ax/
export log_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/vsc_ax/logs/

echo [default] >$config_file
echo #general connection details etc >>$config_file
echo ftp_host: ftp.acri-cwa.fr >>$config_file
echo ftp_user: ftp_s3mpc-opt >>$config_file
echo ftp_pw: 'dgt456!!'  >>$config_file
echo check_days: True >>$config_file
echo check_days_num: 20 >>$config_file
echo log_dir: $log_dir >>$config_file
echo email_alerts:  >>$config_file
echo lockfile: $lockfile >>$config_file
echo >>$config_file

for days_ago in {0..5}
do
   export month=`date -d $days_ago' days ago' +%m`
   export year=`date -d $days_ago' days ago' +%Y`
   export day=`date -d $days_ago' days ago' +%d`
   echo [L1_viscal$days_ago] >>$config_file
   echo ftp_server_path: ADFs/all_current_ADFs/$year$month$day >>$config_file
   echo product_base: $model'_SL_1_VSC_' >>$config_file
   echo local_path: $output_dir >>$config_file
   echo >>$config_file
done

