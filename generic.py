from connectivity import *
import math
from functools import reduce
from pymavlink.mavutil import mavlink

DEFAULT_SPEED = 0.2


def set_position_target_local_ned(self=0, x=0, y=0, z=0, vx=0, vy=0, vz=0, ax=0, ay=0, az=0, yaw=0,
    yaw_rate=0, frame=mavlink.MAV_FRAME_LOCAL_NED, x_ignore=1, y_ignore=1, z_ignore=1, vx_ignore=1, vy_ignore=1,
    vz_ignore=1, ax_ignore=1, ay_ignore=1, az_ignore=1, yaw_ignore=1, yaw_rate_ignore=1, force_set=0):
    """
    mavcommon.MAV_FRAME_BODY_FRD, mavlink.MAV_FRAME_LOCAL_NED
    """

    mask_bits = (
        x_ignore << 0,
        y_ignore << 1,
        z_ignore << 2,
        vx_ignore << 3,
        vy_ignore << 4,
        vz_ignore << 5,
        ax_ignore << 6,
        ay_ignore << 7,
        az_ignore << 8,
        force_set << 9,
        yaw_ignore << 10,
        yaw_rate_ignore << 11,
    )
    mask = reduce(lambda a, b: a | b, mask_bits, 0)

    print(f"SET_POSITION_TARGET_LOCAL_NED: mask: {bin(mask)}, args: {locals()}")
    send(mav.set_position_target_local_ned_encode(0, 0, 0, frame, mask, x, y, z, vx, vy, vz,
        ax, ay, az, yaw, yaw_rate).pack(mav))


def rc_channels_override():
    msg = mav.rc_channels_override_encode(0, 0, 1500, 1500, 1500, 1500, 2000, 2000, 0, 0)
    msg = msg.pack(mav)
    send(msg)


def manual_control(x, y, z, r, buttons):
    msg = mav.manual_control_encode(0, x, y, z, r, buttons)
    msg = msg.pack(mav)
    send(msg)