#!/bin/bash

# Iterate over all the files in the current directory
for file in *
do
    # Check if the file contains a '.gz?'
    if [[ $file == *'.gz?'* ]]; then
        # Remove everything after '.gz' (including '?')
        new_file="${file%%.gz*}.gz"

        # Rename the file
        mv -- "$file" "$new_file"
    fi
done