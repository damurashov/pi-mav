from command import *
import time

if __name__ == "__main__":
    command_arm(True)
    command_wait_for_ack()

    time.sleep(1)

    command_takeoff()
    command_wait_for_ack()