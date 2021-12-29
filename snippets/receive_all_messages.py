from connectivity import wait_for_message, send
from connectivity import mavcommon

if __name__ == "__main__":
	while True:
		send(b'geoscan')
		wait_for_message(None, seconds=1, do_print=True)
		# wait_for_message(None, seconds=1, do_print=True)