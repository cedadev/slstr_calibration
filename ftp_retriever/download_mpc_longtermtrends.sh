#!/bin/bash

export model=$1

export base_directory=/group_workspaces/cems2/slstr_cpa/public/$model'_monitoring_MPC'/
export longtermtrend_dir=$base_directory'long_term_trends'

if [ ! -d $longtermtrend_dir ]; then
  mkdir -p $longtermtrend_dir
else
  rm -rf $longtermtrend_dir
  mkdir -p $longtermtrend_dir
fi
chmod g+w $longtermtrend_dir


export temp_mon_list=$base_directory/temp_ltt_filelist.txt
export remote_dir=SL_0_monitoring_ope/$model'_monitoring/long_term_trends/'

/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mon_$model.cfg -vL  -p $remote_dir > $temp_mon_list

#export date_directory=$base_directory/$data_type/$process_date

#if [ ! -d $date_directory ]; then
#  mkdir -p $date_directory
#fi
#chmod g+w $date_directory

export temp_config=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mpc_mon_temp_$model.cfg
export temp_log_dir=$base_directory/logs_tmp/

export remote_len=${#remote_dir}

while read -r line; do 
   echo $line
   export id=`expr substr $line $((remote_len+1)) 150`
   echo $id   
   if [[ "$id" =~ ".csv" ]]; then
      echo 'downloading csv file'
   else
      echo $longtermtrend_dir/$id
      if [ ! -d $longtermtrend_dir/$id ]; then
         mkdir -p $longtermtrend_dir/$id
      fi
   fi
   echo [default] >$temp_config
   echo #general connection details etc >>$temp_config
   echo ftp_host: ftp.acri-cwa.fr >>$temp_config
   echo ftp_user: ftp_s3mpc-esl >>$temp_config
   echo ftp_pw: rM15Nv5p  >>$temp_config
   echo check_days: False >>$temp_config
   echo check_days_num: 1000 >>$temp_config
   echo log_dir: $temp_log_dir >>$temp_config
   echo email_alerts:  >>$temp_config
   echo lockfile: $base_directory/mpc_mon_lock_temp.txt>>$temp_config
   echo >>$temp_config
   echo [L1_MPC01] >>$temp_config
   if [[ "$id" =~ ".csv" ]]; then
      echo ftp_server_path: $remote_dir >>$temp_config
      echo product_base: $id >>$temp_config
      echo local_path: $longtermtrend_dir >>$temp_config
   elif [[ "$id" =~ "count_histogram" ]]; then
      if [ ! -d $longtermtrend_dir/count_histogram/nadir_view ]; then
         mkdir -p $longtermtrend_dir/count_histogram/nadir_view
      fi
      echo ftp_server_path: $remote_dir/count_histogram/nadir_view >>$temp_config
      echo product_base:  >>$temp_config
      echo local_path: $longtermtrend_dir/count_histogram/nadir_view >>$temp_config
      for i in {0..92} ; do
         /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
      done
      if [ ! -d $longtermtrend_dir/count_histogram/oblique_view ]; then
         mkdir -p $longtermtrend_dir/count_histogram/oblique_view
      fi
      echo ftp_server_path: $remote_dir/count_histogram/oblique_view >>$temp_config
      echo product_base:  >>$temp_config
      echo local_path: $longtermtrend_dir/count_histogram/oblique_view >>$temp_config
      for i in {0..92} ; do
         /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
      done
   else 
      echo ftp_server_path: $remote_dir/$id >>$temp_config
      echo product_base:  >>$temp_config
      echo local_path: $longtermtrend_dir/$id >>$temp_config
      /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
      /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
      /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   fi
   /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   # clear log directory
   rm $temp_log_dir/*_retrieve.log
done < <(sed -e 1,6d $temp_mon_list) 
