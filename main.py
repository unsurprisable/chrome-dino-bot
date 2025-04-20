import pyautogui
import time
from PIL import ImageOps

print("Open the game window! Starting 3 in seconds...")
time.sleep(3)

# region coordinates
left = 300
bottom = 570

# region bounds
width = 250
height = 1

region_bounds = (left, bottom-height, width, height)

# lastTime = time.time()

while True:
    region = pyautogui.screenshot(region=region_bounds)
    
    grayscale_region = ImageOps.grayscale(region)

    colors = grayscale_region.getcolors()

    print(f"Color data: {colors}")

    # if more than 1 color, theres an obstacle
    if len(colors) > 1:
        pyautogui.press("space")
        print("Jump!")

    time.sleep(0.05) 
    # print(f"Time Elapsed: {time.time() - lastTime}")
    # lastTime = time.time()
