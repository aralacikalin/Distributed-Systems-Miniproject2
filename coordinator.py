
import sys
import subprocess
import rpyc
import time 
import os
import signal 

number_of_processes = int(sys.argv[1])

print(f'N={number_of_processes}')

start_port = 15330
friendly_id = 1
primary_general = None
primary_general_port = start_port
general_ports = []
processes = []
id_to_port = {}
port_to_id = {}
generals = []

for i in range(number_of_processes):
    general_ports.append( start_port+i )
    
    cmd = 'python general.py ' + str(start_port+i) #+ ' ' + str(friendly_id)
    print( 'cmd', cmd.split() )
    
    port_to_id[ start_port+i ] = friendly_id
    id_to_port[ friendly_id ] = start_port+i

    friendly_id += 1

    p = subprocess.Popen( cmd.split() )
    processes.append(p)

def all_ports_except( all_ports, port_to_exclude ):
    output = []
    for port in all_ports:
        if port == port_to_exclude:
            continue
        output.append( port )
        
    return output

def get_connection_by_port( connectins, ports, port ):
    for idx, p in enumerate( ports ):
        if p == port:
            return connectins[idx]

    return None

time.sleep(2)

for port in general_ports:
    generals.append( rpyc.connect('localhost',port) )

primary_general = generals[0]
generals = generals[1:]

primary_general_port = general_ports[0]
general_ports = general_ports[1:]

primary_general.root.addGenerals( general_ports ) 

## general other_ps_ports ==> add_generals 
for idx, conn in enumerate(generals):
    other_ps_ports = all_ports_except( general_ports, general_ports[idx] )
    conn.root.addGenerals( other_ps_ports )

running=True
while running:
    print( "Input the command: " )
    
    command = input()
    
    if not command:
        continue

    command = command.lower()

    cmds = command.split()

    if cmds[0] == 'actual-order':

        full_output = primary_general.root.giveOrder( cmds[1] )
        
        print( f'G{port_to_id[primary_general_port]}, primary, majority={primary_general.root.getMajority()}, state={primary_general.root.getState()}' )

        for idx, general in enumerate( generals ):
            general_state = general.root.getState()
            majority = general.root.getMajority()
            port = general_ports[idx]
            print( f'G{port_to_id[port]}, secondary, majority={majority}, state={general_state}' )
        
        print( full_output )
    elif cmds[0] == 'g-state':
        if len(cmds) > 1:
            id = int(cmds[1])
            new_state = cmds[2]

            if id_to_port[id] == primary_general_port:
                print(f"ERROR: Primary general can't be a TRAITOR!") 
                continue

            if id not in id_to_port:
                print(f"ERROR: there is no such general with id={general_id_to_kill}") 
                continue

            port = id_to_port[id]
            conn = get_connection_by_port( generals, general_ports, port )
            if conn == None:
                print( "g-state command FAILED" )
                continue

            process_output = conn.root.setState( 'F' if new_state.upper() == 'FAULTY' else 'NF' )
        else:
            print( f'G{port_to_id[primary_general_port]}, primary, state={primary_general.root.getState()}' )
            for idx, general in enumerate( generals ):
                general_state = general.root.getState()
                port = general_ports[idx]
                print( f'G{port_to_id[port]}, secondary, state={general_state}' )

    elif cmds[0] == 'g-kill':
        if len( generals ) <= 0:
            print("ERROR: Killing last general is forbidden!")
            continue

        general_id_to_kill = int(cmds[1])

        if general_id_to_kill not in id_to_port:
            print(f"ERROR: there is no such general with id={general_id_to_kill}") 
            continue

        general_port_to_kill = id_to_port[ general_id_to_kill ]

        if general_port_to_kill == primary_general_port and generals:
            primary_general = generals[0]
            primary_general_port = general_ports[0]

            generals = generals[1:]
            general_ports = general_ports[1:]

            id_to_port.pop( general_id_to_kill )
            port_to_id.pop( general_port_to_kill )
            
        else:
            for idx, general in enumerate( generals ):
                general_id = port_to_id[ general_ports[idx] ]
                if general_id == general_id_to_kill:
                    generals[idx].close()
                    generals.pop( idx )
                    general_ports.pop( idx )
                    id_to_port.pop( general_id_to_kill )
                    port_to_id.pop( general_port_to_kill )
                    break
        
        primary_general.root.reset_all_ports( general_ports )

        for idx, conn in enumerate(generals):
            other_ps_ports = all_ports_except( general_ports, general_ports[idx] )
            conn.root.reset_all_ports( other_ps_ports )


    elif cmds[0] == 'g-add':
        old_ports = general_ports.copy()
        num_new_generals = int(cmds[1])
        new_ports = []
        for i in range(num_new_generals):
            general_ports.append( start_port+friendly_id+i )
            new_ports.append( general_ports[-1] )
            cmd = 'python general.py ' + str(general_ports[-1]) #+ ' ' + str(friendly_id)
            #print( 'cmd', cmd.split() )
            
            port_to_id[ general_ports[-1] ] = friendly_id
            id_to_port[ friendly_id ] = general_ports[-1]

            friendly_id += 1

            p = subprocess.Popen( cmd.split() )
            processes.append(p)

        # sleep is need since we are using subprocess( i.e. new general ). 
        # We need to wait until it initializes otherwise it won't be possible to connect to the server. 
        time.sleep(2)

        for conn in generals:
            conn.root.addGenerals( new_ports )

        primary_general.root.addGenerals( new_ports ) 

        new_generals = []
        for port in new_ports:
            new_generals.append( rpyc.connect('localhost',port) )

        for idx, conn in enumerate(new_generals):
            other_ps_ports = all_ports_except( new_ports, new_ports[idx] )
            conn.root.addGenerals( old_ports + other_ps_ports )

        for ngen in new_generals:
            generals.append( ngen )


for conn in connections:
   conn.root.exit()
