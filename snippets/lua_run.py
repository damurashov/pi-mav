from command import command_lua_run
from connectivity import wait_for_message
from connectivity import mavcommon
import time


def _wait_ack():
    wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT, mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=True,
                     seconds=3)


if __name__ == "__main__":
    command_lua_run(False)
    _wait_ack()
    time.sleep(1)
