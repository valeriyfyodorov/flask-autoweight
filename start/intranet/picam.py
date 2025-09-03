from .config import MAC_OS, DUMMY_IMG_INVOICE, DUMMY_IMG_QR, GPIO_LAMP, TEMP_INVOICE_IMG_FILE, DEBUG_WITH_DUMMY_QR
import time
from shutil import copyfile
from io import BytesIO
from PIL import Image
# from .utils import Timer
from .vision import isThisEmptyBox

if MAC_OS:
    from . import GPIO
else:
    import RPi.GPIO as GPIO
    from picamera import PiCamera


def light_on():
    GPIO.output(GPIO_LAMP, True)


def light_off():
    GPIO.output(GPIO_LAMP, False)


def rotateAndResave(filepath, degrees):  # return true if invoice photo was success
    im = Image.open(filepath)
    im.rotate(degrees, expand=True).save(filepath)


def captureInvoiceToFile():  # return true if invoice photo was success
    result = True
    number = ""
    if MAC_OS:
        result = not isThisEmptyBox(Image.open(DUMMY_IMG_INVOICE))
        copyfile(DUMMY_IMG_INVOICE, TEMP_INVOICE_IMG_FILE)
        rotateAndResave(TEMP_INVOICE_IMG_FILE, 90)
    else:
        with PiCamera() as camera:
            light_on()
            camera.start_preview()
            time.sleep(2)
            camera.capture(TEMP_INVOICE_IMG_FILE)
            time.sleep(0.8)
            result = not isThisEmptyBox(Image.open(TEMP_INVOICE_IMG_FILE))
            if result:
                rotateAndResave(TEMP_INVOICE_IMG_FILE, 90)
            # maybe recgnize number in a future
            number = "XXX"
            light_off()
    return result, number


def camToPilImg():  # return PIL image from cam
    image = None
    if DEBUG_WITH_DUMMY_QR:
        image = Image.open(DUMMY_IMG_QR)
    else:
        with PiCamera() as camera:
            light_on()
            stream = BytesIO()
            camera.start_preview()
            time.sleep(2)
            camera.capture(stream, format='jpeg')
            # "Rewind" the stream to the beginning so we can read its content
            stream.seek(0)
            image = Image.open(stream)
            light_off()
    return image
