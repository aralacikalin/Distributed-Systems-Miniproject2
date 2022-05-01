
import sys
import subprocess
import rpyc
import time 

number_of_processes = int(sys.argv[1])

print(f'N={number_of_processes}')

start_port = 15229
friendly_id = 1
primary_general = None
primary_general_port = start_port
general_ports = []
processes = []
id_to_port = {}
port_to_id = {}

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

generals = []
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
    command = command.lower()

    cmds = command.split()

    if cmds[0] == 'actual-order':
        ## primary_general is None, then find new primary general
        full_output = primary_general.root.giveOrder( cmds[1] )
        
        print( f'G{port_to_id[primary_general_port]}, primary, majority={primary_general.root.getMajority()}, state={primary_general.root.getState()}' )

        for general in generals:
            general_state = general.root.getState()
            majority = general.root.getMajority()
            print( f'G??, secondary, majority={majority}, state={general_state}' )
    elif cmds[0] == 'g-state':
        if len(cmds) > 1:
            id = int(cmds[1])
            new_state = cmds[2]
            generals[id-1]
            port = id_to_port[id]
            conn = get_connection_by_port( generals, general_ports, port )
            if conn == None:
                print( "g-state command FAILED" )
                continue

            process_output = conn.root.setState( new_state.upper() )
        else:
            print( f'G{port_to_id[primary_general_port]}, primary, state={primary_general.root.getState()}' )
            for general in generals:
                general_state = general.root.getState()
                print( f'G??, secondary, state={general_state}' )
            
    # for idx, general in enumerate(generals):

    #     if command.lower() == 'exit':
    #         try:
    #             running=False
    #             conn.root.exit()
    #         except:
    #             break
    #         break
    #     else:
    #         cmd_name, value = command.split()

    #         if cmd_name.lower() == 'time-cs':
    #             conn.root.time_cs( int(value) )
    #         elif cmd_name.lower() == 'time-p':
    #             conn.root.time_p( int(value) )


for conn in connections:
   conn.root.exit()
