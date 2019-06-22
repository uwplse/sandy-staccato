#!/bin/bash

set -e
set -u

THIS_DIR=$(cd $(dirname $0) && pwd)

. $THIS_DIR/../deploy_tools.sh

function subsonic_deploy() {
	common_deploy $1 $2

	sudo cp $THIS_DIR/subsonic.properties /var/subsonic/subsonic.properties
        rm -f /var/subsonic/db/subsonic.lck
	sudo chown tomcat7:tomcat7 /var/subsonic/subsonic.properties
	set +e
	sudo /etc/init.d/tomcat7 start
	set -e
	wait_for_server
}

function inst() {
	deploy_runtime
	run_gradle subsonic:instrumentSubsonic;
	subsonic_deploy /home/staccato/evaluation-programs/subsonic-code/subsonic-main/target/subsonic.war "staccato"
}


function havoc() {
	deploy_runtime
	run_gradle subsonic:instrumentSubsonic;
	subsonic_deploy /home/staccato/evaluation-programs/subsonic-code/subsonic-main/target/subsonic.war "havoc"
}


function base() {
	run_gradle subsonic:buildClean
	subsonic_deploy /home/staccato/evaluation-programs/subsonic-orig/subsonic-main/target/subsonic.war "clean"
}


function mem() {
	deploy_runtime
	run_gradle subsonic:instrumentSubsonic;
	subsonic_deploy /home/staccato/evaluation-programs/subsonic-code/subsonic-main/target/subsonic.war "mem"
}

"$@"
