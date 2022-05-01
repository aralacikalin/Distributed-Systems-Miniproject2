"""In this version of the server main replica resets when another client connects """
from multiprocessing import connection
import rpyc
from rpyc.utils.server import ThreadedServer,OneShotServer
import datetime
date_time=datetime.datetime.now()

from threading import Lock
import time
from functools import wraps
import sys
import datetime
import time


otherProcessPorts=[]
thisPort=int(sys.argv[1])
okCount=0


HELD="HELD"
DONOTWANT="DO-NOT-WANT"
WANTED="WANTED"
# start the main loop

connections=[]


# start a separate thread for system tick
FAULTY="F"
NONFAULTY="NF"
currentState=NONFAULTY
receivedCommand=""
majorityCommand=""
class ProcessService(rpyc.Service):


    def exposed_other_ps_ports(self,ports):
        global otherProcessPorts
        global connections
        for port in ports:
            otherProcessPorts.append(port)
        for port in otherProcessPorts:
            connections.append(rpyc.connect("localhost",port))
    
    def exposed_getCommand(self,command):
        pass

    def exposed_validateCommand(self):
        pass

    def exposed_sendMyCommand(self,):
        pass




     

 
if __name__=='__main__':
 t=ThreadedServer(ProcessService, port=thisPort)
 t.start()