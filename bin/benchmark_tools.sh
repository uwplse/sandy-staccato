#!/bin/bash

THIS_DIR=$(cd $(dirname $0) && pwd)

declare -A commands

commands=(["openfire"]="bash $THIS_DIR/../evaluation/openfire/run_tests.sh baseline" ["jforum"]="bash $THIS_DIR/../evaluation/jforum/run_tests.sh" ["subsonic"]="bash $THIS_DIR/../evaluation/subsonic/run_tests.sh")

declare -A output

function run_benchmark() {
	ARG=
	if [ $# -gt 0 ]; then
		ARG=$1
	fi
	for i in jforum subsonic; do
		output[$i]=""
		for j in $(seq 0 4); do
			TMP=$(${commands[$i]} $ARG)
			echo $TMP
			output[$i]="${output[$i]} $TMP"
		done
	done
}

run_benchmark
