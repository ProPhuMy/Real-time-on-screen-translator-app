import numpy as np
import cv2
import pyautogui
import gui
from gui import select_region
import time
import keyboard
import threading

global uptime
uptime = True

def on_hotkey():
    global coords
    gui.running = False
    print("\nCtrl+L pressed! Stopping screenshot monitoring...")
    print("Opening region selector...")
    time.sleep(0.5)  
    coords = select_region()
    if coords:
        print(f"New region selected: {coords}")
    else:
        print("No region selected. Exiting...")

keyboard.add_hotkey('ctrl+l', on_hotkey)  

if __name__ == "__main__":
    global coords
    coords = select_region()
    while uptime:
        while gui.running and coords:
            time.sleep(2)
            print("Taking screenshot...")
        time.sleep(0.1)
        if coords is None:
            break
