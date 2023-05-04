from pathlib import Path
import easyocr
import psutil
import os
import pdf2image
import tempfile

BASE_DIR = Path(__file__).resolve().parent.parent
# C:\Program Files (x86)\Tesseract-OCR


def ParseFileThread(f_name, document):
    p = psutil.Process(os.getpid())
    p.nice(19)
    reader = easyocr.Reader(['ru'], gpu=True)
    print("file parsing started...")
    with tempfile.TemporaryDirectory() as path:
        pdf2image.convert_from_path(
            os.path.join(BASE_DIR, str(document.get_url()))[1:], 600, path)
        text = ''

        print("images processing started")
        for i in sorted(os.listdir(path)):
            print("processing " + i)
            text += reader.readtext(
                os.path.join(path, i), detail=0, paragraph=True, workers=1)

        document.text = text
        document.is_readed = True
        document.save()
        print("end.")
