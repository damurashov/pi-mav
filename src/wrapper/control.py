from pymavlink.dialects.v20 import common
from pymavlink import mavutil
import sys
import pathlib
from pymavlink.dialects.v20.common import MAV_FRAME_LOCAL_NED, MAV_FRAME_BODY_FRD

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from dataclasses import dataclass, field
from functools import reduce


@dataclass
class Control:
	mavlink_connection: object
	target_system: int = field(default_factory=int)
	target_component: int = field(default_factory=int)

	def send_set_position_target_local_ned(self, x=0, y=0, z=0, vx=0, vy=0, vz=0, ax=0, ay=0, az=0, yaw=0,
		yaw_rate=0, frame=MAV_FRAME_LOCAL_NED, x_ignore=1, y_ignore=1, z_ignore=1, vx_ignore=1, vy_ignore=1,
		vz_ignore=1, ax_ignore=1, ay_ignore=1, az_ignore=1, yaw_ignore=1, yaw_rate_ignore=1, force_set=0):

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

		# print(f"SET_POSITION_TARGET_LOCAL_NED: mask: {bin(mask)}, args: {locals()}")
		time_boot_ms = 0
		self.mavlink_connection.mav.send(self.mavlink_connection.mav.set_position_target_local_ned_encode(time_boot_ms,
			self.target_system, self.target_component, frame, mask, x, y, z, vx, vy, vz, ax, ay, az, yaw, yaw_rate))

	def recv_mission_item_reached(self, timeout_seconds=1, block=True):
		return self.mavlink_connection.recv_match(type="MISSION_ITEM_REACHED", blocking=block, timeout=timeout_seconds)
