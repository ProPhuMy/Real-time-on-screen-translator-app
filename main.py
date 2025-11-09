import screenshot as sc
from screenshot import OCR
import translate as ts
from gui_pyqt import SnippingToolGUI
from overlay import TransparentFramelessWindow
from PyQt5.QtWidgets import QApplication, QProgressDialog
from PyQt5 import QtCore
import sys
from google import genai

overlay = None
reader = None
client = None
coords = None
control = None


class CaptureWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(object, object)  # (translated, error)

    def __init__(self, coords, reader, client):
        super().__init__()
        self.coords = coords
        self.reader = reader
        self.client = client

    @QtCore.pyqtSlot()
    def run(self):
        try:
            img = sc.convert_image(sc.take_image(self.coords))
            result = self.reader.extract_text(img)
            translated = ts.translate_text(result, self.client) if result else None
            self.finished.emit(translated, None)
        except Exception as e:
            self.finished.emit(None, e)


def on_region_changed(new_coords):
    global overlay, coords
    coords = new_coords
    # Recreate overlay for the new region
    try:
        if overlay is not None:
            overlay.close()
            overlay = None
        if coords is not None:
            overlay = TransparentFramelessWindow(coords)
            overlay.show()
    except Exception as e:
        print(f"Error creating overlay: {e}")


def on_take_picture():
    global overlay, reader, client, coords, control
    if coords is None:
        print("No region selected. Click 'Select Region' first.")
        return

    # hide overlay to avoid capturing it
    if overlay is not None:
        overlay.hide()
        QApplication.processEvents()

    # Show dialog
    progress = QProgressDialog("Processing image...", None, 0, 0, control)
    progress.setWindowModality(QtCore.Qt.ApplicationModal)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)
    progress.setAutoClose(False)
    progress.setAutoReset(False)
    progress.show()

    # Start background worker
    thread = QtCore.QThread()
    worker = CaptureWorker(coords, reader, client)
    worker.moveToThread(thread)

    def on_finished(translated, error):
        try:
            if error:
                print(f"Error in manual capture: {error}")
            else:
                if translated and overlay is not None:
                    overlay.reset_labels()
                    overlay.create_labels(translated)
        finally:
            if overlay is not None:
                overlay.show()
                QApplication.processEvents()
            progress.close()
            worker.deleteLater()
            thread.quit()
            thread.wait()

    thread.started.connect(worker.run)
    worker.finished.connect(on_finished)
    thread.start()


def _cleanup():
    """Cleanup resources when app is quitting."""
    global overlay
    try:
        if overlay is not None:
            overlay.close()
            overlay = None
    except Exception:
        pass


if __name__ == "__main__":
    reader = OCR()
    client = genai.Client()
    app = QApplication(sys.argv)

    # Create control window
    control = SnippingToolGUI()
    control.regionChanged.connect(on_region_changed)
    control.takePicture.connect(on_take_picture)
    control.show()

    app.aboutToQuit.connect(_cleanup)

    sys.exit(app.exec_())
    