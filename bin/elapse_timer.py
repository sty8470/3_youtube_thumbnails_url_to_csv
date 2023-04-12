
import sys
import os
  
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

# from crawl_google_images import GCrawler, webdriver
import threading

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))
sys.path.append(os.path.normpath(os.path.join(current_path, '../../')))

class TimeDisplayWorker(QtCore.QThread):
    time_signal = QtCore.pyqtSignal(int)
    job_finished_signal = QtCore.pyqtSignal(bool)
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.working = True
        self.job_finished = False

    def run(self):        
        display_time = 0
        self.working = True
        while self.working:
            self.time_signal.emit(display_time)            
            display_time += 1
            self.sleep(1)
        self.job_finished_signal.emit(True)
    def stop(self):
        # https://developer-mistive.tistory.com/58
        self.working = False
        self.quit()
        self.wait(5000)