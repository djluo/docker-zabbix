#!/bin/bash

#PW=$(</dev/urandom tr -dc A-Za-z0-9 | head -c12)
source /etc/zabbix/zabbix_proxy.conf
PW=${DBPassword:-xlands}

mysql -uroot -S ${DBSocket} <<EOF
create database zabbix_proxy character set utf8 collate utf8_bin;
grant all privileges on zabbix_proxy.* to zabbix_proxy@localhost   identified by '${PW}';
grant all privileges on zabbix_proxy.* to zabbix_proxy@'127.0.0.1' identified by '${PW}';
grant all privileges on zabbix_proxy.* to zabbix_proxy@'172.%'     identified by '${PW}';
EOF

i=0
pushd /usr/share/zabbix-proxy-mysql
[ -f ./schema.sql.gz ] \
  && zcat ./schema.sql.gz | mysql -uroot -S ${DBSocket} zabbix_proxy \
  && let i+=1
popd

[ $i -eq 1 ] && touch /logs/proxy-${VER}.lock
