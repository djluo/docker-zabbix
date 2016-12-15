#!/usr/bin/python
# vim:set et ts=2 sw=2: #

import os
import sys
import json
import struct
import socket

def get_conf(path = "/var/lib/zabbix/java/"):
  conf = []
  if os.path.isdir(path):

    for app in os.listdir(path):
      fpath=os.path.join(path, app)
      if os.path.isfile(fpath):
        conf.append(fpath)

  return conf

def discovery(path = "/var/lib/zabbix/java/"):
  '''
  { "data": [ { "{#PORT}": "9000", "{#NAME}": "h1-4002-hajava" } ] }
  '''
  pool = { "data": [] }
  conf = get_conf()
  for app in conf:
    name=os.path.basename(app).rstrip(".conf")
    with open(app, 'r') as f:
      line=f.readline().rstrip('\n')
    ip, port = line.split(':')

    pool["data"].append( { "{#PORT}": port, "{#NAME}": name } )
  print json.dumps(pool,indent=4)

if __name__ == '__main__':

  if sys.argv[1] == "discovery":
    discovery()
  elif len(sys.argv) == 3:
    proc, port, key = sys.argv
  else:
    print "usage"
