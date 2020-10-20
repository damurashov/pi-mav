from ftp import *
from command import *
import serial

if __name__ == "__main__":
	ser = serial.Serial('/dev/ttyUSB0', 115200)
	# msg = mav.vision_position_estimate_encode(1, 2, 3, 4, 5, 6, 7)
	# ser.write(msg.pack(mav))
	msg = mav.vision_speed_estimate_encode(1, 2, 3, 4)
	ser.write(msg.pack(mav))
	# ftp_write_file(3)
	# ftp_list()
	# ftp_write_file()
	# ftp_read_file()
	# ftp_list()
	# command_lua_run()