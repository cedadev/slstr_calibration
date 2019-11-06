#!/bin/sh

#Script to report on files based on a given hour minute etc

#NOTE - if an "A" is supplied instead of a number for JD, hour or minute this will be treated as a wildcard


######### FUNCTIONS ##########


########## MAIN ##############
if [ $# != 4 ]
then
	echo "Usage: JD Hour Min SourceDir" 
	exit
fi

jd=$1
hour=$2
min=$3
source_dir=$4

year="2015"

search_string=`echo $year"_"$jd"_"$hour"_"$min`
search_string=`echo $search_string | sed 's/A/\*/g'`
search_string=`echo $search_string"*.ArcRaw"`
search_string_md5=`echo $search_string".md5"`

echo "Searching for files with pattern: $search_string"
#files_to_move=`find $source_dir -name ${search_string} -print`
num_data_files=`find $source_dir -type f -name ${search_string} -print | wc -l`
num_data_md5files=`find $source_dir -type f -name ${search_string_md5} -print | wc -l`

echo -e "Files for pattern; $search_string = $num_data_files"
echo -e "Files for pattern; $search_string_md5 = $num_data_md5files"

#identify missing files...
if [ $num_data_md5files -lt $num_data_files ]
then
	echo "There are missing md5 files!"

	for file in `find $source_dir -type f -name ${search_string} -print`
	do
		md5_equiv=`echo $file".md5"`
		if [ ! -f $md5_equiv ]
		then
			echo "There is no md5 file for: $file"
		fi
	done
fi

if [ $num_data_md5files -gt $num_data_files ]
then
        echo "There are missing datafiles!"
	for file in `find $source_dir -type f -name ${search_string_md5} -print`
        do
                data_equiv=`echo $file | cut -d\. -f1-2`
                if [ ! -f $data_equiv ]
                then
                        echo "There is no equivalent data file for: $file"
                fi
        done
fi



