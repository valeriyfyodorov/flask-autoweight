# from PIL import Image
import re
import requests
import numpy as np
import cv2  # run opencv_install.sh to install
import zbarlight
from .utils import Timer
from .config import (
    ALPR_API_TOKEN, ALPR_URL,
    DEBUG_WITH_DUMMY_PLATES, DUMMY_IMG_FRONT,
)


def bad_image(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [1], None, [5], [0, 180])
    return min(hist) / max(hist) < 0.001


def pilToOpenCvImg(pilImage):
    open_cv_image = np.array(pilImage.convert('RGB'))
    # Convert RGB to BGR
    image = open_cv_image[:, :, ::-1].copy()
    return image


def unskewed_image(img, box_warped, box_straight):
    img[np.where(img == 0)] = 1
    # height = img.shape[0]
    # width = img.shape[1]
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
            if not bad_image(frame) or timer.read() > 4.5:
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
        response = requests.post(
            ALPR_URL, files=files, headers=headers, timeout=7)
        if (len(response.json()['results']) != 0):
            result = chooseBestFromAPI(response.json()['results'])
    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass
    return result


def readQrCodeFromImg(pilImage, onlyNumeric=True):
    code = 0
    codes = zbarlight.scan_codes(['qrcode'], pilImage)
    if codes is not None:
        res = codes[0].decode("utf-8")
        if res.isnumeric():
            code = int(res)
        elif onlyNumeric:
            code = 0
        else:
            code = res
    return code


def isThisTooRed(pilImage):
    image = pilToOpenCvImg(pilImage)
    # height = image.shape[0]
    # width = image.shape[1]
    # img = image[
    #     int(height*0.4):int(height*0.6),
    #     int(width*0.4):int(width*0.6)
    # ]
    # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = image
    # avg_color = np.average(np.average(hsv, axis=0), axis=0)[0]
    hist = cv2.calcHist([hsv], [0], None, [4], [0, 255])
    # print(hist)
    ratio = (min(hist) / max(hist))[0]
    # print(ratio)
    return (ratio > 0.1)
    # return (avg_color > 5 and avg_color < 15)


def isThisEmptyBox(pilImage):
    # return isThisTooRed(image) # old type check
    zcode = readQrCodeFromImg(pilImage, onlyNumeric=False)
    if zcode == "iiiiii":
        return True
    else:
        return False
