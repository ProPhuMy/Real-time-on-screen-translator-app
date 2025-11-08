import numpy as np
import cv2
import pyautogui
import time
import easyocr

def take_image(coords):
    x, y, w, h = coords
    image = pyautogui.screenshot(region=(x,y,w,h))
    return image

def convert_image(image):
    img = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    return img

#return true if image has changed, else return false
def compare_images(img1, img2, threshold=1000):    
    #calculate MSE
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img2.shape[1])
    if err > threshold:
        return True
    return False

class OCR:
    def __init__(self, langlist = ['ja', 'en']):
        self.reader = easyocr.Reader(langlist)
    
    def extract_text(self, img):
        result = self.reader.readtext(img)
        return result

