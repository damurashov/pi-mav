from generic import manual_control
from command import command_arm
import tkinter as tk


class KbController(tk.Tk):
	MIN = -1000
	MAX = 1000

	MODE_STABILIZE = 0
	MODE_ALTHOLD = 1
	MODE_NAVIGATION = 2

	CONTROL_SEND_PERIOD_MS = 40

	def __init__(self):
		super().__init__()

		self.x = 0
		self.y = 0
		self.z = 0
		self.r = 0
		self.buttons = 0

		self.bind("<KeyPress>", self.kb)
		self.bind("<KeyRelease>", self.reset)

	def reset(self, *argv):
		self.x = 0
		self.y = 0
		self.z = 0
		self.r = 0

	def kb(self, event: tk.Event):
		# info = lambda k: print(f'"{str(k)}" of type {str(type(k))}')
		info = lambda k: None
		info(event)
		info(event.type)
		info(event.state)
		info(event.keycode)
		info(event.keysym)

		if event.type == tk.EventType.KeyPress:
			if event.state & 0x0001:  # Shift
				if event.keysym == "Right":
					self.r = KbController.MAX
				elif event.keysym == "Left":
					self.r = KbController.MIN
				elif event.keysym == "Up":
					self.z = KbController.MAX
				elif event.keysym == "Down":
					self.z = KbController.MIN
			else:
				if event.keysym == "Right":
					self.y = KbController.MAX
				elif event.keysym == "Left":
					self.y = KbController.MIN
				elif event.keysym == "Up":
					self.x = KbController.MAX
				elif event.keysym == "Down":
					self.x = KbController.MIN
				elif event.keysym == "Return":
					command_arm(True)
				elif event.keysym == "Escape":
					command_arm(False)
				elif event.keysym in ['0', '1', '2']:
					self.buttons = int(event.keysym)
					print(f'Mode: {self.buttons & 0b11}')
		elif event.type == tk.EventType.KeyRelease:
			self.reset()

	def send(self):
		manual_control(self.x, self.y, self.z, self.r, self.buttons)
		self.after(KbController.CONTROL_SEND_PERIOD_MS, self.send)


if __name__ == "__main__":
	controller = KbController()
	controller.after(KbController.CONTROL_SEND_PERIOD_MS, controller.send)
	controller.mainloop()