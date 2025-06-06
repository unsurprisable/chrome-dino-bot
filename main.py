import time
import numpy as np
import cv2
from mss import mss
from pynput.keyboard import Controller
import os

# 84,013 high score but it's because i didn't have time to run it longer
# i honestly think it can go forever if the speed gets capped at 99,999 score

def run_bot(game_region: tuple[int, int, int, int], skip_countdown=False):
    keyboard = Controller()
    sct = mss()

    # relative obstacle region
    obstacle_region = {
        "left": 145,
        "top": 210,
        "width": 160,
        "height": 7
    }

    feet_region = {
        "left": 48,
        "top": 265,
        "width": 27,
        "height": 9
    }

    jump_region = {
        "left": 69,
        "top": 0,
        "width": 1,
        "height": 170
    }

    duck_region = {
        "left": 70,
        "top": 171,
        "width": 140,
        "height": 81
    }

    ground_region = {
        "left": 0,
        "top": 262,
        "width": game_region["width"],
        "height": 2
    }

    game_over_region = {
        "left": 410,
        "top": 85,
        "width": 380,
        "height": 20
    }

    duckable_bird_region = {
        "left": 0,
        "top": 179,
        "width": obstacle_region["left"] + obstacle_region["width"],
        "height": 1
    }
    

    target_loop_time = 1/30
    delta_time = 0

    run_time = 0.0
    time_since_jump = 0.0
    game_over_check_delay = 1.0 # how often (seconds) to check if the game is over
    time_since_game_over_check = 0.0
    is_grounded_delay = 0.15 # time to wait after jumping in order to ensure the dino is in the air by the time "is_grounded" is checked for
    frames_since_grounded = 0 # amount of frames the dino has been grounded for
    is_grounded = True
    is_ducking = False

    def check_for_game_over(dino_color: int):
        frame = get_pixels(game_over_region)
        pixels, counts = np.unique(frame, return_counts=True)
        pixel_map = dict(zip(pixels, counts))  

        game_over_pixel_threshold = 500
        if dino_color in pixel_map and pixel_map[dino_color] >= game_over_pixel_threshold:
            print("Game over! :(\n-----------------------------")
            exit()

    if not skip_countdown:
        countdown = 3
        while countdown > 0:
            print(f"Open the game window! Starting in {countdown} seconds...")
            time.sleep(1)
            countdown -= 1

    keyboard.press(Controller._Key.space)
    keyboard.release(Controller._Key.space)

    game_pixel_array: np.ndarray = None
    def get_pixel(x: int, y: int) -> int:
        """
        Extract a single relative pixel's grayscale color value.
        """
        return game_pixel_array[y, x]
    
    def get_pixels(region: tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract a subregion of relative pixels from the main game capture.
        """
        top = region['top']
        left = region['left']
        height = region['height']
        width = region['width']

        return game_pixel_array[top:top+height, left:left+width]

    last_time = time.time()

    while True:
        current_time = time.time()
        delta_time = time.time() - last_time
        last_time = time.time()

        run_time += delta_time
        time_since_jump += delta_time
        time_since_game_over_check += delta_time

        frame = np.array(sct.grab(game_region))
        game_pixel_array = np.array(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))

        sky_color = get_pixel(0, 0)
        dino_color = np.argmax(np.bincount(get_pixels(ground_region).flatten()))
        # 1077, 21

        if is_grounded:
            frames_since_grounded += 1

            # check for duckable bird
            frame = get_pixels(duckable_bird_region)
            unique = np.unique(frame)

            if not is_ducking and len(unique) > 1:
                print("DUCK!!!")
                keyboard.press(Controller._Key.down)
                is_ducking = True
            
            if is_ducking and len(unique) == 1:
                keyboard.release(Controller._Key.down)
                is_ducking = False

            if not is_ducking:
                frame = get_pixels(obstacle_region)

                # find unique pixel colors
                unique = np.unique(frame)

                print(f"Unique shades: {len(unique)}, Time: {delta_time}")

                # avoid accidentally jumping before the game registers that the dino can jump again
                min_grounded_frames_to_jump = 2

                # if theres more than 1 color, there must be an obstacle
                if len(unique) > 1 and frames_since_grounded >= min_grounded_frames_to_jump:
                    check_for_game_over(dino_color) # check if the game is over before accidentally hitting space and restarting it
                    keyboard.press(Controller._Key.space)
                    print("jumpy")
                    time_since_jump = 0
                    is_grounded = False
                    frames_since_grounded = 0

        elif time_since_jump >= is_grounded_delay:
            feet_detected = False
            airborne_dino_detected = False

            # first, check if the dino feet region is satisfied
            frame = get_pixels(feet_region)

            pixels, counts = np.unique(frame, return_counts=True)
            pixel_map = dict(zip(pixels, counts))

            # more than just bg pixels
            if len(pixel_map) > 1:

                # number of pixels in the region that need to not be bg pixels in order to correctly assume the dino's feet are there
                non_bg_pixel_threshold = 60
                non_bg_pixels = 0
                for pixel, count in enumerate(pixel_map):
                    if pixel != sky_color: 
                        non_bg_pixels += count
                
                if non_bg_pixels >= non_bg_pixel_threshold:
                    feet_detected = True

            # now check if the dino is in the air or not to differentiate it from a cactus
            # if feet_detected:
            frame = get_pixels(jump_region)

            dino_pixel_threshold = 25 # to avoid birds causing false positives
            dino_pixels = np.count_nonzero(frame == dino_color)

            if dino_pixels >= dino_pixel_threshold:
                airborne_dino_detected = True

            print(f"{feet_detected=}{' ' if feet_detected else ''} | {airborne_dino_detected=}")
            
            if feet_detected and not airborne_dino_detected:
                keyboard.release(Controller._Key.space)
                print("\nHE REACHED THE GROUND SAFELY YAY!!!!!!!\n")
                is_grounded = True
                if is_ducking:
                    keyboard.release(Controller._Key.down)
                    is_ducking = False

            frame = get_pixels(duck_region)

            unique = np.unique(frame)

            if not is_ducking and airborne_dino_detected and len(unique) == 1:
                print("DUCK!!!")
                keyboard.press(Controller._Key.down)
                is_ducking = True

        if time_since_game_over_check >= game_over_check_delay:
            check_for_game_over(dino_color)
            time_since_game_over_check = 0

        loop_time = time.time() - current_time

        # ensure maximum framerate
        if loop_time < target_loop_time:
            time.sleep(target_loop_time - loop_time)
        # print(f"Time: {time.time() - current_time}")



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