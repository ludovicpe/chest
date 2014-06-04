#!/bin/bash
#NUMCPU="`cat /proc/cpuinfo | grep ^processor | wc -l`" 

NUMCPU="1"

find . -type f -regextype posix-awk -iregex '.*\.aac' | while read i ; do
       if [ `jobs -p | wc -l` -ge $NUMCPU ] ; then
               wait
       fi
       TEMP="${i%.*}.mp3"
       OUTF=`echo "$TEMP" | sed 's#\(.*\)/\([^,]*\)#\1/\2#'`
       if [ ! -e "$OUTF" ] ; then
               avconv -i "$i"  -vn -acodec libmp3lame -aq 0 "$OUTF" 
               if [ -e "$OUTF" ] ; then
	               rm "$i"
	       fi
       fi 
done
