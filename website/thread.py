import threading

import easyocr
import pdf2image
#C:\Program Files (x86)\Tesseract-OCR


class ParseFileThread(threading.Thread):

    def __init__(self, total):
        self.total = total 
        threading.Thread.__init(self)
    def run(self):
        print("search")
       

    