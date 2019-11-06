#!/bin/sh

#Script to check every entry in a manifest file (with windows path notation) and to report whether file is present in destination gws directory

# Steve Donegan Feb 2015

if [ $# != 4 ]
then
	echo "Usage: <manifest file> <incoming directory> <target directory> <report directory>"
	exit
fi


manifest_file=$1
incoming_dir=$2
dest_dir=$3
report_log_dir=$4

auto_report_inc=`echo "${manifest_file}.report.incoming"`
auto_report_trg=`echo "${manifest_file}.report.target"`

#check presence of manifest file
if [ ! -f $manifest_file ]
then
	echo "No manifest file exists ($manifest_file)"
	exit
fi

#how many files in total?
tot_num_files=`wc -l $manifest_file | awk '{print $1}'`

#if the file exists, does it have data in?
if [ $tot_num_files  -eq 0 ]
then
        echo "Warning: $manifest_file is empty!"
        echo -e "data:E:${dirToBackup}\tmd5:E:${dirToBackup}" > $auto_report_trg
        echo -e "data:E:${dirToBackup}\tmd5:E:${dirToBackup}" > $auto_report_inc
        exit
fi

#has data been generated?
first_line=`head -1 $manifest_file | sed -e 's/\r$//' | sed -e 's/ \{1,\}$//'`
#echo "ppp"$first_line"ppp"
if [ "$first_line" = "No Data Generated" ]
then
        echo "Warning: no data generated for this day!"

	echo -e "data:N:${dirToBackup}\tmd5:N:${dirToBackup}" > $auto_report_trg
	echo -e "data:N:${dirToBackup}\tmd5:N:${dirToBackup}" > $auto_report_inc
       	exit
fi

#outputfilename is the same as the manifestfile with ".report" added
datestamp=`date +"%Y_%j_%H_%M"`
manifest_file_name=`basename $manifest_file`
report_file_inc=`echo "${report_log_dir}/${manifest_file_name}.incoming.report.${datestamp}"`
report_file_trg=`echo "${report_log_dir}/${manifest_file_name}.target.report.${datestamp}"`

#clear out old report
if [ -f $report_file_inc ]
then
	rm -f $report_file_inc
fi
if [ -f $report_file_trg ]
then
        rm -f $report_file_trg
fi


count=0
countmd5=0
count_inc=0
countmd5_inc=0

for file in `cat $manifest_file`
do
	#echo $file
	filename=`echo -e $file | sed -e 's/\r$//' | sed 's/\\\/\t/g' | awk '{print $NF}'`
	#echo $filename
	
	#work out year, jd, hr & min
	year=`echo $filename | cut -c1-4`
	jd=`echo $filename | cut -c6-8`
        hour=`echo $filename | cut -c10-11`
	min=`echo $filename | cut -c13-14`

	#work out dir structure
	targetdir=`echo "${dest_dir}/${year}/${jd}/${hour}/${min}/"`
	dirToBackup=`echo "${dest_dir}/${year}/${jd}/"`
	targetDirFilename=`echo "${targetdir}/${filename}"`
	targetDirFilenameMd5=`echo $targetDirFilename".md5"`
	#targetDirFilenameMd5=`echo "${targetdir}/${filename}.md5"`
	#echo $targetdir
	#echo $targetDirFilename
	#echo $targetDirFilenameMd5
	#echo $targetDirFilename".md5"

	#..& for incoming
	filename_inc=`echo "${incoming_dir}/${filename}"`
	filename_incMd5=`echo "${incoming_dir}/${filename}.md5"`

	#Check the incoming directory
	if [ ! -f $filename_inc ]
	then
		echo -e "${filename} is not in ${incoming_dir}" >> $report_file_inc
		count_inc=`expr $count_inc + 1`
	fi

	if [ ! -f $filename_incMd5 ]
        then
                echo -e "${filename}.md5 is not in ${incoming_dir}" >> $report_file_inc
		countmd5_inc=`expr $countmd5_inc + 1`
        fi

	#check that they are in the target directory..
	if [ ! -f $targetDirFilename ]
	then
		echo -e "${filename} is not in ${targetdir}" >> $report_file_trg
		count=`expr $count + 1`
	fi

	if [ ! -f $targetDirFilenameMd5 ]
        then
                echo -e "${filename}.md5 is not in ${targetdir}" >> $report_file_trg
		countmd5=`expr $countmd5 + 1`
        fi
done

echo -e "\nTotal number of datafiles generated according to manifest (${manifest_file_name}): ${tot_num_files}"

#incoming data
if [ "$count_inc" != "0" ] && [ "$countmd5_inc" != "0" ]
then
	echo -e "\nFiles found missing in INCOMING directory: ${count_inc}\n(Md5 files missing: ${countmd5_inc})"
else
	echo -e "\nNo missing files (or accompanying md5 files) found in incoming directory!"	
fi

#create a report file to action later
echo -e "data:${count_inc}:${incoming_dir}:${tot_num_files}\tmd5:${countmd5_inc}:${incoming_dir}:${tot_num_files}" > $auto_report_inc

if [ -f $report_file_inc ]
then
	echo -e "Reportfile: ${report_file_inc}"
fi

#target data
if [ "$count" != "0" ] && [ "$countmd5" != "0" ]
then
	echo -e "\nFiles found missing in TARGET directory: ${count}\n(Md5 files missing: ${countmd5})"
else
	echo -e "\nNo missing files (or accompanying md5 files) found in target directory!"
fi

#create a report file to action later
echo -e "data:${count}:${dirToBackup}:${tot_num_files}\tmd5:${countmd5}:${dirToBackup}:${tot_num_files}" > $auto_report_trg

if [ -f $report_file_trg ] 
then
	echo -e "Reportfile: ${report_file_trg}"
fi

