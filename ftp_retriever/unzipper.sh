#!/bin/sh

#Script to find new zip files, check and extract and delete bad ones

top_level_dir=$1

for roi in `grep local_path ${top_level_dir}  | awk '{print $2}'`
do
	cnt=0
	for zipfile in `find ${roi} -name "*.zip" -print`
	do
		opdir=`dirname ${zipfile}`

		zip_status=`zip -T ${zipfile}`

		status=`echo $zip_status | awk '{print $NF}'`

		if [ $status == "OK" ]
		then
        		echo "${zipfile}: good"

			#unzip the zipfile
			unzip -q ${zipfile} -d ${opdir}

			unzippeddir=`basename ${zipfile} | sed 's/zip/SEN3/g'`			
			outputzipdir=`echo "${opdir}/${unzippeddir}"`
			
			#remove the original zipfile
			if [ -d ${outputzipdir} ]
			then
				rm -f ${zipfile}
			else
				echo "Problem extracting ${zipfile}"
			fi
		else
	       		echo "${zipfile}: bad"
			rm -f ${zipfile}
		fi

		cnt=`expr $cnt + 1`
	done
	echo "Found ${cnt} zipfiles in ${roi}"
done
