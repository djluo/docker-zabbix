#!/usr/bin/python
# vim:set et ts=2 sw=2: #

import sys
import json
import struct
import socket

port = sys.argv[1]

if port == "discovery":
  ports = { "data": [ 
            { "{#PORT}": "9000", "{#NAME}": "h1-4002-hajava" }, 
            { "{#PORT}": "9335", "{#NAME}": "h1-4002-admin"  }, 
            { "{#PORT}": "9140", "{#NAME}": "h1-4002-chat"   }, 
            { "{#PORT}": "9141", "{#NAME}": "h1-4002-inner"  }, 
            { "{#PORT}": "9120", "{#NAME}": "h1-4002-login"  }, 
            { "{#PORT}": "9110", "{#NAME}": "h1-4002-outer"  }, 
            { "{#PORT}": "9180", "{#NAME}": "h1-4002-core"   }, 
            { "{#PORT}": "9170", "{#NAME}": "h1-4002-scene1" }, 
            { "{#PORT}": "9171", "{#NAME}": "h1-4002-scene2" }, 
            { "{#PORT}": "9172", "{#NAME}": "h1-4002-scene3" }, 
            { "{#PORT}": "9160", "{#NAME}": "h1-4002-whole"  }, 
            { "{#PORT}": "9333", "{#NAME}": "h1-4002-logserver" }, 
          ] }
  print json.dumps(ports,indent=4)
  sys.exit(0)
else:
  keys = sys.argv[2]

JavaGateway = ('172.17.42.1', 10052)

common  = {
  "request":  "java gateway jmx",
  "conn":     "172.17.42.1",
  "username": None,
  "password": None,
}

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
def queries():
  common["keys"] = [ jmxs[keys] ]
  common["port"] = port

  queries = json.dumps(common)

  header = 'ZBXD\1'
  length = struct.pack('<8B', len(queries),0,0,0,0,0,0,0)

  s = None
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(JavaGateway)

  if s is None:
    print 'could not open socket'
    sys.exit(1)

  s.send(header)
  s.send(length)
  s.send(queries)

  data = s.recv(5)
  data = s.recv(8)
  data = s.recv(1024)
  s.close()

  value = json.loads(data)
  value = value["data"][0]
  print value.get("value")

queries()
