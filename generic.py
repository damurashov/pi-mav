from connectivity import *


def msg_set_position_target_local_ned():
    msg = mav.set_position_target_local_ned_encode(0, 0, 0, 0, 0, 1, 1, 1, 0.5, 0.5, 0.5,
                                                   0, 0, 0, 0, 0)
    mav.set_position_target_local_ned_encode(1, 1, 1, 1, 0xff, 0, 1, 1, 1, 1, 1, 1, 1, 1, 90, 1)
    return msg.pack(mav)


def set_position_target_local_ned():
    send(msg_set_position_target_local_ned())


def rc_channels_override():
    msg = mav.rc_channels_override_encode(0, 0, 1500, 1500, 1500, 1500, 2000, 2000, 0, 0)
    msg = msg.pack(mav)
    send(msg)


def manual_control(x, y, z, r, buttons):
    msg = mav.manual_control_encode(0, x, y, z, r, buttons)
    msg = msg.pack(mav)
    send(msg)