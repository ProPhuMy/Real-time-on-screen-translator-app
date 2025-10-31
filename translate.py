import easyocr
import screenshot as sc

class OCR:
    def __init__(self, langlist = ['ja', 'en']):
        self.reader = easyocr.Reader(langlist)
    
    def extract_text(self, img):
        result = self.reader.readtext(img)
        return result