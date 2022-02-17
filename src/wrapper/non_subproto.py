"""
Generic messages
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pymavlink.mavutil import mavlink
from connectivity import MavlinkConnectionWrapper
from generic import Logging, uptime_ms
from functools import reduce


class NonSuproto(MavlinkConnectionWrapper):

	def __init__(self, *args, **kwargs):
		MavlinkConnectionWrapper.__init__(self, *args, **kwargs)

	def set_position_target_local_ned(self=0, x=0, y=0, z=0, vx=0, vy=0, vz=0, ax=0, ay=0, az=0, yaw=0,
		yaw_rate=0, frame=mavlink.MAV_FRAME_LOCAL_NED, x_ignore=1, y_ignore=1, z_ignore=1, vx_ignore=1, vy_ignore=1,
		vz_ignore=1, ax_ignore=1, ay_ignore=1, az_ignore=1, yaw_ignore=1, yaw_rate_ignore=1, force_set=0,
		f_ensure_recv=True):

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

		Logging.info(__file__, NonSuproto, "SET_POSITION_TARGET_LOCAL_NED")
		self.connection.mav.set_position_target_local_ned_send(uptime_ms(), self.connection.target_system,
			self.connection.target_component, mask, x, y, z, vx, vy, vz, ax, ay, az, yaw, yaw_rate)

		return self.wrap_recv_match(f_ensure_recv=f_ensure_recv, type="POSITION_TARGET_LOCAL_NED")
