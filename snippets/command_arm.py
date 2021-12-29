from connectivity import *
from command import *
from generic import *
import threading
import tkinter as tk
import math
import time

flag_rc_thread = True


def task_rc_thread():
	global rc_thread

	print("msg_rc_channels_override -- launched")
	msg = mav.rc_channels_override_encode(1, 1, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500)
	msg = msg.pack(mav)
	while flag_rc_thread:
		send(msg)
		time.sleep(0.05)


rc_thread = threading.Thread(target=task_rc_thread)


def run_rc_thread(run: bool = True):
	global flag_rc_thread
	global rc_thread

	is_alive = rc_thread.is_alive()
	action_required = is_alive is not run

	if not action_required:
		print(f"[RC thread] already {'running' if run else 'stopped'}")
		return

	if run:
		flag_rc_thread = True
		rc_thread.start()
		print("[RC thread] running")
	else:
		flag_rc_thread = False
		rc_thread.join()

		del rc_thread
		rc_thread = threading.Thread(target=task_rc_thread)
		print("[RC thread] stopped")


def msg_arm(arm: bool):
	msg = mav.command_long_encode(123, 123, mavcommon.MAV_CMD_COMPONENT_ARM_DISARM, 0, int(arm), 0, 0, 0, 0, 0, 0)
	return msg.pack(mav)


def cb_arm(arm: bool):
	send(msg_arm(arm))


def wait_msg():
	while True:
		wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT,
			mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,),
			do_print=True,
			seconds=1
		)


STEP_HORIZONTAL = 1
STEP_VERTICAL = 0.3
f_use_body_frame = True


def bind_set_vel(x=0, y=0, z=0, yaw=0, seconds=1):
	print("bind set vel. <x,y,z,w>: <%f, %f, %f, %f>" % (x, y, z, yaw,))
	period_ms = 20
	start = time.time()

	while time.time() < start + seconds:
		set_position_target_local_ned(vx=x, vy=y, vz=z, yaw_rate=yaw,
			frame=mavcommon.MAV_FRAME_BODY_FRD if f_use_body_frame else mavcommon.MAV_FRAME_LOCAL_NED, vx_ignore=0,
			vy_ignore=0, vz_ignore=0, yaw_rate_ignore=0)
		time.sleep(period_ms / 1000)


def bind_set_pos(x=0, y=0, z=0, yaw=0):
	print("bind set pos. <x,y,z,w>: <%f, %f, %f, %f>" % (x, y, z, yaw,))
	set_position_target_local_ned(x=x, y=y, z=z, yaw=yaw,
		frame=mavcommon.MAV_FRAME_BODY_FRD if f_use_body_frame else mavcommon.MAV_FRAME_LOCAL_NED, x_ignore=0, y_ignore=0,
		z_ignore=0, yaw_ignore=0)


bind = bind_set_vel


def bind_to_set_vel():
	global bind
	print("as set vel")
	bind = bind_set_vel


def bind_to_set_pos():
	global bind
	print("as set pos")
	bind = bind_set_pos


def toggle_body_frame():
	global f_use_body_frame
	f_use_body_frame = not f_use_body_frame
	print(f"Use body frame: {f_use_body_frame}")


def get_gui():
	global bind
	root = tk.Tk()

	main_frame = tk.Frame(root)
	arm_btn = tk.Button(main_frame, text="Arm", command=lambda: cb_arm(True))
	disarm_btn = tk.Button(main_frame, text="Disarm", command=lambda: cb_arm(False))
	run_rc_thread_btn = tk.Button(main_frame, text="Run RC thread", command=lambda: run_rc_thread(True))
	stop_rc_thread_btn = tk.Button(main_frame, text="Stop RC thread", command=lambda: run_rc_thread(False))
	takeoff_btn = tk.Button(main_frame, text="Takeoff", command=lambda: command_takeoff())
	land_btn = tk.Button(main_frame, text="Land", command=lambda: command_land())

	for b in [arm_btn, disarm_btn, run_rc_thread_btn, stop_rc_thread_btn, takeoff_btn, land_btn]:
		b.pack(fill=tk.X)

	goto_frame = tk.Frame(root)
	up_goto_btn = tk.Button(goto_frame, text="Up", command=lambda: bind(z=.3))
	down_goto_btn = tk.Button(goto_frame, text="Down", command=lambda: bind(z=-.3))
	left_goto_btn = tk.Button(goto_frame, text="Left", command=lambda: bind(x=-1))
	right_goto_btn = tk.Button(goto_frame, text="Right", command=lambda: bind(x=1))
	fwd_goto_btn = tk.Button(goto_frame, text="Fwd", command=lambda: bind(y=1))
	back_goto_btn = tk.Button(goto_frame, text="Back", command=lambda: bind(y=-1))
	yawi_goto_btn = tk.Button(goto_frame, text="Yaw+", command=lambda: bind(yaw=math.pi / 2))
	yawd_goto_btn = tk.Button(goto_frame, text="Yaw-", command=lambda: bind(yaw=-math.pi / 2))
	switch_pos_btn = tk.Button(goto_frame, text="Switch set pos.", command=lambda: bind_to_set_pos())
	switch_vel_btn = tk.Button(goto_frame, text="Switch set vel.", command=lambda: bind_to_set_vel())
	toggle_body_frame_btn = tk.Button(goto_frame, text="Toggle body frame", command=lambda: toggle_body_frame())

	yawd_goto_btn.pack(side=tk.LEFT, fill=tk.X)
	left_goto_btn.pack(side=tk.LEFT, fill=tk.X)
	yawi_goto_btn.pack(side=tk.RIGHT, fill=tk.X)
	right_goto_btn.pack(side=tk.RIGHT, fill=tk.X)
	up_goto_btn.pack(fill=tk.X)
	fwd_goto_btn.pack(fill=tk.X)
	back_goto_btn.pack(fill=tk.X)
	down_goto_btn.pack(fill=tk.X)
	switch_pos_btn.pack(fill=tk.X)
	switch_vel_btn.pack(fill=tk.X)
	toggle_body_frame_btn.pack(fill=tk.X)

	goto_frame.pack()
	main_frame.pack()

	return root


if __name__ == "__main__":
	t = threading.Thread(target=wait_msg)
	t.start()

	gui_tk = get_gui()

	gui_tk.mainloop()
