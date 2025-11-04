import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtGui import QFont
from gui import select_region

class TransparentFramelessWindow(QWidget):
    def __init__(self, coords):
        super().__init__()
        self.setWindowTitle('I need your love')
        self.x1, self.y1, self.width1, self.height1 = coords
        self.setGeometry(self.x1, self.y1 , self.width1, self.height1)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
    
    def convert_bbox_to_xywh(self, bbox: list):
        # the list returned from easyocr is in the format:
        # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        # we only want to extract the first and last item from the 2d array to get xywh
        x, y =  bbox[0]
        placeholder_x , placeholder_y = bbox[2]
        return x, y, abs(placeholder_x-x), abs(y - placeholder_y)
    
    def create_labels(self, bbox_and_text_list: list):
        for bbox_and_text_tuple in bbox_and_text_list:
            x, y, width, height = self.convert_bbox_to_xywh(bbox_and_text_tuple[0])
            text_size = height * 0.7
            label = QLabel(bbox_and_text_tuple[1], self)
            label.setGeometry(x, y, width, height)
            label.setStyleSheet("background-color: white;")
            label.setMargin(5)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            font = QFont('Arial', text_size)
            font.setBold(True)
            label.setFont(font)
    
    def reset_labels(self):
        for child in self.findChildren(QLabel):
            child.deleteLater()

def main():
    app = QApplication(sys.argv)
    coords = select_region()
    if coords:
        x, y, w, h = coords
        win = TransparentFramelessWindow(x, y , w, h)
        win.create_labels()
        win.show()
        sys.exit(app.exec())
if __name__ == "__main__":
    main()