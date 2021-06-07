from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QStackedWidget,
    QWidget,
)
from PyQt5 import uic
from config import Config
from threading import Thread
from functools import partial

from component_scripts.led import blinkLed
from component_scripts.camera import capture
from component_scripts.servo import rotateServo

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


class Sensor:
    def __init__(self):
        self.__threads = []
        self.__config = Config()
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
        res = [t.join() for t in self.__threads]
        self.cleanThreads()

        return res

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
        self.runCamera(
            [
                self.__config["filename"],
            ]
        )

        # Wait for capturing finished
        self.joinThreads()

        # TODO
        # Get the NIK and compare to database
        nik = self.getIdCardData(self.__config["filename"], "nik")

        # Push the ID Card out
        self.runServo(4)

        # Wait for all process finished
        self.joinThreads()

        # TODO
        # Return value based on comparison
        return False

    def openSpace(self):
        """
        Rotate the servo to let the
        ID Card get into the cartridge
        """
        self.runServo(11)

    def getIdCardData(self, image, what: str):
        x1, y1, x2, y2 = self.__config[what]
        return self.__model.getKtpData(image, x1, y1, x2, y2)

    def scanFace(self):
        x1, y1, x2, y2 = self.__config["face"]
        image = self.__config["filename"]
        self.addThread(
            target=self.__model.isFaceMatch,
            args=(
                image,
                x1,
                y1,
                x2,
                y2,
            ),
        )


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

    @property
    def condition(self, state):
        try:
            res = self.__condition[state]
            return res
        except:
            return False

    def setCondition(self, state: int, condition: bool):
        if 0 <= state <= 4:
            self.__condition[state] = condition

    def setState(self, state: int):
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
        self.__uidata["start_button"].clicked.connect(partial(self.nextPage, 1))

        # Scan Button
        self.__uidata["scan_button"] = getChild(
            getChild(self.__uidata["container"], QWidget, "IdentityScanPage"),
            QPushButton,
            "ScanButton",
        )
        self.__uidata["scan_button"].clicked.connect(partial(self.nextPage, 2))

    def nextPage(self, nextState):

        # Scan the ID Card first
        if nextState == 0:
            self.sensor.openSpace()
        elif nextState == 2:
            res = self.sensor.runScanSequence()
            self.setCondition(res)
        elif nextState == 4:
            self.sensor.scanFace()
            
            # TODO
            # update the UI accordingly

            res = self.sensor.joinThreads()
            self.setCondition(res)

        # Go to next state if every process above completed successfully
        self.__uidata["container"].setCurrentIndex(nextState)
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
