import numpy as np
import cv2
import pyautogui
import gui
from gui import select_region
import time
import keyboard
import easyocr

global count
count = 0 
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
        print("No region selected. Exiting")

keyboard.add_hotkey('ctrl+l', on_hotkey)  

def take_image(coords):
    x, y, w, h = coords
    image = pyautogui.screenshot(region=(x,y,w,h))
    return image

def convert_image(image):
    img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    return img

#return true if image has changed, else return false
def compare_images(img1, img2, threshold=5000):    
    #calculate MSE
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img2.shape[1])
    if err > threshold:
        global count
        count = 0
        return True
    return False

class OCR:
    def __init__(self, langlist = ['ja', 'en']):
        self.reader = easyocr.Reader(langlist)
    
    #too lazy to implement manual reset at the moment, will implement later if want :)
    def reset(self):
        global count
        count = 0

    def extract_text(self, img):
        global count
        if count != 0:
            return None
        result = self.reader.readtext(img)
        count += 1
        return result

if __name__ == "__main__":
    coords = select_region()
    while True:
        while gui.running and coords:
            print("Taking screenshot...")
            img1 = convert_image(take_image(coords))
            time.sleep(2)
            img2 = convert_image(take_image(coords))
            if (compare_images(img1, img2)):
                print("yeah baby")
        time.sleep(0.1)
        if coords is None:
            break