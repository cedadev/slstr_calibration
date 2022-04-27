#!/bin/sh

#script to generate a report overview of all data identified from the manifest checking scripts
if [ $# != 1 ]
then
	echo "Usage <type: DPM|ICM>"
	exit
fi

type=$1

year="2020"
cnt=1
#/gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/incoming_report/ICM/daily_manifest
report_dir=`echo "/gws/nopw/j04/slstr_cpa/incoming/${type}/daily_manifest/"`
report_overview=`echo "${report_dir}/all_days_overview_${type}.txt"`

create_backuplist=`echo "${report_dir}/backup_tar_${type}.txt"`

if [ -f $create_backuplist ]
then
	rm $create_backuplist
fi

if [ -f $report_overview ] 
then
	rm $report_overview
fi

backupbasedir="/gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/backup/S3C/"

echo -e "Year: ${year}\tType: ${type}" > $report_overview
echo -e "\n\nKey:\n\tE = Empty Manifest file\n\tN = No data generated\n\n" >> $report_overview
echo -e "JD\tTotal\tMissing(inc)\tMissing md5 (inc)\tMissing(trg)\t Missing md5 (trg)\tBackedup?\n" >> $report_overview

datcnt=0
while [ $cnt -le 366 ]
do
	#don't forget to clear the numbers reported...
	totalgen="0"
	num_inc="0"
	num_incmd5="0"
	num_trg="0"
	num_trgmd5="0"
	backedup="FALSE"

	#calculate the JD
	if [ $cnt -lt 100 ]
	then
		if [ $cnt -lt 10 ]
		then
			jd=`echo "00${cnt}"`
		else
			jd=`echo "0${cnt}"`

		fi
	else
		jd=`echo "${cnt}"`
	fi

	#predict what the backup name is
	backuptarfile=`echo "${backupbasedir}/${type}/${year}_${jd}_${type}.tar.gz"`

	if [ -f $backuptarfile ]
	then
		backedup="TRUE"
	fi

	#work out report filename
	report_inc=`echo "${report_dir}/${year}_${jd}_${type}_daily_manifest.txt.report.incoming"`
	report_trg=`echo "${report_dir}/${year}_${jd}_${type}_daily_manifest.txt.report.target"`

	if [ -f $report_inc ]
	then
		echo "Checking ${report_inc}"

		data_triple_inc=`head -1 $report_inc |  awk '{print $1}' | tr ':' '\t'`
		data_triple_incmd5=`head -1 $report_inc |  awk '{print $2}' | tr ':' '\t'`
        	num_inc=`echo $data_triple_inc | awk '{print $2}'`
        	num_incmd5=`echo $data_triple_incmd5 | awk '{print $2}'`

		totalgen=`echo $data_triple_inc | awk '{print $4}'`
	fi

	if [ -f $report_trg ]
	then
		echo "Checking ${report_trg}"
		data_triple_trg=`head -1 $report_trg |  awk '{print $1}' | tr ':' '\t'`
		data_triple_trgmd5=`head -1 $report_trg |  awk '{print $2}' | tr ':' '\t'`
        	num_trg=`echo $data_triple_trg | awk '{print $2}'`
        	num_trgmd5=`echo $data_triple_trgmd5 | awk '{print $2}'`

		totalgen=`echo $data_triple_trg | awk '{print $4}'`
	fi

	#only report if something for that day..
	if [ "${totalgen}" = "" ]
	then 
		totalgen="0"
	fi

	#put a warning in case there is data but NO backup!
        if [ ! -f $backuptarfile ] && [ "$totalgen" != "0" ]
        then
                backedup="**FALSE**"
        fi

	if [ -f $report_inc ] && [ -f $report_trg ]
	then
		datcnt=`expr $datcnt + 1`
		echo -e "${jd}\t${totalgen}\t${num_inc}\t${num_incmd5}\t${num_trg}\t${num_trgmd5}\t${backedup}" >>  $report_overview

		#create list we can use for generating bulk backups
		if [ "$num_trg" = "0" ]
		then
			echo $report_trg >> $create_backuplist
		fi
	fi
	cnt=`expr $cnt + 1`

done

cp $report_overview /gws/nopw/j04/slstr_cpa/public/s3c_ground_calibration/.

echo "Have processed ${datcnt} report files"
echo -e "\n\nHave processed ${datcnt} report files\n\n"  >>  $report_overview
if [ -f $report_overview ] 
then
	echo "Have generated report at: ${report_overview}"
else
	echo "Failed to generate report (${report_overview})"
fi

if [ -f $create_backuplist ]
then
	echo "List of files to use with create_tar.sh: ${create_backuplist}"
fi
