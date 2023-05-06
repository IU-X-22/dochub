from pathlib import Path
import easyocr
import psutil
import os
import pdf2image
import tempfile
import math
from queue import Queue
import threading
BASE_DIR = Path(__file__).resolve().parent.parent

image_queue = Queue()

def ParseFileThread():
    p = psutil.Process(os.getpid())
    p.nice(19)
    while True:
        document = image_queue.get()  
        image_queue.task_done()
        document = image_queue.get()    
        reader = easyocr.Reader(['ru'], gpu=True)
        print("file parsing started...")
        with tempfile.TemporaryDirectory() as path:
            pdf2image.convert_from_path(
                os.path.join(BASE_DIR, str(document.get_url()))[1:], 800, path)
            text = ''
            print("images processing started")
            for i in sorted(os.listdir(path)):
                print("processing " + i)
                text += ''.join(reader.readtext(
                    os.path.join(path, i), detail=0, paragraph=True, workers=1))
    
            document.text = text
            document.is_readed = True
            document.save()
            print("end.")
            image_queue.task_done()

t = threading.Thread(target=ParseFileThread,)
t.daemon=True
t.start()


def add_image(image):
    image_queue.put(image)