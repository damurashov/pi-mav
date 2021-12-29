from command import *
from generic import set_position_target_local_ned

if __name__ == "__main__":
	print('arm')
	command_arm(True)
	time.sleep(2)

	input()
	print('takeoff')
	command_takeoff()
	time.sleep(10)

	print('go to local point')
	set_position_target_local_ned(y=1)
	time.sleep(10)


	print('land')
	command_land()
	time.sleep(10)