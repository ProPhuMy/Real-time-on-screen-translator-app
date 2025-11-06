import gui
from gui import select_region
import time
import screenshot as sc
from screenshot import OCR
import translate as ts
from overlay import TransparentFramelessWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import sys
from queue import Queue
import threading

def check_results():
    """Called every 100ms by timer"""
    if not result_queue.empty():
        data = result_queue.get()
        
        if data is None or len(data) == 0:
            return # return nothing
        
        overlay.reset_labels()
        overlay.create_labels(data)

def monitor(coords, result_queue):
    img = None
    while True:
        while gui.running and coords:
            print("Taking screenshot...")
            img2 = sc.convert_image(sc.take_image(coords))
            if img is None:
                result = reader.extract_text(img2)
                if result is None:
                    continue
                new_result = ts.translate_text(result)
                if new_result is not None and len(new_result) > 0:
                    img = img2
                    result_queue.put(new_result)
            else:
                if (sc.compare_images(img, img2)):
                    result = reader.extract_text(img2)
                    if result is None:
                        continue
                    new_result = ts.translate_text(result)
                    if new_result is not None and len(new_result) > 0:
                        img = img2
                        result_queue.put(new_result)
                else:
                    pass
            time.sleep(2)
        time.sleep(0.1)
        if (gui.has_exit):
            break
    
def has_exit():
    pass

if __name__ == "__main__":
    reader = OCR()
    result_queue = Queue()
    app = QApplication(sys.argv)

    coords = select_region()
    if coords is None:
        sys.exit()

    overlay = TransparentFramelessWindow(coords)
    overlay.show()

    timer = QTimer()
    timer.timeout.connect(check_results)
    timer.start(100)

    monitor_thread = threading.Thread(target=monitor, args=(coords, result_queue))
    monitor_thread.daemon = True  # Thread dies when main program exits
    monitor_thread.start()
    
    sys.exit(app.exec_())
    