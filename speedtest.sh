#!/bin/bash

function help {
	echo "Usage: $0 [interface]"
	exit 0
}

function error {
	echo $1
	exit 1
}

[ "$1" == "--help" ] && help
[ "$1" == "-h" ] && help

if [ "$1" != "" ]
then
	ifconfig |grep "${1}:" > /dev/null 2>&1
	[ $? -ne 0 ] && error "Invalid interface"
	opts="--interface $1"
fi

time1=`date +%s`
speed="`curl  -s http://annttu.fi/10M -w "%{speed_download}" $opts -o /dev/null`"
[ $? -ne 0 ] && error "Curl exit code nonzero"
time2=`date +%s`

tdiff=$(($time2 - $time1))


if [ $tdiff -lt 3 ]
then
	# that was quick, test with bigger packet
	speed="`curl  -s http://annttu.fi/10M -w "%{speed_download}" $opts -o /dev/null`"
fi
# Pretty print speed
if [ ${#speed} -ge 11 ]
then
	prettyspeed="`echo "scale=2; $speed / 1024 / 1024 / 8" |bc -l`"
	printf '%3.2f MB/s\n' $prettyspeed
else
	prettyspeed="`echo "scale=2; $speed / 1024 / 8" |bc -l`"
	printf '%3.2f KB/s\n' $prettyspeed
fi
