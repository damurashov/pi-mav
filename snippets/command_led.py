from command import *
from connectivity import wait_for_message
import time
from random import random


def _wait_for_ack(seconds=4, do_print=True):
    wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=do_print, seconds=seconds)


def random_tuple(n):
    return tuple([random() for r in range(0, n)])


if __name__ == "__main__":
    N_LED = 4

    try:
        while True:
            for i in range(0, N_LED):
                args = tuple([random() for r in range(0, 3)])
                command_user_1_led(i, *args)
                time.sleep(1)
    except:
        for i in range(0, N_LED):
            command_user_1_led(i, 0, 0, 0)
            time.sleep(0.1)
