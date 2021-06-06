from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QStackedWidget,
    QWidget,
)
from PyQt5 import uic
from led import blinkLed
from camera import capture
from threading import Thread
from servo import rotateServo
from functools import partial

import RPi.GPIO as GPIO
import subprocess
import importlib  
import atexit
import time
import sys


def getChild(parent, type, id):
    return parent.findChild(type, id)


class ThreadWithReturnValue(Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None
    ):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


class Sensor():
    def __init__(self):
        self.__threads = []
        self.__model = importlib.import_module("machine-learning.facial-ocr.combined")

    def addThread(self, target, args):
        thread = ThreadWithReturnValue(
            target=target,
            args=args,
        )
        thread.start()

        self.__threads.append(thread)

    def cleanThreads(self):
        for t in self.__threads:
            if not t.is_alive():
                t.handled = True

        self.__threads = [t for t in self.__threads if not t.handled]

    def joinThreads(self):
        _ = [t.join() for t in self.__threads]
        self.cleanThreads()

    def runLed(self, duration):
        self.addThread(
            target=blinkLed,
            args=(duration,),
        )
    
    def runCamera(self, files):
        self.addThread(
            target=capture,
            args=(files,),
        )

    def runServo(self, rotation):
        self.addThread(
            target=rotateServo,
            args=(rotation,),
        )

    def runScanSequence(self) -> bool:
        # Capture the ID Card
        self.runLed(1.5)
        self.runCamera(["captured_card.jpg",])

        # Wait for capturing finished
        self.joinThreads()

        # TODO
        # Get the NIK and compare to database


        # Push the ID Card out
        self.runServo(4)

        # Wait for all process finished
        self.joinThreads()

        # Wait for 3 seconds before
        # setting up the servo for next scan
        time.sleep(3)
        self.runServo(11)

        # TODO
        # Return value based on comparison
        return False


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("ui-components/application.ui", self)

        self.setState(0)
        self.setupSensor()
        self.initializeUI()

    def setupSensor(self):
        self.__sensor = Sensor()

    @property
    def sensor(self):
        return self.__sensor

    def setState(self, state):
        """
        Set current state of the application

        ===|Description
        [0]|Initialization of the application
        [1]|Scanning the ID Card (KTP) of the recipient
        [2]|Report of the scanning result
        [3]|Face recognition phase
        [4]|Final result of authentication
        ===|===

        param:
            state = Int
        """
        if 0 <= state <= 4:
            self.__state = state

    @property
    def state(self):
        return self.__state

    def initializeUI(self) -> None:
        self.__uidata = dict()

        # The page container
        self.__uidata["container"] = self.findChild(QStackedWidget, "StackedWidget")
        self.__uidata["container"].setCurrentIndex(0)

        # Start Button
        self.__uidata["start_button"] = getChild(
            getChild(self.__uidata["container"], QWidget, "WelcomePage"),
            QPushButton,
            "StartButton",
        )
        self.__uidata["start_button"].clicked.connect(
            partial(self.nextPage, self.__uidata["container"].currentIndex(), 1)
        )

        # Scan Button
        self.__uidata["scan_button"] = getChild(
            getChild(self.__uidata["container"], QWidget, "IdentityScanPage"),
            QPushButton,
            "ScanButton",
        )
        self.__uidata["scan_button"].clicked.connect(
            partial(self.nextPage, self.__uidata["container"].currentIndex(), 2)
        )

    def nextPage(self, currentPageIndex, nextState):

        # Scan the ID Card first
        if self.state == 1:
            self.sensor.runScanSequence()

        # Go to next state if every process above completed successfully
        self.__uidata["container"].setCurrentIndex(currentPageIndex + 1)
        self.setState(nextState)


def cleanup():
    GPIO.cleanup()


def main():
    app = QApplication(sys.argv)
    window = UI()
    window.show()

    # Open the window in fullscreen mode
    window.showMaximized()

    # Start the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    atexit.register(cleanup)

    main()
