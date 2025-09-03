from pyModbusTCP.client import ModbusClient
import time
from shutil import copyfile
import cv2
from .utils import Timer, archiveFileName, dictFromArgs
from .config import (
    PlatesSet, SCALES,
    DEBUG_WITH_DUMMY_SCALES, SCALES_NAME_FOR_ID,
    IMAGES_DIRECTORY, TEMP_INVOICE_IMG_FILE,
    TEMP_PLATE_IMG_FILE_FRONT, TEMP_PLATE_IMG_FILE_REAR
)
from .vision import recognizePlate, readRtspImage
from .picam import captureInvoiceToFile


def getPlatesNumbers(scalesName, weight=1000):
    plates = PlatesSet()
    if weight < 200:
        return plates
    img_front = readRtspImage(
        SCALES[scalesName]["cam_front"]
    )
    plates.front = recognizePlate(img_front)
    img_rear = readRtspImage(
        SCALES[scalesName]["cam_rear"]
    )
    time.sleep(0.1)
    plates.rear = recognizePlate(img_rear)
    if len(plates.front) > 8:
        plates.front = plates.front[-6:]
    if len(plates.rear) > 8:
        plates.rear = "S" + plates.rear[-4:]
    # # test img
    # cv2.imwrite(TEMP_PLATE_IMG_FILE_FRONT,img_front)
    # cv2.imwrite(TEMP_PLATE_IMG_FILE_REAR,img_rear)
    time.sleep(0.1)
    return plates


def getWeightKg(scalesName):
    c = ModbusClient()
    c.host(SCALES[scalesName]["modbus"]["host"])
    c.port(SCALES[scalesName]["modbus"]["port"])
    if not c.is_open():
        if not c.open():
            print(
                f"unable to connect to modbus {SCALES[scalesName]['modbus']['host']} at port {SCALES[scalesName]['modbus']['port']}")
    str_weight = "0"
    if c.is_open():
        regs = c.read_holding_registers(1, 2)
        print(regs)
        if regs is not None:
            if len(regs) > 0:
                str_weight = regs[0]
    if c.is_open():
        c.close()  # close connection on every weight request
    result = int(str_weight)
    if result == 0 and DEBUG_WITH_DUMMY_SCALES:
        if scalesName == "north":
            result = 44000
        if scalesName == "south":
            result = 9000
    return result


def readInvoice():
    timer = Timer("invoice")
    result = False
    number = ""
    while True:
        # TODO real qr recognition here
        result, number = captureInvoiceToFile()
        if result or timer.read() > 10:
            break  # 10 seconds to try to scan invoice
    return result, number


def archivePlates(car_id, args):
    queryDict = dictFromArgs(args)
    wkg = str(queryDict["wkg"])
    ptf = str(queryDict["ptf"]).replace('/', '-').replace('\\', '-')
    ptr = str(queryDict["ptr"]).replace('/', '-').replace('\\', '-')
    sc = str(queryDict["sc"]).strip()
    scalesName = SCALES_NAME_FOR_ID[sc]
    img_front = readRtspImage(
        SCALES[scalesName]["cam_front"]
    )
    img_rear = readRtspImage(
        SCALES[scalesName]["cam_rear"]
    )
    cv2.imwrite(archiveFileName(IMAGES_DIRECTORY,
                                f"_{car_id}_({wkg}-F-{ptf}).jpg"), img_front)
    cv2.imwrite(archiveFileName(IMAGES_DIRECTORY,
                                f"_{car_id}_({wkg}-R-{ptr}).jpg"), img_rear)
    cv2.imwrite(TEMP_PLATE_IMG_FILE_FRONT, img_front)
    cv2.imwrite(TEMP_PLATE_IMG_FILE_REAR, img_rear)


def archiveInvoice(car_id, args, invoiceNr):
    # queryDict = dictFromArgs(args)
    # wkg = str(queryDict["wkg"])
    copyfile(TEMP_INVOICE_IMG_FILE, archiveFileName(
        IMAGES_DIRECTORY, f"_{car_id}.jpg", saveTime=False))
