from .config import MAC_OS

if MAC_OS:
    from . import GPIO
else:
    import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO_BUZZER = 26
GPIO.setup(GPIO_BUZZER, GPIO.OUT)
GPIO.output(GPIO_BUZZER, False)

GPIO_LAMP = 22
GPIO.setup(GPIO_LAMP, GPIO.OUT)
GPIO.output(GPIO_LAMP, False)

