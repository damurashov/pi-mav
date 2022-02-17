"""
Wrapper over Geoscan MAVLink protocol implementation. This wrapper is supposed to take into consideration all the
peculiarities of the implementation.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pymavlink.mavutil import mavlink
from connectivity import MavlinkConnectionWrapper
from generic import Logging, uptime_ms
from functools import reduce
from wrapper.command import Command
from wrapper.non_subproto import NonSubproto


class GeoscanMavlink(MavlinkConnectionWrapper, Command, NonSubproto):

	def __init__(self, *args, **kwargs):
		MavlinkConnectionWrapper.__init__(self, *args, **kwargs)
		Command.__init__(self, *args, **kwargs)
		NonSubproto.__init__(self, *args, **kwargs)

	def rc(self, roll, pitch, yaw, throttle, mode, mode1):
		"""
		Imitate RC transmitter control
		:param mode:
		:param mode1:  Overrides mode 0, when not 1000. More on that
			here
			https://gitlab.corp.geoscan.aero/d.murashov/dmdoc/-/blob/master/Autopilot-Mavlink--En.md
			and here
			https://gitlab.corp.geoscan.aero/d.murashov/dmdoc/-/blob/master/Autopilot-Generic-ClientPerspective-Ru.md
		:return:
		"""
		self.connection.mav.rc_channels_override_send(self.connection.target_system, self.connection.target_component,
			throttle, yaw, pitch, roll, mode, mode1)

	def set_position_local_nav(self, x, y, z, yaw, f_ensure_recv=True):
		"""
		Set the vehicle's position related to its external coordinate frame using its current navigation system.
		"""
		return self.non_subproto.set_position_target_local_ned(x=x, y=y, z=z, yaw=yaw, x_ignore=0, y_ignore=0,
			z_ignore=0, yaw_ignore=0, frame=mavlink.MAV_FRAME_LOCAL_NED)

	def set_position_local_body(self, x, y, z, yaw, f_ensure_recv=True):
		"""
		Set the vehicle's position related to its body frame using its current navigation system.
		"""
		return self.non_subproto.set_position_target_local_ned(x=x, y=y, z=z, yaw=yaw, frame=mavlink.MAV_FRAME_BODY_FRD,
			f_ensure_recv=f_ensure_recv, x_ignore=0, y_ignore=0, z_ignore=0, yaw_ignore=0)

	def set_velocity_local_nav(self, vx, vy, vz, yaw_rate, f_ensure_recv=True):
		return self.non_subproto.set_position_target_local_ned(vx=vx, vy=vy, vz=vz, yaw_rate=yaw_rate,
			frame=mavlink.MAV_FRAME_LOCAL_NED, ignore_vx=0, ignore_vy=0, ignore_vz=0, ignore_yaw_rate=0)

	def set_velocity_local_body(self, vx, vy, vz, yaw_rate, f_ensure_recv=True):
		return self.non_subproto.set_position_target_local_ned(vx=vx, vy=vy, vz=vz, yaw_rate=yaw_rate,
			frame=mavlink.MAV_FRAME_BODY_FRD, ignore_vx=0, ignore_vy=0, ignore_vz=0, ignore_yaw_rate=0)
