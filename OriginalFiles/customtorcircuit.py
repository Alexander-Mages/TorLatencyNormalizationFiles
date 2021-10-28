import os
import sys
import time
import socket
from TorCtl import *

num_circs = 10

selmgr = PathSupport.SelectionManager(
    pathlen = 3,
    use_exit = "name of exit node",
    use_guards = "name of guard"
)
try:
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("localhost",9051))
    c = PathSupport.Connection(s)
    c.authenticate()
except socket.error as e:
    print("cant connect to tor control port")
    sys.exit(-1)

c.set_events([TorCtl.EVENT_TYPE.CIRC,TorCtl.EVENT_TYPE.STREAM,TorCtl.EVENT_TYPE.ADDRMAP,TorCtl.EVENTTYPE.NS,TorCtl.EVENT_TYPE.NEWDESC], True)
c.set_option("__DisablePredictedCircuits", "1")
c.set_option("__LeaveStreamsUnnattached", "1")


handler = PathSupport.StreamHandler(c, selmgr, num_circs, GeoIPSupport.GeoIPRouter)