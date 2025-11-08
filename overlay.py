from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QFont


class TransparentFramelessWindow(QWidget):
    def __init__(self, coords):
        super().__init__()
        self.setWindowTitle('I need your love')
        self.x1, self.y1, self.width1, self.height1 = coords
        self.setGeometry(self.x1, self.y1 , self.width1, self.height1)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowOpacity(0.3)
    
    def convert_bbox_to_xywh(self, bbox: list):
        # the list returned from easyocr is in the format:
        # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        # we only want to extract the first and last item from the 2d array to get xywh
        x, y =  bbox[0]
        placeholder_x , placeholder_y = bbox[2]

        x = int(x)
        y = int(y)
        placeholder_x = int(placeholder_x)
        placeholder_y = int(placeholder_y)

        width = abs(placeholder_x-x)
        height = abs(y - placeholder_y)

        # padding = max(10, int(height * 0.15))
        # x = x - padding
        # y = y - padding
        # width = width + (padding * 2)
        # height = height + (padding * 2)
        return x, y, width , height
    
    def create_labels(self, bbox_and_text_list: list):
        for bbox_and_text_tuple in bbox_and_text_list:
            x, y, width, height = self.convert_bbox_to_xywh(bbox_and_text_tuple[0])
            label = QLabel(bbox_and_text_tuple[1], self)
            label.setGeometry(x, y, width, height)
            label.setStyleSheet("background-color: white;")
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            font = QFont('Arial')
            font.setBold(True)
            label.setFont(font)
            label.show()
           
    def reset_labels(self):
        from PyQt5.QtWidgets import QApplication
        for child in self.findChildren(QLabel):
            child.setParent(None)
            child.deleteLater()
        QApplication.processEvents()  # Force Qt to process deletions immediately
