#!/bin/bash

## Note:
# Use this script only, if you have legal rights to open pdf
# Eg. If you have forgotten password.

GS=`which gs`
[ "$GS" = "" ] && echo "Install GhostScript" && exit 1

if [ "$1" != "" ] && [ "$2" != "" ]
then
	gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$1" -c .setpdfwrite -f  "${2}"
else
	echo "Usage $0 input.pdf output.pdf"
fi
