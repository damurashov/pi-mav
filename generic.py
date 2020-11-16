from common import *


def msg_set_position_target_local_ned():
    msg = mav.set_position_target_local_ned_encode(0, 0, 0, 0, 0, 1, 1, 1, 0.5, 0.5, 0.5,
                                                   0, 0, 0, 0, 0)
    return msg.pack(mav)


def set_position_target_local_ned():
    send(msg_set_position_target_local_ned())
