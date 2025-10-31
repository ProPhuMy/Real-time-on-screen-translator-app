import easyocr
import numpy as np
reader = easyocr.Reader(['en'])
result = reader.readtext('12.png', detail = 1)
formatted = [(bbox, text) for bbox, text, _ in result]
print(formatted)