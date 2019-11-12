#!/bin/bash

export model=$1
export year=$2
export month=$3
export day=$4

echo $year$month$day

export process_date=$year$month$day

export base_directory=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/vsc_ax

export temp_viscal_list=$base_directory/temp_viscal_filelist.txt

/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_viscal_$model.cfg -v -L -p ADFs/all_current_ADFs/$process_date > $temp_viscal_list


#export date_directory=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/phase_E1/data/MPC/OPTICAL/GEOCAL/SLSTR/$timeliness/$process_date
export date_directory=$base_directory/$year/$month/$day

if [ ! -d $date_directory ]; then
  mkdir -p $date_directory
fi
chmod g+w $date_directory

export temp_config=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mpc_viscal_temp_$model.cfg
export temp_log_dir=$base_directory/logs_tmp/

while read -r line; do 
   #echo $line
   export id=`expr substr $line 32 150`
   echo $id   
   echo [default] >$temp_config
   echo #general connection details etc >>$temp_config
   echo ftp_host: ftp.acri-cwa.fr >>$temp_config
   echo ftp_user: ftp_s3mpc-opt >>$temp_config
   echo ftp_pw: dgt456!!  >>$temp_config
   echo check_days: False >>$temp_config
   echo check_days_num: 1000 >>$temp_config
   echo log_dir: $temp_log_dir >>$temp_config
   echo email_alerts:  >>$temp_config
   echo lockfile: $base_directory/mpc_viscal_lock_temp.txt>>$temp_config
   echo >>$temp_config
   echo [L1_MPC01] >>$temp_config
   echo ftp_server_path: ADFs/all_current_ADFs/$process_date/$id >>$temp_config
   echo product_base:  >>$temp_config
   echo local_path: $date_directory/$id >>$temp_config
   echo making new directory $date_directory/$id
   mkdir $date_directory/$id
   /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   # clear log directory
   rm $temp_log_dir/*_retrieve.log
done < <(sed -e 1,6d $temp_viscal_list) 
