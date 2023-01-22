#!/bin/bash

# FILESX=$(find . -maxdepth 1 -type f -exec grep "$@" {} +)
# FILESX=$(find . -type f -exec grep "cpp_proj_run" {} +)
# FILESX=$(ls | grep "cpp_proj_run")

# maybe not each time
sudo updatedb

FILESX=$(locate "cpp_proj_run" | grep $(pwd))
# echo "$FILESX $@"

$FILESX $@
