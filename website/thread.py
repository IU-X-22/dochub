from pathlib import Path
import easyocr
import psutil
import os
import pdf2image
import tempfile
from queue import Queue
from website.models import QueueStatus
import logging
import threading
BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)
image_queue = Queue()


def ParseFileThread():
    p = psutil.Process(os.getpid())
    p.nice(19)
    while True:
        document = image_queue.get()
        text = ''
        logger.warning("начало обработки файла "+document.name)
        reader = easyocr.Reader(['ru'], gpu=True)
        with tempfile.TemporaryDirectory() as path:
            pdf2image.convert_from_path(
                os.path.join(BASE_DIR, str(document.get_url()))[1:], 700, path)
            for i in sorted(os.listdir(path)):
                logger.warning("обработка " + i)
                text += ''.join(reader.readtext(
                    os.path.join(path, i), detail=0, paragraph=True))
                text += ' '
            document.text = text
            document.read_status = 1
            document.save()
            q = QueueStatus.objects.get()
            q.actual_progress+=1    
            if q.actual_progress==q.max_progress:
                q.actual_progress=0
                q.max_progress=0
            q.save()
            logger.warning("конец обработки файла " + document.name)
            image_queue.task_done()


num_threads = int(os.environ.get("NUM_THREADS", default=1))
for _ in range(num_threads):
    t = threading.Thread(target=ParseFileThread,)
    t.daemon = True
    t.start()


def add_image(image):
    image_queue.put(image)
