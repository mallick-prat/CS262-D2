""" Scale Model

This script implements the scale model specification for CS 262 Design Exercise 2.
The results of the simulation are stored in the logs folder.


The individual log files are formatted as follows:

Each line corresponds to an event (e.g. send, receive message, internal action)
Each line contains the following information about an event, comma-separated:
Event type (send message, receive message, or internal event)
The id of the machine on which the event took place. This value is 0, 1 or 2.
A piece of "data".
If the event was a received message, "data" is the number of remaining events in the queue.
If the event was send a message or internal event, "data" is an int drawn uniformly at random from [1,10] whose meaning is specificied in the project description.
The value of the logical clock for that event on that machine
The global system time of the event

"""

import os
import random
import time
import socket
import multiprocessing


""" Global parameters

These encode the clock speeds and probability of internal events.
"""

# Clock speeds are integers between the these two values
MIN_SPEED = 1
MAX_SPEED = 6

# Number of virtual machines
NUM_PROCESSERS = 3

# Randomly assign clock speeds to machines
PROCESSER_SPEED = [random.randint(MIN_SPEED, MAX_SPEED) for _ in range(NUM_PROCESSERS)]

# Length of simulation in seconds.
DURATION = 60

# Number of possible actions
MAX_ACTIONS = 10

# These actions correspond to sending a message to first neighbor
FIRST = [1,2]

# These actions correspond to sending a message to second neighbor
SECOND = [3,4]

# These actions correspond to sending a message to both neighbors
BOTH = [5,6]

# These actions correspond to sending a message. All other actions are internal events
SEND = FIRST + SECOND + BOTH

# Host and ports on which the 3 machines listen
HOST = "localhost"  
PORTS = [65443, 65442, 65441]


def get_action():
    """
    Generates an action uniformly at random.
    """
    action = random.randint(1, MAX_ACTIONS)
    return action


def write_to_log(processer_id, message, data, clock):
    """
    Writes message to log. See documentation in README.md for formatting details.
    """
    with open("logs/{}.txt".format(processer_id), "a") as f:
        f.write(",".join([message, str(processer_id), str(data), str(clock), str(time.time())])+"\n")


def run_vm(processer_id):
    """
    Executes the operations of one virtual machine.
    """

    queue = [] # Queue of unprocessed events
    clock = 0 # Internal clock valuue

    # Create a socket to listen to
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (HOST, PORTS[processer_id])
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()
    print("VM {} online, will begin sending and receiving in 1 second".format(processer_id))
    time.sleep(1)

    while True:
        # Add any incoming messages to the queue first
        try:
            Client, address = server_socket.accept()
            
            # Receive message from client
            with Client:
                while True:
                    data = Client.recv(2048)
                    if data:
                        queue.append(data.decode('utf-8').split(','))
                        break
        except Exception as e:
            print("No incoming message")

        # Check current time; stop in 1 second
        start = time.time()
        end = start + 1
        
        # Execute clock speed number of instructions   
        for _ in  range(PROCESSER_SPEED[processer_id]):
            # Process queued up event
            if len(queue) > 0:
                new_clock = int(queue.pop(0)[-1])
                clock += 1
                clock = max(clock, new_clock)
                write_to_log(processer_id, "recv", len(queue), clock)
            
            # Queue is empty, so generate new event
            else:
                action = get_action()
                
                # Action is of type send
                if action in SEND:

                    # Send to first neighbor
                    if action in FIRST:
                        first_socket = socket.socket()
                        first_socket.connect((HOST, PORTS[(processer_id+1)%3]))
                        first_socket.send(str.encode('{},{},{}'.format(action,processer_id,clock)))
                        first_socket.close()
                        clock+=1
                        write_to_log(processer_id, "sent", action , clock)

                    # Send to second neighbor
                    elif action in SECOND:
                        second_socket = socket.socket()
                        second_socket.connect((HOST, PORTS[(processer_id+2)%3]))
                        second_socket.send(str.encode('{},{},{}'.format(action,processer_id,clock)))
                        second_socket.close()
                        clock+=1
                        write_to_log(processer_id, "sent", action , clock)  
                    
                    # Send to both
                    elif action in BOTH:
                        first_socket = socket.socket()
                        first_socket.connect((HOST, PORTS[(processer_id+1)%3]))
                        first_socket.send(str.encode('{},{},{}'.format(action,processer_id,clock)))
                        first_socket.close()
                        second_socket = socket.socket()
                        second_socket.connect((HOST, PORTS[(processer_id+2)%3]))
                        second_socket.send(str.encode('{},{},{}'.format(action,processer_id,clock)))
                        second_socket.close()
                        clock+=1
                        write_to_log(processer_id, "sent2", action , clock)  
                
                # Internal event
                else:
                    clock+=1
                    write_to_log(processer_id, "internal", action , clock)
        
        # Sleep until 1 second has not elapsed, before executing more instructions
        if time.time() < end:
            time.sleep(end - time.time())   
    server_socket.close()
    
if __name__ == '__main__':
    
    # Delete all log files if already exist   
    if not os.path.exists("logs"):
        os.mkdir("logs")
    else:
        for f in os.listdir("logs"):
            os.remove(os.path.join("logs", f))
    
    # Run machines in separate Processes
    vms = [multiprocessing.Process(target=run_vm, args=(i,)) for i in range(NUM_PROCESSERS)]

    # Start the machines
    print("starting vms, clock speeds: " + str(PROCESSER_SPEED))
    for vm in vms:
        vm.start()

    # Break after DURATION number of seconds
    end = time.time() + DURATION
    while True:
        if time.time() > end:
            for vm in vms:
                vm.terminate()
                vm.join()
            break

