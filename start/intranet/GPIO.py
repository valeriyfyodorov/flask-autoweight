# brew install zbar
# export LDFLAGS="-L$(brew --prefix zbar)/lib"
# export CFLAGS="-I$(brew --prefix zbar)/include"
# pip install zbarlight

BOARD = 1
OUT = 1
IN = 1
BCM = 1
PUD_UP = 1

def setmode(a):
    # print(a)
    return

def setwarnings(a):
    # print(a)
    return

def setup(a, b, pull_up_down=0):
    # print(a)
    return

def output(a, b):
    # print(a)
    return

def input(a, b=0):
    return True

def cleanup():
    # print(a)
    return

def setwarnings(flag):
    # print("False")
    return