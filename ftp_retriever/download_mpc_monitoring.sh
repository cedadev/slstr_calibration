#!/bin/bash

export model=$1
export year=$2
export month=$3
export day=$4
export data_type=$5

echo $year$month$day
echo $data_type

export process_date=$year$month$day

export base_directory=/group_workspaces/cems2/slstr_cpa/public/$model'_monitoring_MPC'/

export temp_mon_list=$base_directory/temp_mon_filelist.txt
export temp_orbit_list=$base_directory/temp_mon_orbitlist.txt

export remote_dir=SL_0_monitoring_ope/$model'_monitoring'/$data_type/$process_date

/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mon_$model.cfg -vL  -p $remote_dir > $temp_mon_list

export date_directory=$base_directory/$data_type/$process_date

if [ ! -d $date_directory ]; then
  mkdir -p $date_directory
fi
chmod g+w $date_directory

export temp_config=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mpc_mon_temp_$model.cfg
export temp_log_dir=$base_directory/logs_tmp/

export remote_len=${#remote_dir}

while read -r line; do 
   echo $line
   export id=`expr substr $line $((remote_len+2)) 150`
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
   echo lockfile: $base_directory/mpc_mon_lock_temp.txt>>$temp_config
   echo >>$temp_config
   echo [L1_MPC01] >>$temp_config
   echo ftp_server_path: $remote_dir >>$temp_config
   if [ "$data_type" == "bb_counts" ] || [ "$data_type" == "bb_temps" ] || [ "$data_type" == "viscal_counts" ]; then
      echo product_base: $id >>$temp_config
      echo local_path: $date_directory >>$temp_config
   else
      echo product_base: >>$temp_config
   fi
   if [ "$data_type" == "bb_counts" ] || [ "$data_type" == "bb_temps" ] || [ "$data_type" == "viscal_counts" ]; then
      /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   else
      if [ ! -d $date_directory/$id ]; then
         cp $temp_config $temp_config.thumb
         echo local_path: $date_directory/$id >>$temp_config
         mkdir $date_directory/$id
         mkdir $date_directory/$id/thumbnails
         echo local_path: $date_directory/$id/thumbnails >>$temp_config.thumb
         /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vFL -p $remote_dir/$id > $temp_orbit_list
         while read -r line; do
            /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF -p $remote_dir/$id
         done < <(sed -e 1,6d $temp_orbit_list) 
         /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config.thumb -vFL -p $remote_dir/$id/thumbnails > $temp_orbit_list
         while read -r line; do
            /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config.thumb -vF -p $remote_dir/$id/thumbnails
         done < <(sed -e 1,6d $temp_orbit_list)
      fi 
  fi
   # clear log directory
   rm $temp_log_dir/*_retrieve.log
done < <(sed -e 1,6d $temp_mon_list) 
