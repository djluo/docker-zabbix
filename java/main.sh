#!/bin/bash
# vim:set et ts=2 sw=2:
# set -x

JDK_OPT="/java-options.conf"

if [ -f  "${JDK_OPT}" ];then
  source "${JDK_OPT}"
else
  JDK_OPTIONS="-Xms128M -Xmx512M"
fi

DAEMON=/usr/sbin/zabbix_java
pushd $DAEMON

CLASSPATH="$DAEMON/lib"
for jar in `find lib bin -name "*.jar"`; do
  [ $jar != *junit* ] && CLASSPATH="$CLASSPATH:$DAEMON/$jar"
done

ZABBIX_OPTIONS="-Dzabbix.pidFile=/tmp/zabbix_proxy.pid"
[ -n "$LISTEN_IP"     ] && ZABBIX_OPTIONS="$ZABBIX_OPTIONS -Dzabbix.listenIP=$LISTEN_IP"
[ -n "$LISTEN_PORT"   ] && ZABBIX_OPTIONS="$ZABBIX_OPTIONS -Dzabbix.listenPort=$LISTEN_PORT"
[ -n "$START_POLLERS" ] && ZABBIX_OPTIONS="$ZABBIX_OPTIONS -Dzabbix.startPollers=$START_POLLERS"

exec /usr/bin/java -server -classpath $CLASSPATH $ZABBIX_OPTIONS $JDK_OPTIONS \
    com.zabbix.gateway.JavaGateway
    #1> >(exec /usr/bin/cronolog $current_dir/logs/stdout.txt-%Y%m%d >/dev/null 2>&1) \
    #2> >(exec /usr/bin/cronolog $current_dir/logs/stderr.txt-%Y%m%d >/dev/null 2>&1)
