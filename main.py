import numpy as np
import cv2
import pyautogui
import gui
from gui import select_region
import time
import screenshot as sc
import translate as ts

if __name__ == "__main__":
    coords = select_region()
    while True:
        while gui.running and coords:
            print("Taking screenshot...")
            img1 = sc.convert_image(sc.take_image(coords))
            time.sleep(2)
            img2 = sc.convert_image(sc.take_image(coords))
        time.sleep(0.1)
        if coords is None:
            break