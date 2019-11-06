#!/bin/sh

#Script to move incoming SLSTR test data to a directory accessible by others in the slstr_cpa gws

#Steve Donegan x8123 Feb 2015


#Functions

function makedir (){
	mkdir -p $1

	#if this job run as cron on aatsr_services then need to make sure permissions are ok for users
	current_user=`whoami`

	if [ $current_user = "root" ]
	then
		chown -R root:users $1
	fi
}

function checkMD5 {
	#Function to compare md5 of actual file ($2) against a stated value ($1)

	#default is NOT a match and return 0, if it matches it will be 1
	#local md5match=0
	md5_from_md5file=`head -1 $1 | awk '{print $1}'`
	md5_of_file=`md5sum $2 | awk '{print $1}'`

	#echo "md5 from md5file"$md5_from_md5file
	#echo "md5 of file:"$md5_of_file

	if [ $md5_from_md5file = $md5_of_file ]
	then
		echo 1
	else
		echo 0
	fi

}


##################### MAIN ####################

starttm=`date +"%y-%m-%dT%H:%M:%S"`

if [ $# != 3 ]
then
	echo "Usage: <source filename> <target directory> <log directory> "
	#exit
fi

source_filename=$1
filename=`basename $source_filename`
dest_base_dir=$2
log_dir=$3

if [ ! -d $log_dir ]
then
	echo "No directory: $log_dir"
	exit
else
	logfile_name=`date +"%Y_%j_%H_%M.log"`
 	logfile=`echo $log_dir"/"$logfile_name`
	#touch $logfile
fi

#step 1: check that there is an equivalent md5 file
source_filename_md5=`echo $source_filename".md5"`
filename_md5=`basename $source_filename_md5`

if [ ! -f $source_filename ]
then
        endtm=`date +"%y-%m-%dT%H:%M:%S"`
	#just print this to stdout - will get a lot of these records..
        #echo "ERROR ($starttm $endtm): There is no such file: $source_filename" >> $logfile 
        exit
else
	#if file exists so we can generate a log file!
	#does logfile exist?
	if [ ! -f $logfile ]
	then
		touch $logfile
	fi
fi

if [ ! -f $source_filename_md5 ]
then
	endtm=`date +"%y-%m-%dT%H:%M:%S"`
	echo "ERROR ($starttm $endtm): There is no md5 file for: $source_filename" >> $logfile
	exit
fi

#step 2: check that the md5 matches the data file
#note no output on this as this will happen a lot
#md5=`tail -1 $source_filename_md5 | awk '{print $1}'`
#md5offile=`md5sum $source_filename| awk '{print $1}'`
#echo "md5: $md5 actual: $md5offile"
#md5_check=`checkMD5 $source_filename_md5 $source_filename`
#echo "md5check: $md5check"
if [ `checkMD5 $source_filename_md5 $source_filename` = 0 ]
then
	#finish quietly, this just means the file has not finished transferring
	exit
fi

#step 3: work out the destination directory
year=`echo $filename | cut -c 1-4`
jd=`echo $filename | cut -c 6-8`
hour=`echo $filename | cut -c 10-11`
min=`echo $filename | cut -c 13-14`

dest_dir=`echo "$dest_base_dir/$jd/$hour/$min"`

#step 4: if the target directory does not exist, create it
if [ ! -d $dest_dir ]
then
	makedir $dest_dir
fi

#check again, if it's still not there then throw an error!
if [ ! -d $dest_dir ]
then
	endtm=`date +"%y-%m-%dT%H:%M:%S"`
	echo -e "ERROR ($starttm $endtm): could not make directory: $dest_dir" >> $logfile
	exit
fi


#step 5: is the file already in the target directory?
#dest_dir_filename=`echo $dest_dir"/"$filename`
if [ -f `echo $dest_dir"/"$filename` ]
then
	#echo "$filename is in $dest_dir"
	exit
else
	#echo "$filename is not in $dest_dir so copying it across"

	cp $source_filename $dest_dir
	cp $source_filename_md5 $dest_dir
fi

#check files did indeed make it over
dest_filename=`echo $dest_dir"/"$filename`
dest_filename_md5=`echo $dest_dir"/"$filename_md5`

if [ -f $dest_filename ] && [ -f $dest_filename_md5 ]
then
	#echo "$filename transferred successfully"

	#now md5 check the transferred file
	if [ `checkMD5 $dest_filename_md5 $dest_filename` = 1 ]
	then
		endtm=`date +"%y-%m-%dT%H:%M:%S"`
		echo -e "SUCCESS ($starttm $endtm): moved $filename to $dest_dir" >> $logfile
	fi	
else
	endtm=`date +"%y-%m-%dT%H:%M:%S"`
	echo -e "ERROR ($starttm $endtm): unsuccessful transfer of: $filename (md5 at destination does not match)" >> $logfile
fi



#step 6: remove files from incoming area?


#echo -e "Start: $starttm \nEnd: $endtm"
