import os
import random
import time

PROCESSER_SPEED = [1, 5, 10]
NUM_PROCESSERS = len(PROCESSER_SPEED)
INTERNAL_CLOCK = [0] * NUM_PROCESSERS
MESSAGE_QUEUE = [[]] * NUM_PROCESSERS
DURATION = 10


def get_action():
    
    # Generate random int between 1 and 10 inclusive
    action = random.randint(1, 10)
    return action



def execute(processer_id):
    

    if len(MESSAGE_QUEUE[processer_id]) > 0:
        _, _, new_clock = MESSAGE_QUEUE[processer_id].pop(0)
        INTERNAL_CLOCK[processer_id] += 1

        INTERNAL_CLOCK[processer_id] = max(INTERNAL_CLOCK[processer_id], new_clock)
        write_to_log(processer_id, "Received message at local time {}, queue length {}".format(INTERNAL_CLOCK[processer_id], len(MESSAGE_QUEUE[processer_id])))
    else:
        action = get_action()

        
        if action == 1:
            MESSAGE_QUEUE[(processer_id+1)%3].append(("send", processer_id, INTERNAL_CLOCK[processer_id]))
            INTERNAL_CLOCK[processer_id] += 1
            write_to_log(processer_id, "Sent message {} at local time {}".format(action, INTERNAL_CLOCK[processer_id]))
        elif action == 2:
            MESSAGE_QUEUE[(processer_id+2)%3].append(("send", processer_id, INTERNAL_CLOCK[processer_id]))
            INTERNAL_CLOCK[processer_id] += 1
            write_to_log(processer_id, "Sent message {} at local time {}".format(action, INTERNAL_CLOCK[processer_id]))
        elif action == 3:    
            MESSAGE_QUEUE[(processer_id+1)%3].append(("send", processer_id, INTERNAL_CLOCK[processer_id]))
            MESSAGE_QUEUE[(processer_id+2)%3].append(("send", processer_id, INTERNAL_CLOCK[processer_id]))
            INTERNAL_CLOCK[processer_id] += 1
            write_to_log(processer_id, "Sent double message {} at local time {}".format(action, INTERNAL_CLOCK[processer_id]))
        else:
            INTERNAL_CLOCK[processer_id] += 1
            write_to_log(processer_id, "Internal action at local time {}".format(INTERNAL_CLOCK[processer_id]))

def write_to_log(processer_id, message):
    with open("logs/{}.txt".format(processer_id), "a") as f:
        f.write(message + " " + str(time.time()) + "\n")

def run():
    # Processer speed is how often a processer will check for new instructions

    # Delete all log files
    if not os.path.exists("logs"):
        os.mkdir("logs")
    else:
        for f in os.listdir("logs"):
            os.remove(os.path.join("logs", f))
        

    real_timestamp = 0
    print("Running for {} seconds".format(DURATION))
    end = time.time() + DURATION
    while time.time() < end:
        real_timestamp += 1
        for i, processer_speed in enumerate(PROCESSER_SPEED):
            for _ in range(processer_speed):
                execute(i)



if __name__ == '__main__':
    run()
    