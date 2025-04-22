import time
import numpy as np
import cv2
from mss import mss
from pynput.keyboard import Controller
import os



def run_bot(game_region: tuple[int, int, int, int], skip_countdown=False):
    
    keyboard = Controller()
    sct = mss()

    # TODO: take screenshot of entire game area every frame and
    # use helper methods to look through the array pixels to make
    # the regions relative instead of all monitor-based

    # relative obstacle region
    obstacle_region = {
        "left": 145,
        "top": 205,
        "width": 160,
        "height": 10
    }

    target_loop_time = 1/30
    delta_time = 0
    last_time = time.time()

    # jump_cooldown = target_loop_time*3 # est. time before another jump would be needed
    time_since_jump = 0.0 
    jump_hold_time = 0.6 # time the bot should hold down space for max jump height
    is_jumping = False


    if not skip_countdown:
        print("Open the game window! Starting in 3 seconds...")
        time.sleep(3)

    keyboard.press(Controller._Key.space)
    keyboard.release(Controller._Key.space)

    pixels: np.ndarray = None
    def get_pixels(region: tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract a subregion of relative pixels from the main game capture.
        """
        top = region['top']
        left = region['left']
        height = region['height']
        width = region['width']

        return pixels[top:top+height, left:left+width]

    while True:
        current_time = time.time()
        delta_time = time.time() - last_time
        last_time = time.time()
        time_since_jump += delta_time

        frame = np.array(sct.grab(game_region))
        pixels = np.array(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))

        if not is_jumping:
            frame = get_pixels(obstacle_region)

            # find unique pixel colors
            unique = np.unique(frame)

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
            
        loop_time = time.time() - current_time

        # ensure maximum framerate
        if loop_time < target_loop_time:
            time.sleep(target_loop_time - loop_time)
        print(f"Time: {time.time() - current_time}")



def game_capture(draw=False):
    sct = mss()
    monitor = sct.monitors[1] # primary monitor

    countdown = 3
    while (countdown > 0):
        print(f"Screenshotting in {countdown} seconds... trigger the blue border around the dino game!")
        time.sleep(1)
        countdown -= 1

    screenshot = np.array(sct.grab(monitor))
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

    # color range for detecting the blue bounding box
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest = sorted(contours, key=cv2.contourArea, reverse=True)[0]
    x, y, w, h = cv2.boundingRect(largest)

    padding = 6
    x += padding
    y += padding
    w -= 2 * padding
    h -= 2 * padding

    print(f"\nDino game bounding box found at:\nx: {x}, y: {y}\nw: {w}, h: {h}")

    with open("bounds.txt", "w") as file:
        file.write(f"{x} {y} {w} {h}")
    
    if draw:
        cv2.rectangle(screenshot, (x-2, y-2), (x + w+2, y + h+2), (0, 255, 0), 3)

        cv2.namedWindow("Detected", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Detected", cv2.WND_PROP_TOPMOST, 1)

        cv2.imshow("Detected", screenshot)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()



if __name__ == "__main__":
    skip_countdown = False
    if not os.path.exists("bounds.txt"):
        print("Bounds file not found. Running bounds setup...")      
        game_capture(draw=True)
        print("Setup complete.\n")
        skip_countdown = True
        time.sleep(0.5)

    game_region = None
    with open("bounds.txt", "r") as file:
        values = list(map(lambda str: int(str), file.read().split()))
        game_region = {"left": values[0], "top": values[1], "width": values[2], "height": values[3]}
    print(game_region, end="\n\n")
    run_bot(game_region, skip_countdown=skip_countdown)