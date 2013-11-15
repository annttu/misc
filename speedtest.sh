#!/bin/bash

function help {
	echo "Usage: $0 [interface]"
	exit 0
}

function error {
	echo $1
	exit 1
}

function scale {
	speed=$1
	if [ ${#speed} -ge 10 ]
	then
		prettyspeed="`echo "scale=2; $speed / 1024 / 1024 * 8" |bc -l`"
		printf '%3.2f Mb/s' $prettyspeed
	else
		prettyspeed="`echo "scale=2; $speed / 1024 * 8" |bc -l`"
		printf '%3.2f Kb/s' $prettyspeed
	fi
}

function download {
	[ -n "$1" ] || error "No size given"
	size="$1"
	speed="`curl  -s http://data.kapsi.fi/${size} -w "%{speed_download}" $opts -o /dev/null`"
	[ $? -ne 0 ] && error "Curl exit code nonzero"
	echo $speed
	return 0
}

function upload {
	[ -n "$1" ] || error "No size given"
	size="$1"
	dd if=/dev/zero of=/tmp/${size}M bs=${size}m count=1 > /dev/null 2>&1
	upload="`curl -s http://data.kapsi.fi/ --data-binary @/tmp/${size}M -w "%{speed_upload}" $opts -o /dev/null`"
	echo "$upload"
	rm /tmp/${size}M
}

[ "$1" == "--help" ] && help
[ "$1" == "-h" ] && help

if [ "$1" != "" ]
then
	ifconfig |grep "${1}:" > /dev/null 2>&1
	[ $? -ne 0 ] && error "Invalid interface"
	opts="--interface $1"
fi

speed=0
for size in "1M" "10M" "100M" "1G"
do
	time1=`date +%s`
	echo "Downloading $size packet"
	speed="`download ${size}`"
	time2=`date +%s`
	tdiff=$(($time2 - $time1))
	[ $tdiff -ge 3 ] && break
done

# Test upload speed

upload=0
upload_size=10
while true
do
	time1=`date +%s`
	echo "Uploading ${upload_size}M packet"
	upload="`upload ${upload_size}`"
	time2=`date +%s`
	tdiff=$(($time2 - $time1))
	[ $tdiff -ge 5 ] && break
	if [ $tdiff -ge 3 ]
	then
		upload_size=$(($upload_size * 2))
		continue
	elif [ $tdiff -ge 2 ]
	then
		upload_size=$(($upload_size * 5))
	else
		upload_size=$(($upload_size * 10))
	fi
done

# Pretty print speed
echo "Down: `scale ${speed}`"
echo "Up:   `scale ${upload}`"
