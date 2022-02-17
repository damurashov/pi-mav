from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))  # We need files from "src/", that's how we access them

from wrapper import geoscan_mavlink
import tkinter as tk
import threading

RC_CHANNELS_PERIOD_MS = 50


class ButtonFrame(tk.Frame):

	def manual_control_task(self):

	def __init__(self, master, *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)

		stub = lambda x, y, z, w: None
		self.on_set_pos_frame = kwargs.pop("set_pos_frame", stub)
		self.on_set_pos_local = kwargs.pop("set_pos_local", stub)
		self.on_set_vel_local = kwargs.pop("set_vel_local", stub)
		self.on_set_vel_frame = kwargs.pop("set_vel_frame", stub)
		self.on_arm = kwargs.pop("arm", stub)
		self.on_disarm = kwargs.pop("disarm", stub)

		self.x = 0
		self.y = 0
		self.z = 0
		self.w = 0

		self.nav_mode = tk.StringVar()
		w_mode = tk.OptionMenu(self, self.nav_mode, "rc", "set_pos_local", "set_pos_frame", "set_vel_local", "set_vel_frame")

		self.rc_mode = tk.IntVar()
		rc_mode = tk.OptionMenu(self, self.rc_mode, 1, 2, 3, 4, 5)

		w_btns = tk.Frame(self)
		w_btn_n = tk.Button(w_btns, text="N")


class Gui(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(*args, **kwargs)