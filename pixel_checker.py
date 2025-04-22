import pyautogui
import time
import os


print("Tracking mouse cursor... Ctrl+C to quit")

if not os.path.exists("bounds.txt"):
    print("bounds.txt does not exist!")
    exit()

game_region = None
with open("bounds.txt", "r") as file:
    values = list(map(lambda str: int(str), file.read().split()))
    game_region = {"left": values[0], "top": values[1], "width": values[2], "height": values[3]}

left = game_region['left']
top = game_region['top']

while True:
    x, y = pyautogui.position()

    print(f"Mouse position: ({max(0, x-left)}, {max(0, y-top)})       ", end="\r")

    time.sleep(0.1)