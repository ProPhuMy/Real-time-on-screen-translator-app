import gui
from gui import select_region
import screenshot as sc
from screenshot import OCR
import translate as ts
from overlay import TransparentFramelessWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys
from google import genai

overlay = None
reader = None
client = None
previous_img = None
coords = None


def take_screenshot_and_translate():
    global overlay, reader, client, previous_img, coords, timer
    
    if overlay is None or coords is None:
        return
    
    # Check if user requested region change
    if not gui.running:
        timer.stop()
        handle_region_change()
        if coords is not None:
            timer.start(2000)
        return
    
    if gui.has_exit:
        app.quit()
        return
    
    try:
        # Hide overlay before screenshot
        overlay.hide()
        QApplication.processEvents()  # Force Qt to process the hide
        
        # Take screenshot
        print("Taking screenshot...")
        img2 = sc.convert_image(sc.take_image(coords))
        
        # Show overlay again
        overlay.show()
        
        # First screenshot or image has changed
        if previous_img is None or sc.compare_images(previous_img, img2):
            result = reader.extract_text(img2)
            
            if result is not None and len(result) > 0:
                translated = ts.translate_text(result, client)
                
                if translated is not None and len(translated) > 0:
                    previous_img = img2
                    overlay.reset_labels()
                    overlay.create_labels(translated)
                    
    except Exception as e:
        print(f"Error in screenshot/translate: {e}")
        overlay.show()  # Make sure overlay is visible even if error


def handle_region_change():
    global overlay, coords, previous_img
    
    if overlay is not None:
        overlay.close()
        overlay = None
    
    new_coords = select_region()
    print(new_coords)
    if new_coords is None:
        app.quit()
        return
    
    coords = new_coords
    previous_img = None
    
    # Create new overlay
    overlay = TransparentFramelessWindow(coords)
    overlay.show()

    gui.running = True


if __name__ == "__main__":
    reader = OCR()
    client = genai.Client()
    app = QApplication(sys.argv)

    coords = select_region()
    if coords is None:
        sys.exit()

    overlay = TransparentFramelessWindow(coords)
    overlay.show()

    # Single timer that handles everything
    global timer
    timer = QTimer()
    timer.timeout.connect(take_screenshot_and_translate)
    timer.start(2000)  # Check every 2 seconds
    print("wth")
    
    sys.exit(app.exec_())
    print("ge")
    