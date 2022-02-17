"""
Encapsulation of various MAVLink commands related to flight control operations
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from pymavlink.mavutil import mavlink
from connectivity import MavlinkConnectionWrapper
from generic import Logging
from functools import reduce


class CommandLong(MavlinkConnectionWrapper):
	ENSURE_ACK_RECEIVE_DEFAULT = True

	def __init__(self, *args, **kwargs):
		MavlinkConnectionWrapper.__init__(self, *args, **kwargs)
		self.command_send_cb = self.connection.mav.command_send_long  # MAVLink command protocol can be implemented via COMMAND_LONG... or COMMAND_INT...

	@staticmethod
	def log_result(ack):
		ack_map = {
			0: "MAV_RESULT_ACCEPTED",
			1: "MAV_RESULT_TEMPORARILY_REJECTED",
			2: "MAV_RESULT_DENIED",
			3: "MAV_RESULT_UNSUPPORTED",
			4: "MAV_RESULT_FAILED",
			5: "MAV_RESULT_IN_PROGRESS",
			6: "MAV_RESULT_CANCELLED"}

		if ack is not None:
			Logging.get_logger().info(Logging.format(__file__, ack_map[int(ack.result)]))
		else:
			Logging.get_logger().warning(Logging.format(__file__, "NO ACK"))

	def send_receive_wrap(self, message_type, tup_message_params, f_ensure_ack=True, i_attempt=1):
		self.command_send_cb(self.connection.target_system, self.connection.target_component, message_type, i_attempt,
			*tup_message_params)
		msg = self.wrap_recv_match(f_ensure_ack, type='COMMAND_ACK')
		CommandLong.log_result(msg)

		return msg

	def arm(self, f_ensure_ack=True, i_attempt=0):
		Logging.info(__file__, "ARM")
		return self.send_receive_wrap(mavlink.MAV_CMD_COMPONENT_ARM_DISARM, (1, 0, 0, 0, 0, 0, 0,),
			f_ensure_ack=f_ensure_ack, i_attempt=i_attempt)

	def disarm(self, f_ensure_ack=True, i_attempt=0):
		Logging.info(__file__, "DISARM")
		return self.send_receive_wrap(mavlink.MAV_CMD_COMPONENT_ARM_DISARM, (0, 0, 0, 0, 0, 0, 0,),
			f_ensure_ack=f_ensure_ack, i_attempt=i_attempt)

	def takeoff(self, f_ensure_ack=True, i_attempt=0):
		Logging.info(__file__, "TAKEOFF")
		return self.send_receive_wrap(mavlink.MAV_CMD_NAV_TAKEOFF, (0, 0, 0, 0, 0, 0, 0,), f_ensure_ack=f_ensure_ack,
			i_attempt=i_attempt)

	def land(self, f_ensure_ack=True, i_attempt=0):
		Logging.info(__file__, "LAND")
		return self.send_receive_wrap(mavlink.MAV_CMD_NAV_LAND, (0, 0, 0, 0, 0, 0, 0,), f_ensure_ack=f_ensure_ack,
			i_attempt=i_attempt)
