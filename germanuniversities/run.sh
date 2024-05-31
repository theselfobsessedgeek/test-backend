#!/bin/bash

UNIVHOME="/home/kapilsharma/www/germanuniversities"
echo "Running python Script to find German Universities"
ps aux --sort -rss | grep python
############ Number of Universities Found till now
cd "$UNIVHOME/univdir"
echo "Nunber of Universities Found till now"
ls | wc -l
#cd /home/kapilsharma/www/germanuniversities
cd $UNIVHOME
pwd
nohup python /home/kapilsharma/www/germanuniversities/university.py > error.log &
