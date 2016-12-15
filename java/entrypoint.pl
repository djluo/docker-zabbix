#!/usr/bin/perl
# vim:set et ts=2 sw=2:

# Author : djluo
# version: 2.0(20150107)
#
# 初衷: 每个容器用不同用户运行程序,已方便在宿主中直观的查看.
# 需求: 1. 动态添加用户,不能将添加用户的动作写死到images中.
#       2. 容器内尽量不留无用进程,保持进程树干净.
# 问题: 如用shell的su命令切换,会遗留一个su本身的进程.
# 最终: 使用perl脚本进行添加和切换操作. 从环境变量User_Id获取用户信息.

use strict;
#use English '-no_match_vars';

my $uid = 1000;
my $gid = 1000;
my $ver = 1000;

$uid = $gid = $ENV{'User_Id'} if $ENV{'User_Id'} =~ /\d+/;
$ver = $ENV{'VER'} if $ENV{'VER'} =~ /^\d+\.\d+/;

sub add_user {
  my ($name,$id)=@_;

  system("/usr/sbin/useradd",
    "-s", "/sbin/nologin",
    "-d", "/var/empty/$name",
    "-U", "--uid", "$id",
    "$name");
}
unless (getpwuid("$uid")){
  add_user("docker", "$uid");
}

my $logs="/var/log/zabbix";
system("chown", "docker.docker", "-R", "$logs") if ( -d "$logs");

for my $pid ("/tmp/supervisord.pid","/tmp/zabbix_java.pid"){
  unlink($pid) if ( -f $pid);
}

my $agent_dir  = "/etc/zabbix/zabbix_agentd.d/";
my $script_dir = "/etc/zabbix/script/";
my $zabbix_dir = "/var/lib/zabbix/";

system("cp", "-v", "/example/java.conf",   "$agent_dir" ) if ( -d "$agent_dir" );
system("cp", "-v", "/example/lld-java.py", "$script_dir") if ( -d "$script_dir");

my $socket   = "/var/lib/mysql/mysql.sock";
my $password = "zabbix1";

$socket   = $ENV{'socket'}   if $ENV{'socket'};
$password = $ENV{'password'} if $ENV{'password'};

system("mkdir", "-vm", "700", "$zabbix_dir") unless ( -d "$zabbix_dir");
system("cp", "-v", "/example/.my.cnf", "$zabbix_dir") unless ( -f "$zabbix_dir/.my.cnf");
system("sed", "-i", "s%\\(^socket   =\\).*%\\1 $socket%",   "$zabbix_dir/.my.cnf");
system("sed", "-i", "s%\\(^password =\\).*%\\1 $password%", "$zabbix_dir/.my.cnf");
system("chmod", "400", "$zabbix_dir/.my.cnf");


$( = $) = $gid; die "switch gid error\n" if $gid != $( ;
$< = $> = $uid; die "switch uid error\n" if $uid != $< ;
$ENV{'HOME'} = "/home/docker";

# 设置CLASSPATH
my $zabbix_bin = "/usr/sbin/zabbix_java";

my @all="$zabbix_bin/lib";
for my $dir ( ( "$zabbix_bin/lib", "$zabbix_bin/bin") ) {
  opendir(DIR, "$dir") or die "Error in opening dir $dir\n";
  while(readdir(DIR)) {
    next if ( $_ eq '.' or $_ eq '..');
    next if $_ !~ /\.jar$/ ;
    push @all, "$dir/$_";
  }
  closedir(DIR);
}

$ENV{'CLASSPATH'} = join(':', @all);

my @JAVA_OPTS = ("-Xms32M", "-Xmx64M");
   @JAVA_OPTS = split(/ /,$ENV{'JAVA_OPTS'}) if ($ENV{'JAVA_OPTS'});

exec("/usr/bin/java", "-server", @JAVA_OPTS, "com.zabbix.gateway.JavaGateway");
