#!/bin/bash

shopt -s nullglob
rm -fv testfile?
sleep 5

while true
do
    for I in $(seq 3)
    do
        for J in $(seq 5)
        do
            TEXT="$I $J $(date)"
            FILE="testfile$I"
            echo $TEXT
            echo $TEXT >> $FILE
            sleep 1
        done
    done
done
