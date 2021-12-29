from generic import manual_control
from command import command_arm, command_lua_run
from connectivity import wait_for_message, mavcommon
import tkinter as tk
import threading


def clamp(v, v_min, v_max):
	assert v_min < v_max
	return max(v_min, min(v_max, v))


def recv_messages():
	msgs = [
		mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT,
		mavcommon.MAVLINK_MSG_ID_COMMAND_ACK
	]
	while True:
		wait_for_message(msgs, do_print=True, seconds=60)


class Stick:
	PITCH = "pitch"
	ROLL = "roll"
	YAW = "yaw"
	THROTTLE = "throttle"

	MAX = 1.0
	MIN = -1.0
	MID = 0.0
	STEP = 0.1

	@staticmethod
	def normalize(stick_val):
		return clamp(stick_val, Stick.MIN, Stick.MAX)


def dbg_print_event_info(event: tk.Event):
	if 0:
		return

	info = lambda k: print(f'"{str(k)}" of type {str(type(k))}')
	info(event)
	info(event.type)
	info(event.state)
	info(event.keycode)
	info(event.keysym)
	print('---')


class MavlinkControl:

	def __init__(self):
		self.sticks = {
			Stick.PITCH: Stick.MID,  # x
			Stick.ROLL: Stick.MID,  # y
			Stick.THROTTLE: Stick.MID,  # z
			Stick.YAW: Stick.MID  # r
		}
		self.mode = 0

	def send_manual_control(self):

		def normalize(v):
			return int(clamp(Stick.normalize(v) * 1000, -1000, 1000))  # See MAVLink, MANUAL_CONTROL (#69)

		args = tuple([normalize(v) for v in self.sticks.values()]) + (int(self.mode),)
		manual_control(*args)

	def arm(self, f: bool):
		command_arm(f)

	def lua(self, f_run):
		command_lua_run(f_run)


class KbController(tk.Tk, MavlinkControl):

	CONTROL_SEND_PERIOD_MS = 40

	MOD_NONE = 0
	MOD_SHIFT = 1

	def __init__(self):
		tk.Tk.__init__(self)
		MavlinkControl.__init__(self)

		self.bind("<KeyPress>", self.kb)
		self.bind("<KeyRelease>", self.kb)

	def normalize_sticks(self):
		for k, v in self.sticks:
			self.sticks[k] = Stick.normalize(self.sticks[k])

	def is_manual_throttle(self):
		return self.mode == 0

	def reset_sticks(self):
		thr = self.sticks[Stick.THROTTLE]

		for k, v in self.sticks:
			self.sticks[k] = Stick.MID

		# Restore throttle
		if self.is_manual_throttle():
			self.sticks[Stick.THROTTLE] = thr

	@staticmethod
	def get_kb_modifier(event: tk.Event):
		if event.state & 0x0001:
			return KbController.MOD_SHIFT
		else:
			return KbController.MOD_NONE

	def kb_arrows(self, event: tk.Event):
		def set_max(x):
			return Stick.MAX

		def set_min(x):
			return Stick.MIN

		def decr(x):
			return Stick.normalize(x - Stick.STEP)

		def incr(x):
			return Stick.normalize(x + Stick.STEP)

		callables = {
			KbController.MOD_NONE: {
				"Right": [Stick.ROLL, set_max],
				"Left": [Stick.ROLL, set_min],
				"Up":  [Stick.PITCH, set_max],
				"Down": [Stick.PITCH, set_min],
			},
			KbController.MOD_SHIFT: {
				"Right": [Stick.YAW, set_max],
				"Left": [Stick.YAW, set_min],
				"Up": [Stick.THROTTLE, set_max if self.is_manual_throttle() else incr],
				"Down": [Stick.THROTTLE, set_min if self.is_manual_throttle() else decr]
			}
		}

		mode = KbController.get_kb_modifier(event)
		if event.type == tk.EventType.KeyPress:
			stick_name, cbl = callables[mode][event.keysym]
			self.sticks[stick_name] = cbl(stick_name)
		else:
			self.reset_sticks()

	def kb(self, event: tk.Event):
		dbg_print_event_info(event)

		callables_run = {
			KbController.MOD_NONE: [command_arm, (event.keysym == "Return",)],
			KbController.MOD_SHIFT: [command_lua_run, (event.keysym == "Return",)]
		}

		if event.keysym in {"Up", "Down", "Left", "Right"}:
			self.kb_arrows(event)
			return

		if event.keysym in ["Return", "Escape"] and event.type == tk.EventType.KeyPress:
			cb, args = callables_run[KbController.get_kb_modifier(event)]
			cb(*args)
			return

		if event.keysym in ['0', '1', '2'] and event.type == tk.EventType.KeyPress:
			self.mode = int(event.keysym)


if __name__ == "__main__":
	t = threading.Thread(target=recv_messages)
	t.start()

	controller = KbController()
	controller.after(KbController.CONTROL_SEND_PERIOD_MS, controller.send_manual_control)
	controller.mainloop()