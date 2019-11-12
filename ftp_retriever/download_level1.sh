#!/bin/bash

export month=06
export year=2018
export model=S3B

export day=13

#for day in {01..15}
#do
echo $year$month$day

export process_date=$year$month$day
export temp_list=/group_workspaces/cems2/slstr_cpa/S3A_test_data/tandem_data_S7_S8_tests/temp_filelist.txt

/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_tandem_s7_s8_level1.cfg -v -L -p RAL/S3MPC-3356/$process_date/$model > $temp_list

export date_directory=/group_workspaces/cems2/slstr_cpa/S3A_test_data/tandem_data_S7_S8_tests/$process_date/$model/


export temp_config=/group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mpc_tandem_temp.cfg
export output_dir=/group_workspaces/cems2/slstr_cpa/S3A_test_data/tandem_data_S7_S8_tests/
export temp_log_dir=/group_workspaces/cems2/slstr_cpa/S3A_test_data/tandem_data_S7_S8_tests/


while read -r line; do 
   echo $line
   export id=`expr substr $line 29 253`
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
   echo lockfile: /group_workspaces/cems2/slstr_cpa/S3A_test_data/tandem_data_S7_S8_tests/lock_temp.txt>>$temp_config
   echo >>$temp_config
   echo [L1_MPC01] >>$temp_config
   echo ftp_server_path: RAL/S3MPC-3356/$process_date/$model/$id >>$temp_config
   echo product_base: >>$temp_config
   echo local_path: $output_dir/$process_date/$model/$id >>$temp_config
   echo making new directory $output_dir/$process_date/$model/$id 
   mkdir $output_dir/$process_date/$model/$id
   #for i in {0..111} 
   #do   
   #  /usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF
   #done
   #/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF 
   #/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF 
   #/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c $temp_config -vF 
   # clear log directory
   #rm $temp_log_dir/*_retrieve.log
   #ls $output_dir/$process_date/*.txt
   #mv $output_dir/$process_date/*.txt $output_dir/$process_date/$id/.
done < <(sed -e 1,6d $temp_list) 
#done
