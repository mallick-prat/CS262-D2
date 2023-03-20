import os
import random
import time
import socket
import multiprocessing


# Define constants
MIN_CLOCK_SPEED = 1
MAX_CLOCK_SPEED = 6
NUM_VIRTUAL_MACHINES = 3
DURATION_SECONDS = 60
MAX_ACTIONS_PER_CYCLE = 10

# Define actions
SEND_TO_FIRST_NEIGHBOR = 1
SEND_TO_SECOND_NEIGHBOR = 2
SEND_TO_BOTH_NEIGHBORS = 3
INTERNAL_EVENT = 4

# Define host and ports
HOST = "localhost"
PORTS = [65443, 65442, 65441]


def generate_action():
    """
    Generate a new action.
    """
    return random.randint(1, MAX_ACTIONS_PER_CYCLE)


def write_to_log(vm_id, event_type, data, clock):
    """
    Writes an event to the log file.
    """
    with open(f"logs/vm{vm_id}.log", "a") as f:
        f.write(f"{event_type},{vm_id},{data},{clock},{time.time()}\n")


def run_virtual_machine(vm_id):
    """
    Runs a single virtual machine.
    """
    event_queue = [] 
    internal_clock = 0 

    # Set up listening socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (HOST, PORTS[vm_id])
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()

    print(f"Virtual Machine {vm_id} is online and will begin sending and receiving messages in 1 second.")
    time.sleep(1)

    while True:
        # Check for incoming messages
        try:
            client_socket, address = server_socket.accept()

            # Receive message from client
            with client_socket:
                while True:
                    data = client_socket.recv(2048)
                    if data:
                        event_queue.append(data.decode('utf-8').split(','))
                        break
        except Exception as e:
            pass

        # Stop after DURATION_SECONDS
        start_time = time.time()
        end_time = start_time + DURATION_SECONDS

        # Execute instructions according to clock speed
        for _ in range(random.randint(MIN_CLOCK_SPEED, MAX_CLOCK_SPEED)):
            # Process queued event
            if len(event_queue) > 0:
                new_clock_time = int(event_queue.pop(0)[-2])
                internal_clock += 1
                internal_clock = max(internal_clock, new_clock_time)
                write_to_log(vm_id, "recv", len(event_queue), internal_clock)
            # Generate new event
            else:
                new_action = generate_action()
                if new_action == SEND_TO_FIRST_NEIGHBOR:
                    first_socket = socket.socket()
                    first_socket.connect((HOST, PORTS[(vm_id + 1) % NUM_VIRTUAL_MACHINES]))
                    first_socket.send(str.encode(f'{new_action},{vm_id},{internal_clock}'))
                    first_socket.close()
                    internal_clock += 1
                    write_to_log(vm_id, "send", SEND_TO_FIRST_NEIGHBOR, internal_clock)
                elif new_action == SEND_TO_SECOND_NEIGHBOR:
                    second_socket = socket.socket()
                    second_socket.connect((HOST, PORTS[(vm_id + 2) % NUM_VIRTUAL_MACHINES]))
                    second_socket.send(str.encode(f'{new_action},{vm_id},{internal_clock}'))
                    second_socket.close()
                    internal_clock += 1
                    write_to_log(vm_id, "send", SEND_TO_SECOND_NEIGHBOR, internal_clock)
                elif new_action == SEND_TO_BOTH
