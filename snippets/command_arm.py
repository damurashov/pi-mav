from connectivity import *
import threading
import tkinter as tk

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
	wait_for_message((mavcommon.MAVLINK_MSG_ID_NAMED_VALUE_INT,
		mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,),
		do_print=True,
		seconds=3,
		# return_strategy='return-unique'
	)

def get_gui():
	root = tk.Tk()

	main_frame = tk.Frame(root)
	arm_btn = tk.Button(main_frame, text="Arm", command=lambda: cb_arm(True))
	disarm_btn = tk.Button(main_frame, text="Disarm", command=lambda: cb_arm(False))
	run_rc_thread_btn = tk.Button(main_frame, text="Run RC thread", command=lambda: run_rc_thread(True))
	stop_rc_thread_btn = tk.Button(main_frame, text="Stop RC thread", command=lambda: run_rc_thread(False))

	arm_btn.pack()
	disarm_btn.pack()
	run_rc_thread_btn.pack()
	stop_rc_thread_btn.pack()
	main_frame.pack()

	return root


if __name__ == "__main__":
	gui_tk = get_gui()

	gui_tk.mainloop()
