import gui
from gui import select_region
import time
import screenshot as sc
from screenshot import OCR
import translate as ts
import threading

def main():
    coords = select_region()
    reader = OCR()
    while True:
        while gui.running and coords:
            print("Taking screenshot...")
            img1 = sc.convert_image(sc.take_image(coords))
            time.sleep(2)
            img2 = sc.convert_image(sc.take_image(coords))
            if (sc.compare_images(img1, img2)):
                result = reader.extract_text(img2)
            else:
                result = reader.extract_text(img1)
    
            if result == None:
                continue
            print(ts.translate_text(ts.process_text_for_api(result)))
        time.sleep(0.1)
        if (gui.has_exit):
            break
def has_exit():
    pass

if __name__ == "__main__":
    main()