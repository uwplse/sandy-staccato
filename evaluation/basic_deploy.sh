#!/bin/bash


set -e
set -u

THIS_DIR=$(cd $(dirname $0) && pwd)

. $THIS_DIR/deploy_tools.sh

echo '' > /var/log/tomcat7/catalina.out
$THIS_DIR/tomcat_control start
wait_for_server

