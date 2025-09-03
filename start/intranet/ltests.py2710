import re
import requests
import numpy
import cv2  # run opencv_install.sh to install
from PIL import Image
from random import randint


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
        int(height*0.4):int(height*0.6),
        int(width*0.4):int(width*0.6)
    ]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = image.copy()
    avg_color = numpy.average(numpy.average(hsv, axis=0), axis=0)[0]
    hist = cv2.calcHist([hsv], [0], None, [4], [0, 255])
    # print(hist)
    # print(f"Channel 0 {cv2.minMaxLoc(hsv[:, :, 0])}")
    # print(f"Channel 1 {cv2.minMaxLoc(hsv[:, :, 1])}")
    # print(f"Channel 2 {cv2.minMaxLoc(hsv[:, :, 2])}")
    # print(f"Max 0 {numpy.max(hsv[:, :, 0])}")
    # print(f"Max 1 {numpy.max(hsv[:, :, 1])}")
    # print(f"Max 2 {numpy.max(hsv[:, :, 2])}")
    # print(f"Min 0 {numpy.min(hsv[:, :, 0])}")
    # print(f"Min 1 {numpy.min(hsv[:, :, 1])}")
    # print(f"Min 2 {numpy.min(hsv[:, :, 2])}")
    ratio = (min(hist) / max(hist))[0]
    print(ratio)
    return (ratio > 0.1)


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


loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_tape.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))

loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_red1.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))

loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_red2.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))

loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_ok1.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))

loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_ok2.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))

loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_ok3.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))

loc = '/Users/Valera/Documents/venprojs/pi/latest/html/invoice_ok4.jpg'
test_img = cv2.imread(loc)
print(loc)
print(isThisEmptyBox(test_img))


# value = randint(0, 100)

# IMAGES_DIRECTORY = '/var/www/html/'
# TEMP_INVOICE_IMG_FILE = IMAGES_DIRECTORY + f"invoice_tst_{value}.jpg"
# print(captureInvoiceToFile(img_file=TEMP_INVOICE_IMG_FILE))
