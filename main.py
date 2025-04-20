import pyautogui
import time
from PIL import ImageOps

print("Open the game window! Starting 3 in seconds...")
time.sleep(3)

# region coordinates
left = 233
bottom = 542

# region bounds
width = 317
height = 10

region_bounds = (left, bottom-height, width, height)

jump_cooldown = 0.20 # est. time before another jump would be needed
time_since_jump = 0.0

target_delta_time = 0.05
delta_time = 0
last_time = time.time()

while True:

    delta_time = time.time() - last_time
    last_time = time.time()

    colors: list[tuple[int, int]] = None

    if time_since_jump >= jump_cooldown:
        region = pyautogui.screenshot(region=region_bounds)
        grayscale_region = ImageOps.grayscale(region)
        colors = grayscale_region.getcolors()

    print(f"Data: {colors}")
    print(f"added time: {delta_time}")

    time_since_jump += delta_time

    # if more than 1 color, theres an obstacle
    if colors != None and len(colors) > 1:
        pyautogui.press("space")
        print("Jump!")
        time_since_jump = 0
        
    delta_time = time.time() - last_time

    # ensure maximum framerate
    if delta_time < target_delta_time:
        time.sleep(target_delta_time - delta_time)


# while True:
#     delta_time = time.time() - last_time

#     time_since_jump += delta_time

#     if time_since_jump >= jump_cooldown:
#         pyautogui.press("space")
#         print(f"Jump! {time_since_jump}")
#         time_since_jump = 0

#     last_time = time.time()