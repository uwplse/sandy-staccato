#!/bin/bash

set -e
set -u

THIS_DIR=$(cd $(dirname $0) && pwd)

. $THIS_DIR/benchmark_tools.sh

#rm -f $THIS_DIR/../paper/timing.tex

run_benchmark

for i in jforum subsonic; do
	echo ${output[$i]}
done
