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

def discovery():
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
  return pool

def pool(key):
  jmxs = {
      "Uptime"            : "jmx[java.lang:type=Runtime,Uptime]",
      "MaxFD"             : "jmx[java.lang:type=OperatingSystem,MaxFileDescriptorCount]",
      "OpenFD"            : "jmx[java.lang:type=OperatingSystem,OpenFileDescriptorCount]",
      "Version"           : "jmx[java.lang:type=Runtime,VmVersion]",
      "ThreadCount"       : "jmx[java.lang:type=Threading,ThreadCount]",
      "PeakThreadCount"   : "jmx[java.lang:type=Threading,PeakThreadCount]",
      "DaemonThreadCount" : "jmx[java.lang:type=Threading,DaemonThreadCount]",
      "GC.CMS.Time"       : "jmx[\"java.lang:type=GarbageCollector,name=ConcurrentMarkSweep\",CollectionTime]",
      "GC.CMS.Count"      : "jmx[\"java.lang:type=GarbageCollector,name=ConcurrentMarkSweep\",CollectionCount]",
      "GC.PSM.Time"       : "jmx[\"java.lang:type=GarbageCollector,name=PS MarkSweep\",CollectionTime]",
      "GC.PSM.Count"      : "jmx[\"java.lang:type=GarbageCollector,name=PS MarkSweep\",CollectionCount]",
      "GC.PSS.Time"       : "jmx[\"java.lang:type=GarbageCollector,name=PS Scavenge\", CollectionTime]",
      "GC.PSS.Count"      : "jmx[\"java.lang:type=GarbageCollector,name=PS Scavenge\", CollectionCount]",
      "GC.PN.Time"        : "jmx[\"java.lang:type=GarbageCollector,name=ParNew\",CollectionTime]",
      "GC.PN.Count"       : "jmx[\"java.lang:type=GarbageCollector,name=ParNew\",CollectionCount]",
      "GC.COPY.Time"      : "jmx[\"java.lang:type=GarbageCollector,name=Copy\",  CollectionTime]",
      "GC.COPY.Count"     : "jmx[\"java.lang:type=GarbageCollector,name=Copy\",  CollectionCount]",
      "MP.CC.max"         : "jmx[\"java.lang:type=MemoryPool,name=Code Cache\",    Usage.max]",
      "MP.CC.used"        : "jmx[\"java.lang:type=MemoryPool,name=Code Cache\",    Usage.used]",
      "MP.CC.committed"   : "jmx[\"java.lang:type=MemoryPool,name=Code Cache\",    Usage.committed]",
      "MP.PSOG.max"       : "jmx[\"java.lang:type=MemoryPool,name=PS Old Gen\",    Usage.max]",
      "MP.PSOG.used"      : "jmx[\"java.lang:type=MemoryPool,name=PS Old Gen\",    Usage.used]",
      "MP.PSOG.committed" : "jmx[\"java.lang:type=MemoryPool,name=PS Old Gen\",    Usage.committed]",
      "MP.PSES.max"       : "jmx[\"java.lang:type=MemoryPool,name=PS Eden Space\",    Usage.max]",
      "MP.PSES.used"      : "jmx[\"java.lang:type=MemoryPool,name=PS Eden Space\",    Usage.used]",
      "MP.PSES.committed" : "jmx[\"java.lang:type=MemoryPool,name=PS Eden Space\",    Usage.committed]",
      "MP.PSSS.max"       : "jmx[\"java.lang:type=MemoryPool,name=PS Survivor Space\",Usage.max]",
      "MP.PSSS.used"      : "jmx[\"java.lang:type=MemoryPool,name=PS Survivor Space\",Usage.used]",
      "MP.PSSS.committed" : "jmx[\"java.lang:type=MemoryPool,name=PS Survivor Space\",Usage.committed]",
      "M.HEAP.max"        : "jmx[java.lang:type=Memory,HeapMemoryUsage.max]",
      "M.HEAP.used"       : "jmx[java.lang:type=Memory,HeapMemoryUsage.used]",
      "M.HEAP.committed"  : "jmx[java.lang:type=Memory,HeapMemoryUsage.committed]",
      }
  value=None

  if key in jmxs:
    value = [ jmxs[key] ]
  else:
    print '-4'
    sys.exit(1)

  return value

def conn(JavaGateway,req):
  s = None
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  except socket.error as msg:
    print '-1'
    sys.exit(1)

  try:
    s.connect(JavaGateway)
  except socket.error as msg:
    s.close()
    print '-2'
    sys.exit(1)

  if s is None:
    print '-3'
    sys.exit(1)

  s.send(req)

  data = s.recv(5 + 8)
  data = s.recv(1024)

  s.close()

  return data

def queries(port, key):
  JavaGateway = ('172.17.42.1', 10052)

  common = {
    "request":  "java gateway jmx",
    "conn":     "172.17.42.1",
    "username": None,
    "password": None,
    "keys": pool(key),
    "port": port,
    }

  req    = json.dumps(common)
  header = 'ZBXD\1'
  length = struct.pack('<8B', len(req),0,0,0,0,0,0,0)

  raw = conn(JavaGateway, header + length + req)

  try:
    res = json.loads(raw)
  except:
    print '-5'
    sys.exit(1)

  value = 0

  if "response" in res:
    if res["response"] == "success":
      value = res["data"][0]["value"]

  return value

def usage():
  print "Usage: %s discovery"  % sys.argv[0]
  print "     : %s port key\n" % sys.argv[0]

  pool = discovery()

  port = 9000
  if len(pool["data"]) > 0:
    port = pool["data"][0]['{#PORT}']

  print "   ex: %s %s Uptime"  % ( sys.argv[0], port )
  sys.exit(1)

if __name__ == '__main__':

  if len(sys.argv) > 1 and sys.argv[1] == "discovery":
    pool = discovery()
    print json.dumps(pool, indent=4)
  elif len(sys.argv) == 3:
    proc, port, key = sys.argv
    print queries(port,key)
  else:
    usage()
