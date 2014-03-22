#!/bin/bash
#NUMCPU="`cat /proc/cpuinfo | grep ^processor | wc -l`" 

NUMCPU="1"

find . -type f -regextype posix-awk -iregex '.*\.flac' | while read i ; do
       if [ `jobs -p | wc -l` -ge $NUMCPU ] ; then
               wait
       fi
       TEMP="${i%.*}.ogg"
       OUTF=`echo "$TEMP" | sed 's#\(.*\)/\([^,]*\)#\1/\2#'`
       if [ ! -e "$OUTF" ] ; then
               oggenc "$i" -b 256 -o "$OUTF" 
               if [ -e "$OUTF" ] ; then
	               rm "$i"
	       fi
       fi 
done
