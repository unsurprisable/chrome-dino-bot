import time
import numpy as np
import cv2
from mss import mss
from pynput.keyboard import Controller



def run_bot():
    keyboard = Controller()
    sct = mss()

    # TODO: take screenshot of entire game area every frame and
    # use helper methods to look through the array pixels to make
    # the regions relative instead of all monitor-based

    # screenshot region
    obstacle_region = {
        "top": 532,
        "left": 233,
        "width": 237,
        "height": 10
    }

    # grounded_region = {
    #     "top": 594,
    #     "left": 169,
    #     "width": 25,
    #     "height": 8
    # }

    # sky_color_region = {
    #     "top": 700,
    #     "left": 1350,
    #     "width": 1,
    #     "height": 1
    # }

    target_loop_time = 1/30
    delta_time = 0
    last_time = time.time()

    # jump_cooldown = target_loop_time*3 # est. time before another jump would be needed
    time_since_jump = 0.0 
    jump_hold_time = 0.6 # time the bot should hold down space for max jump height
    is_jumping = False

    print("Open the game window! Starting in 2 seconds...")
    time.sleep(2)

    keyboard.press(Controller._Key.space)
    keyboard.release(Controller._Key.space)

    while True:
        current_time = time.time()
        delta_time = time.time() - last_time
        last_time = time.time()
        time_since_jump += delta_time

        if not is_jumping:
            frame = np.array(sct.grab(obstacle_region)) 
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # find unique pixel colors
            unique = np.unique(gray)

            print(f"Unique shades: {len(unique)}")

            # if theres more than 1 color, there must be an obstacle
            if len(unique) > 1:
                keyboard.press(Controller._Key.space)
                print("Jump!")
                time_since_jump = 0
                is_jumping = True

        elif time_since_jump >= jump_hold_time:
            keyboard.release(Controller._Key.space)
            is_jumping = False
        
        # else:
        #     frame = np.arange(sct.grab(grounded_region))
        #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #     color_map = np.
            
        loop_time = time.time() - current_time

        # ensure maximum framerate
        if loop_time < target_loop_time:
            time.sleep(target_loop_time - loop_time)
        print(f"Time: {time.time() - current_time}")




if __name__ == "__main__":
    run_bot()