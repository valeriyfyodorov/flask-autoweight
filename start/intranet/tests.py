import os
import re
import requests
import time
import numpy as np
import urllib.parse
import cv2  # run opencv_install.sh to install
# from picamera import PiCamera
from PIL import Image
from random import randint
import zbarlight
from pyModbusTCP.client import ModbusClient

SCALES_NAME_FOR_ID = {"2": "north", "1": "south"}
SCALES = {
    "north":
    {
        "id": 2,
        "cam_front":
        {
            "url": "rtsp://192.168.20.183:554/video2",
            "crop_ratio": [0.3, 0.97, 0.255, 0.99],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_rear":
        {
            "url": "rtsp://192.168.20.184:554/video2",
            "crop_ratio": [0.39, 0.81, 0.35, 0.8],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_top":
        {
            "url": "rtsp://192.168.20.185:554/video2",
            "crop_ratio": [0.5, 0.7, 0.4, 0.6],
            "warp_from": [[528, 332], [528, 355], [631, 354], [631, 332]],
            "warp_to": [[528, 332], [528, 355], [631, 354], [631, 332]],
        },
        "modbus":
        {
            "host": "192.168.21.124",
            "port": 505,
        },
    },
    "south":
    {
        "id": 1,
        "cam_front":
        {
            "url": "rtsp://192.168.20.180:554/video2",
            "crop_ratio": [0.3, 0.97, 0.255, 0.99],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_rear":
        {
            "url": "rtsp://192.168.20.181:554/video2",
            "crop_ratio": [0.39, 0.81, 0.35, 0.8],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_top":
        {
            "url": "rtsp://192.168.20.182:554/video2",
            "crop_ratio": [0.3, 0.5, 0.3, 0.5],
            "warp_from": [[528, 332], [528, 355], [631, 354], [631, 332]],
            "warp_to": [[528, 332], [528, 355], [631, 354], [631, 332]],
        },
        "modbus":
        {
            "host": "192.168.21.124",
            "port": 504,
        },
    },
}


MAC_TEST_LOCATION = '/Users/Valera/Documents/venprojs/pi/latest/html/'
IMAGES_DIRECTORY = MAC_TEST_LOCATION
DEBUG_WITH_DUMMY_PLATES = False


class Timer:
    timers = dict()

    def __init__(self, name):
        self.name = name
        self._start_time = time.time()
        self.timers.setdefault(name, 0)

    def reset(self, name=None):
        self._start_time = time.time()
        self.timers.setdefault(name, self._start_time)

    def read(self):
        elapsed_time = time.time() - self._start_time
        if self.name:
            self.timers[self.name] += elapsed_time
        return elapsed_time


def bad_image(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [1], None, [5], [0, 180])
    return min(hist) / max(hist) < 0.001


def unskewed_image(img, box_warped, box_straight):
    img[np.where(img == 0)] = 1
    height = img.shape[0]
    width = img.shape[1]
    TM = cv2.getPerspectiveTransform(box_warped, box_straight)
    warped = cv2.warpPerspective(img, TM, (img.shape[1], img.shape[0]))
    warped[np.where(warped == 0)] = img[np.where(warped == 0)]
    return warped


def readRtspImage(scale_cam, trials=5):
    address = scale_cam["url"]
    crop_ratio = scale_cam["crop_ratio"]
    box_from = np.float32(scale_cam["warp_from"])
    box_to = np.float32(scale_cam["warp_to"])
    vcap = None
    frame = None
    for x in range(trials):
        try:
            vcap = cv2.VideoCapture(address)
            break
        except:
            print(f"readRtspImage. Failed to open Videocapture for {address}")
            continue
    timer = Timer("camRead")
    while True:
        try:
            ret, frame = vcap.read()
            if not bad_image(frame) or timer.read() > 5:
                break
        except:
            print(f"readRtspImage. Failed to capture image at {address}")
            break
    vcap.release()
    if frame is None:
        return frame
    height = frame.shape[0]
    width = frame.shape[1]
    frame = unskewed_image(frame, box_from, box_to)
    cropped = frame[
        int(height*crop_ratio[0]):int(height*crop_ratio[1]),
        int(width*crop_ratio[2]):int(width*crop_ratio[3])
    ]
    if DEBUG_WITH_DUMMY_PLATES:
        cropped = cv2.imread(DUMMY_IMG_FRONT)
    return cropped


def chooseBestFromAPI(input_array):
    exclusions = ['mb533', 'wb533']
    pattern = r'^[a-zA-Z]+\d+'
    result = ""
    for item in input_array:
        item = item['plate']
        if not item:
            continue
        item = item.strip().lower().replace(' ', '').replace('-', '')
        if item in exclusions:
            continue
        if len(item) > 7:
            continue
        if re.search(pattern, item):
            return item.upper()
    return result


def recognizePlate(img):
    if img is None:
        return ""
    result = ""
    headers = {'Authorization': ALPR_API_TOKEN}
    is_success, img_buffer = cv2.imencode(".jpg", img)
    img_encoded = img_buffer.tostring()
    try:
        files = {'upload': img_encoded}
        response = requests.post(ALPR_URL, files=files, headers=headers)
        if (len(response.json()['results']) != 0):
            result = chooseBestFromAPI(response.json()['results'])
    except:
        print("Error during plate getting from api")
    return result


def isThisEmptyBox(image):
    height = image.shape[0]
    width = image.shape[1]
    img = image[
        int(height*0.3):int(height*0.7),
        int(width*0.3):int(width*0.7)
    ]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    avg_color = numpy.average(numpy.average(hsv, axis=0), axis=0)[0]
    hist = cv2.calcHist([hsv], [0], None, [5], [0, 255])
    print(hist)
    ratio = (min(hist) / max(hist))[0]
    print(ratio)
    return (ratio < 0.005)


# return true if invoice photo was success
def captureInvoiceToFile(img_file=""):
    result = True
    with PiCamera() as camera:
        light_on()
        camera.start_preview()
        time.sleep(2)
        camera.capture(img_file)
        time.sleep(0.5)
        img = cv2.imread(img_file)
        result = not isThisEmptyBox(img)
        cv2.imwrite(img_file, img)
        light_off()
    return result

# loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_red1.jpg'
# test_img = cv2.imread(loc)
# print(loc)
# print(isThisEmptyBox(test_img))


# value = randint(0, 100)

# IMAGES_DIRECTORY = '/var/www/html/'
# TEMP_INVOICE_IMG_FILE = IMAGES_DIRECTORY + f"invoice_tst_{value}.jpg"
# print(captureInvoiceToFile(img_file=TEMP_INVOICE_IMG_FILE))

def test_inv(invoiceNr):
    # invoiceNr = invoiceNr.replace("/", "").replace("\\", "").replace(" ", "")
    # alphanumeric_filter = filter(str.isalnum, invoiceNr)
    # invoiceNr = "".join(alphanumeric_filter)
    invoiceNr = urllib.parse.quote(invoiceNr, safe='')
    invoiceWeight = '25000'
    api_query = f"&inr={invoiceNr}&iwt={invoiceWeight}"
    print(api_query)


def readQrCodeFromCam(onlyNumeric=True):
    timer = Timer("readqr")
    code = 0
    IMAGES_DIRECTORY = '/Users/Valera/Documents/venprojs/pi/latest/html/'
    # DUMMY_IMG_QR = IMAGES_DIRECTORY + 'dummy-qr.jpg'
    DUMMY_IMG_QR = IMAGES_DIRECTORY + 'goodqr.jpg'
    image = Image.open(DUMMY_IMG_QR)
    while True:
        codes = zbarlight.scan_codes(['qrcode'], image)
        if codes is not None:
            res = codes[0].decode("utf-8")
            if res.isnumeric():
                code = int(res)
            elif onlyNumeric:
                code = 0
            else:
                code = res
            break
        if timer.read() > 10:
            break
    return code


def getWeightKg(scalesName):
    c = ModbusClient()
    host = "192.168.21.124"
    host = "192.168.21.200"
    port = 505
    port = 502
    c.host(host)
    c.port(port)
    if not c.is_open():
        if not c.open():
            print(
                f"unable to connect to modbus {SCALES[scalesName]['modbus']['host']} at port {SCALES[scalesName]['modbus']['port']}")
    str_weight = "0"
    if c.is_open():
        regs = c.read_holding_registers(1, 2)
        regs = c.read_holding_registers(555, 2)
        print(regs)
        if regs is not None:
            if len(regs) > 0:
                str_weight = regs[0]
    if c.is_open():
        c.close()  # close connection on every weight request
    result = int(str_weight)
    return result


def archiveCargoImage(cargoId, args):
    scalesName = "south"
    img_top = readRtspImage(
        SCALES[scalesName]["cam_top"]
    )
    destination_dir = IMAGES_DIRECTORY + f"/{cargoId}/"
    os.makedirs(destination_dir, exist_ok=True)
    file_path = destination_dir + time.strftime("%y_%m_%d_%H_%M_%S") + ".jpg"
    try:
        cv2.imwrite(file_path, img_top)
    except cv2.error as e:
        print("No image on top camera" + "1" + f" {e}")


print(archiveCargoImage(1, None))
