import pyautogui
import time


print("Tracking mouse cursor... Ctrl+C to quit")

while True:
    x, y = pyautogui.position()

    print(f"Mouse position: ({x}, {y})       ", end="\r")

    time.sleep(0.1)