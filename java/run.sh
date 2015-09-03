#!/bin/bash
# vim:set et ts=2 sw=2:

# Author : djluo
# version: 4.0(20150107)

# chkconfig: 3 90 19
# description:
# processname: redmine container

[ -r "/etc/baoyu/functions"  ] && source "/etc/baoyu/functions" && _current_dir
[ -f "${current_dir}/docker" ] && source "${current_dir}/docker"

# ex: ...../dir1/dir2/run.sh
# container_name is "dir1-dir2"
_container_name ${current_dir}

images="${registry}/baoyu/zabbix-java"
default_port="172.17.42.1:10052:10052"

action="$1"    # start or stop ...
_get_uid "$2"  # uid=xxxx ,default is "1000"
shift $flag_shift
unset  flag_shift

# 转换需映射的端口号
app_port="$@"  # hostPort
app_port=${app_port:=${default_port}}
_port

_run() {
  local mode="-d --restart=always"
  local name="$container_name"
  local cmd=""

  [ "x$1" == "xdebug" ] && _run_debug

  sudo docker run $mode $port \
    -e "TZ=Asia/Shanghai"     \
    -e "User_Id=${User_Id}"   \
    -v ${current_dir}/logs/:/var/log/zabbix/  \
    --name ${name} ${images} \
    $cmd
}
###############
_call_action $action
