#!/bin/bash

#export month='05'
export year='2018'
export timeliness=NT
export model=S3A

#export day=`date -d '4 days ago' +%d`

for month in {01..12}
do
for day in {01..31}
do

echo $year$month$day

export process_date=$year$month$day
export base_directory=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/geocal/geocal_reproc_v007/

#export temp_geocal_list=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/phase_E1/data/MPC/OPTICAL/GEOCAL/temp_geocal_filelist.txt
export temp_geocal_list=$base_directory/temp_geocal_filelist.txt

/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mpc_geocal_reproc_$model.cfg -v -L -p SIIIMPC-3296_GEOCAL_SLSTR_A_REP_GEC_V007/V007_SVAL/$model/SLSTR/$timeliness/$process_date > $temp_geocal_list

#export date_directory=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/phase_E1/data/MPC/OPTICAL/GEOCAL/SLSTR/$timeliness/$process_date
export date_directory=$base_directory/$year/$month/$day

if [ ! -d $date_directory ]; then
  mkdir -p $date_directory
fi
chmod g+w $date_directory

export temp_config=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mpc_geocal_temp_reproc_$model.cfg
#export output_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/phase_E1/data/MPC/OPTICAL/GEOCAL/SLSTR/$timeliness
#export output_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/flight/geocal
#export temp_log_dir=/group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/phase_E1/data/MPC/geocal_logs/
export temp_log_dir=$base_directory/logs_tmp/

count=0
while read -r line; do
   #echo $line
   count=$(($count+1))
   export id=`expr substr $line 74 150`
   echo $id   
   echo [default] >$temp_config
   echo #general connection details etc >>$temp_config
   echo ftp_host: ftp.acri-cwa.fr >>$temp_config
   echo ftp_user: ftp_s3mpc-esl >>$temp_config
   echo ftp_pw: rM15Nv5p  >>$temp_config
   echo check_days: False >>$temp_config
   echo check_days_num: 1000 >>$temp_config
   echo log_dir: $temp_log_dir >>$temp_config
   echo email_alerts:  >>$temp_config
   #echo lockfile: /group_workspaces/cems2/slstr_cpa/s3_slstr_raw_data/$model/phase_E1/data/MPC/mpc_geocal_lock_temp.txt>>$temp_config
   echo lockfile: $base_directory/mpc_geocal_lock_temp.txt>>$temp_config
   echo >>$temp_config
   echo [L1_MPC01] >>$temp_config
   echo ftp_server_path: SIIIMPC-3296_GEOCAL_SLSTR_A_REP_GEC_V007/V007_SVAL/$model/SLSTR/$timeliness/$process_date/$id >>$temp_config
   echo product_base: >>$temp_config
   echo local_path: $date_directory/$id >>$temp_config
   echo making new directory $date_directory/$id
   mkdir $date_directory/$id
   /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   # clear log directory
   rm $temp_log_dir/*_retrieve.log
done < <(sed -e 1,6d $temp_geocal_list) 

if [ $count -eq 0 ]; then
  rmdir $date_directory
fi

done
done
