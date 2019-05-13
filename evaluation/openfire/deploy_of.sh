#!/bin/bash

THIS_DIR=$(cd $(dirname $0) && pwd)

. $THIS_DIR/_kill_of.sh

if [ "$1" = "base" ]; then
	kill_of
	(cd $THIS_DIR/../../; gradle openfire:buildClean)
	cp $THIS_DIR/conf/* /home/staccato/evaluation-programs/openfire_orig/target/openfire/conf;
	shift
	if [ "$#" = "1" ]; then
		bash /home/staccato/evaluation-programs/openfire_orig/target/openfire/bin/openfire.sh > $1;
	else
		bash /home/staccato/evaluation-programs/openfire_orig/target/openfire/bin/openfire.sh;
	fi
	exit
fi

(cd $THIS_DIR/../../; gradle openfire:deploy)

INST_OF="/home/staccato/evaluation-programs/openfire_src/target/openfire/bin/"

cp $THIS_DIR/conf/* $INST_OF/../conf/

declare -A PROFILES

PROFILES=(["baseline"]="" ["havoc"]="-Dstaccato.record=true -Dstaccato.logfile=/tmp/of-staccato.log -Dstaccato.random-pause=true" ["havocupdate"]="-Dstaccato.havoc=3 -Dstaccato.havoc-update=1" ["mem"]="-Dstaccato.mem-file=/tmp/of-mem -Dstaccato.record-mem=true")

PROFILE_FLAGS=${PROFILES[$1]}

shift

kill_of

if [ "$#" = "1" ]; then
	OPENFIRE_DEF=$PROFILE_FLAGS bash $INST_OF/openfire.sh > $1
else
	OPENFIRE_DEF=$PROFILE_FLAGS bash $INST_OF/openfire.sh
fi
