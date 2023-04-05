import threading
import hashlib
from pathlib import Path
import easyocr
import os
BASE_DIR = Path(__file__).resolve().parent.parent
import pdf2image
#C:\Program Files (x86)\Tesseract-OCR


def ParseFileThread(f_name,document):
    
    img = pdf2image.convert_from_path(os.path.join(BASE_DIR,str(document.get_url()))[1:],1000) 
    for i in range(len(img)):
        img[i].save(os.path.join('documents',f_name, str(hashlib.md5( f_name.encode('utf-8')).hexdigest()) + str(hashlib.md5( document.name.encode('utf-8')).hexdigest())+ str(i)+'.jpg')   , 'JPEG')
    reader  = easyocr.Reader(['ru'])# add switch
    text = ''
    for i in range(len(img)):
        text +=''.join(reader.readtext(os.path.join('documents',f_name, str(hashlib.md5( f_name.encode('utf-8')).hexdigest()) + str(hashlib.md5( document.name.encode('utf-8')).hexdigest())+ str(i)+'.jpg'),detail=0))
        os.remove(os.path.join('documents',f_name, str(hashlib.md5( f_name.encode('utf-8')).hexdigest()) + str(hashlib.md5( document.name.encode('utf-8')).hexdigest())+ str(i)+'.jpg'))
    document.text = text
    document.is_readed=True
    document.save()

    