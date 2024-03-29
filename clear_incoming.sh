#!/bin/sh

#Script to look at simple report file generated by manifest checker - if zero missing files found in incoming directory it will  clear files for that day

if [ $# != 2 ]
then
	echo "Usage: <incoming report file> <target report file>"
	exit
fi

incoming_report=$1
target_report=$2

#check that it really is an inooming report and not a target report
filetype=`basename $incoming_report | tr '.' '\t' | awk '{print $NF}'`
filetypetrg=`basename $target_report | tr '.' '\t' | awk '{print $NF}'`
year_day=`basename $incoming_report | cut -c1-8`

#data type
type=`basename $incoming_report | tr '_' '\t' | awk '{print $3}'`

backupbasedir="/gws/nopw/j04/slstr_cpa/s3_slstr_raw_data/backup/S3C/"

#predict what the backup name is
backuptarfile=`echo "${backupbasedir}/${type}/${year_day}_${type}.tar.gz"`

if [ "$filetype" != "incoming" ] 
then
	echo "Please ensure first arguement is an incoming report"
	exit
fi

if [ "$filetypetrg" != "target" ]
then
        echo "Please ensure the second arguement a target report"
        exit
fi

#work out the parameters from the file
if [ -f $incoming_report ]
then
	#data
	data_triple=`head -1 $incoming_report |  awk '{print $1}' | tr ':' '\t'`
	data_triple_trg=`head -1 $target_report |  awk '{print $1}' | tr ':' '\t'`

	type=`echo $data_triple | awk '{print $1}'`
	num=`echo $data_triple | awk '{print $2}'`
	dir=`echo $data_triple | awk '{print $3}'`
	tot=`echo $data_triple | awk '{print $4}'`

	num_trg=`echo $data_triple_trg | awk '{print $2}'`
	tot_trg=`echo $data_triple_trg | awk '{print $4}'`
	
	if [ "$num" = "0" ] && [ "$num_trg" = "0" ]
	then
		numfilestobedeleted=`find $dir -name "${year_day}*.ArcRaw*" -print | wc -l`

		if [ "$numfilestobedeleted" = "0" ]
		then
			echo "ERROR: There are NO files to be deleted for $year_day"
			exit
		fi

		if [ "$numfilestobedeleted" != `expr $tot + $tot_trg` ]
		then
			echo "ERROR! Total number of files in directory to be deleted (${numfilestobedeleted}) does not match the reported total(${tot} + ${tot_trg})"
		else

			#make sure there is a backup tar file..
			if [ -f $backuptarfile ]
			then
				#files should be ok to delete
				echo "Preparing to delete $numfilestobedeleted for $year_day..."
				command=`find $dir -name "${year_day}*.ArcRaw*" -exec rm -r {} \;`
				echo $command

			else
				echo "ERROR! There is no backup tar file ready so will not delete the data!"
				exit
			fi
		fi
	else
		echo -e  "ERROR: Cannot delete as report values do not match! (Number in incoming = ${num}; number in target = ${num_trg})"
	fi
else
	echo "${incoming_report} does not exist"
	exit
fi
