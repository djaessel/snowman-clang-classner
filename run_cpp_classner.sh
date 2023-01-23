#!/bin/bash

# FILESX=$(find . -maxdepth 1 -type f -exec grep "$@" {} +)
# FILESX=$(find . -type f -exec grep "cpp_proj_run" {} +)
# FILESX=$(ls | grep "cpp_proj_run")

# maybe not each time
i="EMPTY" # default value if no arguments
for i in $@; do :; done # get last argument
if [ $i != "-ndbu" ]; then
  sudo updatedb
fi

FILESX=$(locate "cpp_proj_run" | grep $(pwd))
# echo "$FILESX $@"

$FILESX $@
