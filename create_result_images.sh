#!/bin/bash

for ((i=0; i <=425; i++))
do
  echo "Running job $i"
  python3 horizontal_compress.py $i
done
