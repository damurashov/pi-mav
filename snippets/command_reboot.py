from command import *


def _wait_for_ack(seconds=4, do_print=True):
	wait_for_message((mavcommon.MAVLINK_MSG_ID_COMMAND_ACK,), do_print=do_print, seconds=seconds)


if __name__ == "__main__":
	command_reboot(REBOOT_SHUTDOWN_RESTART_BOOTLOADER)
	_wait_for_ack()
