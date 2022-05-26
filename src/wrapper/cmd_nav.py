import sys
import pathlib
from dataclasses import dataclass, field
from pymavlink.dialects.v20 import common
from pymavlink import mavutil

from pymavlink.dialects.v20.common import MAV_CMD_COMPONENT_ARM_DISARM

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


@dataclass
class CmdNav:
	mavlink_connection: object
	target_system: int = field(default_factory=int)
	target_component: int = field(default_factory=int)

	def arm_disarm_send_arm(self, confirmation=0):
		arm = 1
		msg = self.mavlink_connection.mav.command_long_encode(self.target_system, self.target_component,
			common.MAV_CMD_COMPONENT_ARM_DISARM, confirmation, arm, 0, 0, 0, 0, 0, 0)
		self.mavlink_connection.mav.send(msg)

	def arm_disarm_send_disarm(self, confirmation=0):
		arm = 0
		msg = self.mavlink_connection.mav.command_long_encode(self.target_system, self.target_component,
			common.MAV_CMD_COMPONENT_ARM_DISARM, confirmation, arm, 0, 0, 0, 0, 0, 0)
		self.mavlink_connection.mav.send(msg)

	def _cmd_ack_recv(self, command, timeout_seconds, block):
		msg = self.mavlink_connection.recv_match(type="COMMAND_ACK", blocking=block, timeout=timeout_seconds,
			condition=f"COMMAND_ACK.command == {command}")
		return msg

	def arm_disarm_ack_recv(self, timeout_seconds=1, block=True):
		return self._cmd_ack_recv(MAV_CMD_COMPONENT_ARM_DISARM, timeout_seconds, block)