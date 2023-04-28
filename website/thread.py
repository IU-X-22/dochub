import threading
import hashlib
from pathlib import Path
import easyocr
import psutil
import time
import os
BASE_DIR = Path(__file__).resolve().parent.parent
import pdf2image
#C:\Program Files (x86)\Tesseract-OCR


def ParseFileThread(f_name,document):
    p = psutil.Process(os.getpid())
    p.nice(19)
    print("IN THREAD")
    img = pdf2image.convert_from_path(os.path.join(BASE_DIR,str(document.get_url()))[1:],900) 
    for i in range(len(img)):
        print("SAVE ",i," IMAGE")
        img[i].save(os.path.join('documents',f_name, str(hashlib.md5( f_name.encode('utf-8')).hexdigest()) + str(hashlib.md5( document.name.encode('utf-8')).hexdigest())+ str(i)+'.jpg')   , 'JPEG')
    reader  = easyocr.Reader(['ru'],gpu = True)# add switch
    text = ''
    print("START TEXT EXTRA")
    for i in range(len(img)):
        print("GET TEXT FROM",i,"PAGE")
        text +=''.join(reader.readtext(os.path.join('documents',f_name, str(hashlib.md5( f_name.encode('utf-8')).hexdigest()) + str(hashlib.md5( document.name.encode('utf-8')).hexdigest())+ str(i)+'.jpg'),detail=0))
        os.remove(os.path.join('documents',f_name, str(hashlib.md5( f_name.encode('utf-8')).hexdigest()) + str(hashlib.md5( document.name.encode('utf-8')).hexdigest())+ str(i)+'.jpg'))
    document.text = text
    print("TEXT COPIED")
    document.is_readed=True
    document.save()
    print("TEXT SAVE")

    