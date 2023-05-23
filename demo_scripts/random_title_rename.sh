#!/bin/bash

cd taw/

# Iterate over the files
for file in */*; do
  # Check if it is a file with the .md extension
  if [ -f "$file" ] && [[ "$file" == *.md ]]; then
    # Extract the directory from the file path
    directory=$(dirname "$file")

    # Extract the prefix of the file name (first 16 characters without including the directory name)
    prefix="${file#*/}"
    prefix="${prefix:0:16}"

    # Check if the prefix matches the date format "YYYY-MM-DD "
    if [[ "${prefix:0:11}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ $ ]]; then

	# Extract the extension of the file name
	extension="${file##*.}"

	# Generate a random string of letters with the same length as the file name (excluding the prefix and extension)
	#random_letters=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 10 | fold -w $((${#file} - ${#prefix} - ${#extension})) | head -n 1)
	# Generate a random string of 10 letters
	random_letters=$(cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 10 | head -n 1)

	# Create the new file name by combining the prefix, random letters, and extension
	new_name="$directory/$prefix$random_letters.$extension"

	# Rename the file
	mv "$file" "$new_name"

	# Replace the first two lines of the file
	sed -i "1,2c---\ntitle: $random_letters" "$new_name"

	# Print the original and new file names
	echo "Renamed and modified: $file -> $new_name"

    fi
  fi
done

cd ..
