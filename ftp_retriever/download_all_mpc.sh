#!/bin/bash
# get todays date

export model=$1

copy_completed=$(/usr/bin/python2.7 /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/data_retriever.py -c /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/config/slstr_cpa_mon_$model.cfg -vL | grep is_finished)

echo $copy_completed

if [[ "$copy_completed" =~ "is_finished" ]]; then

  # loop over the last 5 days
  for dayago in {5..0}
  do

    export month=`date -d $dayago' days ago' +%m`
    export year=`date -d $dayago' days ago' +%Y`
    export day=`date -d $dayago' days ago' +%d`

    #call the scripts in turn
    echo $model $year $month $day $year
    /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/download_mpc_monitoring.sh $model $year $month $day $year
    /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/download_mpc_monitoring.sh $model $year $month $day bb_counts
    /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/download_mpc_monitoring.sh $model $year $month $day bb_temps
    /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/download_mpc_monitoring.sh $model $year $month $day viscal_counts

  done

  /group_workspaces/cems2/slstr_cpa/software/ftp_retriever/download_mpc_longtermtrends.sh $model
fi
