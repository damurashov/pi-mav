#!/usr/bin/python3

"""
Implements the same functionality as WASD_flight. The difference is
that this script is capable of reading keyboard values in background,
so we don't have to keep input focus on an opencv window.

On nix-es, it must be launched with root privileges.

Controls:

W :  +Y
S :  -Y
A :  -X
D :  +X

Q :  -Yaw
E :  +Yaw

Shift + W :  +Z
Shift + S :  -Z

Ctrl + A : Arm
Ctrl + D : Disarm
Ctrl + W : Takeoff
Ctrl + S : Land
"""

from pioneer_sdk import Pioneer
import cv2
import math
import numpy as np
import keyboard
from command import command_arm, command_takeoff, command_land


class Control(Pioneer):

    def __init__(self, *args, **kwargs):
        Pioneer.__init__(self, *args, **kwargs)

        self.pos = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'w': math.radians(0.0)}

    def reset(self):
        for k in self.pos.keys():
            self.pos[k] = 0

    def step(self, key, step):
        assert key in self.pos.keys()
        self.pos[key] = step
        self.go_to_local_point(x=self.pos['x'], y=self.pos['y'], z=self.pos['z'], yaw=self.pos['w'])
        self.reset()


if __name__ == '__main__':

    # Every control command decreases/increases position
    STEP_XY = 0.2
    STEP_Z = 0.1
    STEP_Z = 0.1
    STEP_Z = 0.1
    STEP_Z = 0.1
    ddSTEP_Z = 0.1
    STEP_YAW = math.radians(float(45))

    pioneer_mini = Control()

    keyboard.add_hotkey("ctrl+a", command_arm, args=(True,))
    keyboard.add_hotkey("ctrl+d", command_arm, args=(False,))
    keyboard.add_hotkey("ctrl+w", command_takeoff)
    keyboard.add_hotkey("ctrl+s", command_land)

    keyboard.add_hotkey('a', pioneer_mini.step, args=('x', -STEP_XY,))
    keyboard.add_hotkey('d', pioneer_mini.step, args=('x', +STEP_XY,))
    keyboard.add_hotkey('s', pioneer_mini.step, args=('y', -STEP_XY,))
    keyboard.add_hotkey('w', pioneer_mini.step, args=('y', +STEP_XY,))
    keyboard.add_hotkey('q', pioneer_mini.step, args=('w', -STEP_YAW,))
    keyboard.add_hotkey('e', pioneer_mini.step, args=('w', +STEP_YAW,))

    keyboard.add_hotkey('shift+s', pioneer_mini.step, args=('z', -STEP_Z,))
    keyboard.add_hotkey('shift+w', pioneer_mini.step, args=('z', +STEP_Z,))

    # pioneer_mini.step('x', 0)  # Trigger setting of the initial position (0, 0, 1)

    while True:
        try:
            camera_frame = pioneer_mini.get_raw_video_frame()
            if camera_frame is not None:
                camera_frame = cv2.imdecode(np.frombuffer(camera_frame, dtype=np.uint8), cv2.IMREAD_COLOR)

            cv2.imshow('pioneer_camera_stream', camera_frame)

            if cv2.waitKey(1) == 27:  # esc
                break
        except:
            pass
