import sys

if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from PyQt5 import QtCore, QtGui, QtWidgets

global running
running = True

class RegionSelectorDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Dialog
        )
        self.setModal(True)

        self.showFullScreen()

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.setCursor(QtCore.Qt.CrossCursor)

        # setting election state
        self._start_global = None
        self._current_global = None
        self._selecting = False
        self.result = None

        self.shortcut_escape = QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self)
        self.shortcut_escape.activated.connect(self._on_escape)

    def _on_escape(self):
        self.result = None
        self.reject()

    # Mouse events work with global positions to return screen coords
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._start_global = QtGui.QCursor.pos()
            self._current_global = self._start_global
            self._selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self._selecting:
            self._current_global = QtGui.QCursor.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self._selecting:
            end_global = QtGui.QCursor.pos()
            start = self._start_global
            # compute normalized rectangle in screen coords
            x = min(start.x(), end_global.x())
            y = min(start.y(), end_global.y())
            w = abs(end_global.x() - start.x())
            h = abs(end_global.y() - start.y())

            if w == 0 or h == 0:
                self.result = None
            else:
                self.result = (int(x), int(y), int(w), int(h))

            self._selecting = False
            self.update()
            self.accept()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        overlay_color = QtGui.QColor(0, 0, 0, 64)
        painter.fillRect(self.rect(), overlay_color)

        # If selecting, draw rectangle in widget coords
        if self._selecting and self._start_global and self._current_global:
            start_widget = self.mapFromGlobal(self._start_global)
            cur_widget = self.mapFromGlobal(self._current_global)
            rect = QtCore.QRect(start_widget, cur_widget).normalized()
            pen = QtGui.QPen(QtGui.QColor("red"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(rect)


class SnippingToolGUI(QtWidgets.QWidget):
    # Emitted when user finishes selecting a region: (x, y, w, h)
    regionChanged = QtCore.pyqtSignal(tuple)
    # Emitted when user clicks "Take Picture"
    takePicture = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.result = None

        self.setWindowTitle("Screen Region Selector")
        self.setFixedSize(300, 200)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Center the window on the primary screen
        qr = self.frameGeometry()
        center_point = QtWidgets.QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(center_point)
        self.move(qr.topLeft())

        # UI
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QtWidgets.QLabel("Screen Region Selector")
        title.setAlignment(QtCore.Qt.AlignCenter)
        font = title.font()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addSpacing(10)

        self.select_button = QtWidgets.QPushButton("Select Region")
        btn_font = self.select_button.font()
        btn_font.setPointSize(10)
        self.select_button.setFont(btn_font)
        self.select_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.select_button.setStyleSheet(
            "QPushButton{background:#0078D4;color:white;border:none;padding:10px 20px;}"
            "QPushButton:pressed{background:#106EBE;}"
        )
        self.select_button.clicked.connect(self.start_selection)
        layout.addWidget(self.select_button, 0, QtCore.Qt.AlignCenter)

        # Take Picture button
        self.capture_button = QtWidgets.QPushButton("Take Picture")
        cap_font = self.capture_button.font()
        cap_font.setPointSize(10)
        self.capture_button.setFont(cap_font)
        self.capture_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.capture_button.setStyleSheet(
            "QPushButton{background:#2D7D46;color:white;border:none;padding:10px 20px;}"
            "QPushButton:pressed{background:#256D3C;}"
        )
        self.capture_button.clicked.connect(self._on_take_picture)
        layout.addWidget(self.capture_button, 0, QtCore.Qt.AlignCenter)

        self.setLayout(layout)

    def start_selection(self):
        self.hide()
        dlg = RegionSelectorDialog(self)
        dlg.exec_()  
        self.result = dlg.result
        # Show this control window again and let the main app continue running.
        self.show()
        if self.result is not None:
            try:
                self.regionChanged.emit(tuple(self.result))
            except Exception:
                pass

    def closeEvent(self, event):
        # Terminate the entire application when the control window is closed
        try:
            QtWidgets.QApplication.quit()
        finally:
            event.accept()

    def _on_take_picture(self):
        # Emit signal. main app will perform the actual capture/translate
        self.takePicture.emit()


def select_region():
    app_created_here = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        # Enable high DPI scaling attributes
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        app_created_here = True

    gui = SnippingToolGUI()
    gui.show()

    # Execution model:
    #  - If we created the QApplication, we need to start its event loop so the
    #    user can interact. The user presses the button, which launches the
    #    modal RegionSelectorDialog. After dialog closes, we exit the app loop
    #    by explicitly closing the launcher window (which ends exec_()).
    #  - If an app already exists (embedded usage), we do not start/stop the
    #    global event loop, we process events manually until the launcher closes.

    if app_created_here:
        # Start the main loop; it will return after the launcher window closes.
        app.exec_()
    else:
        # Existing app: we synchronously process events until the window closes.
        # The start_selection method uses a modal exec_ on the dialog, so we just
        # keep the UI responsive here.
        while gui.isVisible():
            app.processEvents()
            QtCore.QThread.msleep(10)

    global running
    running = True

    return getattr(gui, "result", None)


if __name__ == "__main__":
    coords = select_region()
    print("Returned:", coords)
