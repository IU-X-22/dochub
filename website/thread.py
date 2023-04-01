from pathlib import Path
import easyocr
import os
import pdf2image

BASE_DIR = Path("/".join(__file__.replace("\\", "/").split("/")[:-2]))
# C:\Program Files (x86)\Tesseract-OCR


def ParseFileThread(f_name, document):
    img = pdf2image.convert_from_path(BASE_DIR + document.get_url(), 1000)
    for i in range(len(img)):
        print(os.path.join('documents', f_name, document.name +
                           str(i) + '.jpg'))
        img[i].save(os.path.join('documents', f_name, document.name +
                                 str(i) + '.jpg'), 'JPEG')
    reader = easyocr.Reader(['ru'])  # add switch
    text = ''
    for i in range(len(img)):
        text += ''.join(
            reader.readtext(
              os.path.join('documents', f_name, document.name + str(i)+'.jpg'),
              detail=0
            )
        )
    document.text = text
    document.save()
