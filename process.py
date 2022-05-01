"""In this version of the server main replica resets when another client connects """
from multiprocessing import connection
from sre_parse import State
import rpyc
from rpyc.utils.server import ThreadedServer,OneShotServer
import datetime
date_time=datetime.datetime.now()

import sys
import datetime
import time


otherProcessPorts=[]
thisPort=int(sys.argv[1])



connections=[]


# start a separate thread for system tick
FAULTY="F"
NONFAULTY="NF"
currentState=NONFAULTY
isPrimary=False
ATTACK="attack"
RETREAT="retreat"
receivedCommand=""
majorityCommand=""
isVoting=False
import _thread

def bully():
        i=0
        global thisPort
        global isVoting
        global isPrimary
        smallest=thisPort
        for port in otherProcessPorts:
            if port<smallest:
                smallest=port
                i+=1
        if(smallest==thisPort):
            isPrimary=True
        else:
            for j in range(i):
                connections[j].root.bully()
        isVoting=True
        


# class Timer:

#     def __init__(self, timerSec=5):
#         self.timerSec=timerSec
#         self.currentTime=timerSec


#     # starts a thread that runs the process
#     def start(self):
#         _thread.start_new_thread(self.run, ())

        
#     def run(self):
#         global isPrimary
#         global isVoting
#         while True:
#             while self.currentTime:
#                 time.sleep(1)
#                 self.currentTime -= 1
#             for conn in connections:
#                 if(isPrimary):
#                     conn.root.heartBeat()
#                 else:
#                     bully()

        
            

# timer=Timer()
# timer.start()

class ProcessService(rpyc.Service):
    global currentState

    def exposed_addGeneral(self,ports):
        global otherProcessPorts
        global connections
        for port in ports:
            otherProcessPorts.append(port)
        for port in otherProcessPorts:
            connections.append(rpyc.connect("localhost",port))

    def exposed_reset_all_ports(self,ports):
        global otherProcessPorts
        global connections
        otherProcessPorts=[]
        for conn in connections:
            conn.close()
        connections=[]
        for port in ports:
            otherProcessPorts.append(port)
        for port in otherProcessPorts:
            connections.append(rpyc.connect("localhost",port))
    
    # def exposed_bully(self):
    #     if(not isVoting):
    #         bully()


    def exposed_die(self):
        for conn in connection:
            conn.close()

    


    
    # def exposed_heartBeat(self):
    #     timer.currentTime=timer.timerSec

    def exposed_isGeneral():
        global thisPort
        if(isPrimary):
            return thisPort
        else:
            return False

    def exposed_becomePrimary(self):
        global isPrimary
        isPrimary=True
    def exposed_changeState(self,state):
        global currentState
        if(state=="faulty"):
            global FAULTY
            currentState=FAULTY
        else:
            global NONFAULTY
            currentState=NONFAULTY
    def exposed_giveCommand(self,command):
        global majorityCommand
        
        majorityCommand=command
        for conn in connections:
            conn.root.getCommand(command)
        attackCount,retreatCount=0,0
        for conn in connection:
            attackCount,retreatCount=conn.root.exposed_validateCommand()
        if(attackCount>retreatCount):
            faultyNodesCount=len(connections)-attackCount
            allGeneralCount=attackCount+retreatCount+1
            return f"Execute order: attack! {faultyNodesCount} faulty node in the system {attackCount} out of {allGeneralCount} quorum suggest attack"
        elif(attackCount<retreatCount):
            faultyNodesCount=len(connections)-retreatCount
            allGeneralCount=attackCount+retreatCount+1
            return f"Execute order: retreat! {faultyNodesCount} faulty node in the system {retreatCount} out of {allGeneralCount} quorum suggest retreat"
        else:
            faultyNodesCount=retreatCount
            allGeneralCount=attackCount+retreatCount+1
            return f"Execute order: cannot be determined - not enough generals in the system! {faultyNodesCount} faulty node in the system - {retreatCount+attackCount} out of {allGeneralCount} quorum suggest retreat"

        
    
    def exposed_getCommand(self,command):
        global receivedCommand
        receivedCommand=command

    def exposed_validateCommand(self):
        global majorityCommand
        global ATTACK
        global RETREAT
        allCommands=[]
        attackCount=0
        retreatCount=0
        for conn in connections:
            res=conn.root.returnMyCommand()
            allCommands.append(res)
        for command in allCommands:
            if(command==ATTACK):
                attackCount+=1
            else:
                retreatCount+=1
        if(attackCount>retreatCount):
            majorityCommand=ATTACK
        elif(attackCount<retreatCount):
            majorityCommand=RETREAT
        else:
            majorityCommand="undefined"

        return attackCount,retreatCount

    def exposed_getMajority(self):
        global majorityCommand

        return majorityCommand
    def exposed_getState(self):
        global currentState

        return currentState


    def exposed_returnMyCommand(self):
        global NONFAULTY
        global ATTACK
        global RETREAT

        if currentState==NONFAULTY:
            return receivedCommand
        else:
            if(receivedCommand==ATTACK):
                return RETREAT
            else:
                return ATTACK




     

 
if __name__=='__main__':
 t=ThreadedServer(ProcessService, port=thisPort)
 t.start()