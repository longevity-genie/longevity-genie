#!/bin/bash

# Read URLs from file line by line
while IFS= read -r line
do
    # Extract the filename
    filename=$(echo $line | awk -F'/' '{print $NF}' | awk -F'?' '{print $1}')

    # Download file with wget, -nc prevents re-downloading existing files
    wget -nc -O $filename "$line"
done < files.txt