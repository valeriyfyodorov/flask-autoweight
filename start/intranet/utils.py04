import time
from shutil import copyfile
import os


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


def archiveFileName(folder, suffix, prefix="", saveTime=True):
    file_header = str(prefix)
    if (saveTime):
        file_header += time.strftime("%Y%m%d_%H%M")
    file_header += str(suffix)
    year, month, day = time.strftime("%Y %m %d").split()
    destination_dir = folder + "{}/{}/{}/".format(year, month, day)
    os.makedirs(destination_dir, exist_ok=True)
    return destination_dir + file_header


def dictFromArgs(args):
    return args.to_dict(flat=True)
