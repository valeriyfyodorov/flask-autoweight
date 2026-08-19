MAC_OS = False
MAC_TEST_LOCATION = "/Users/Valera/Documents/venprojs/pi/latest/html/"

if MAC_OS:
    from . import GPIO
else:
    import RPi.GPIO as GPIO

DEBUG_WITH_DUMMY_SCALES = False
DEBUG_WITH_DUMMY_INVOICE = False
DEBUG_WITH_DUMMY_PLATES = False
DEBUG_WITH_DUMMY_QR = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO_BUZZER = 26
GPIO.setup(GPIO_BUZZER, GPIO.OUT)
GPIO.output(GPIO_BUZZER, False)

GPIO_LAMP = 22
GPIO.setup(GPIO_LAMP, GPIO.OUT)
GPIO.output(GPIO_LAMP, False)

CHECK_SAMPLER_HOMING = True


# if CHECK_SAMPLER_HOMING:
#    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button GPIO23  Rakoraf1 (Scales 1)
#    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button GPIO24  Rakoraf2 (Scales 2)


# ls /dev/video* first for right camera device here, minus 1 means first working
VIDEO_CAPTURE_DEVICE = -1
WEBCAM_BUFFER_SIZE = 5
WEBCAM_COLD_START = False
global video_capture

IMAGES_DIRECTORY = "/var/www/html/"
if MAC_OS:
    IMAGES_DIRECTORY = MAC_TEST_LOCATION

DUMMY_IMG_FRONT = IMAGES_DIRECTORY + "dummy-front.jpg"
DUMMY_IMG_REAR = IMAGES_DIRECTORY + "dummy-rear.jpg"
DUMMY_IMG_INVOICE = IMAGES_DIRECTORY + "dummy-invoice.jpg"
DUMMY_IMG_QR = IMAGES_DIRECTORY + "dummy-qr.jpg"
TEMP_INVOICE_IMG_FILE = IMAGES_DIRECTORY + "invoice.jpg"
TEMP_PLATE_IMG_FILE_FRONT = IMAGES_DIRECTORY + "front.jpg"
TEMP_PLATE_IMG_FILE_REAR = IMAGES_DIRECTORY + "rear.jpg"

STORED_IMAGES_KIOSK_IP = "192.168.100.2"
SERVER_URL = "http://notscr.amgs.me/autoweight"
SERVER_API_URL = "http://notscr.amgs.me/apijson.ashx?key=gd3784h67hxgugb"

# ALPR_API_TOKEN = 'Token 702d66a3f614a31139fefd757892acfb85771ee7'
# ALPR_URL = 'https://api.platerecognizer.com/v1/plate-reader'

ALPR_API_TOKEN = "Token 702d66a3f614a31139fefd757892acfb85771ee7"
# ALPR_URL = 'http://192.168.100.5:8080/v1/plate-reader/'
ALPR_URL = "http://192.168.21.34:5002/plate-reader/"

SCALES_NAME_FOR_ID = {"2": "north", "1": "south"}
TRAFFIC_LIGHT_API_URL = "http://192.168.21.82:8123/api/services/mqtt/publish"
TRAFFIC_LIGHT_API_AUTH = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxYTQ2NjM1ZmI3NWU0NmI1YmIzMzU2NjkzYzViYzg4YyIsImlhdCI6MTYzODk2OTA1NCwiZXhwIjoxOTU0MzI5MDU0fQ.ib-WYqlTWzzLsM3PVCLLkS6_0bVIc5G8f1GI_YI3VUI"
SCALES = {
    "north": {
        "id": 2,
        "cam_front": {
            "url": "rtsp://192.168.120.183:554/video2",
            "crop_ratio": [0.001, 0.999, 0.001, 0.999],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_rear": {
            "url": "rtsp://192.168.120.184:554/video2",
            "crop_ratio": [0.001, 0.999, 0.001, 0.999],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_top": {
            "url": "rtsp://192.168.120.185:554/media/video2",
            "crop_ratio": [0.1, 0.9, 0.1, 0.9],
            "warp_from": [[528, 332], [528, 355], [631, 354], [631, 332]],
            "warp_to": [[528, 332], [528, 355], [631, 354], [631, 332]],
        },
        "modbus": {
            "host": "192.168.130.124",
            "port": 505,
        },
        "light_topic_front": "trafficlights/ts2ftl/status",
        "light_topic_rear": "trafficlights/ts2rtl/status",
        "sampler_homing_gpio_port": 24,
    },
    "south": {
        "id": 1,
        "cam_front": {
            "url": "rtsp://192.168.120.180:554/video2",
            "crop_ratio": [0.001, 0.999, 0.001, 0.999],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_rear": {
            "url": "rtsp://192.168.120.181:554/video2",
            "crop_ratio": [0.001, 0.999, 0.001, 0.999],
            "warp_from": [[400, 400], [500, 400], [500, 500], [400, 500]],
            "warp_to": [[400, 400], [500, 400], [500, 500], [400, 500]],
        },
        "cam_top": {
            "url": "rtsp://192.168.120.182:554/media/video2",
            "crop_ratio": [0.1, 0.9, 0.1, 0.9],
            "warp_from": [[528, 332], [528, 355], [631, 354], [631, 332]],
            "warp_to": [[528, 332], [528, 355], [631, 354], [631, 332]],
        },
        "modbus": {
            "host": "192.168.130.124",
            "port": 504,
        },
        "light_topic_front": "trafficlights/ts1ftl/status",
        "light_topic_rear": "trafficlights/ts1rtl/status",
        "sampler_homing_gpio_port": 23,
    },
}


class PlatesSet:
    def __init__(self, front="", rear=""):
        self.front = front
        self.rear = rear
        self.full = f"{{front}}/{{rear}}"

    def __str__(self):
        return f"front: {self.front} rear: {self.rear}"
