from PyQt5.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QApplication,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QWidget,
)
from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import (
    QImage,
    QPixmap,
)

from PyQt5 import uic
from config import Config
from threading import Thread
from functools import partial

from component_scripts.led import blinkLed
from component_scripts.camera import capture
from component_scripts.servo import rotateServo

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

import RPi.GPIO as GPIO
import importlib
import requests
import atexit
import json
import time
import sys


def getChild(parent, type, id):
    return parent.findChild(type, id)


class CameraThread(QThread):
    _signal = pyqtSignal(int, QImage)

    def __init__(self, model, config):
        super().__init__()
        self.__model = model
        self.__config = config
        self.__result = None

    def __del__(self):
        self.wait()

    def run(self):
        x1, y1, x2, y2 = self.__config["face"]
        image = self.__config["filename"]

        self.__result = self.__model.isFaceMatch(
            image, x1, y1, x2, y2, show=False, signal=self._signal
        )


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
    def __init__(self, backend):
        self.__threads = []
        self.__config = Config().configuration
        self.__model = importlib.import_module("machine-learning.facial-ocr.combined")

        self.setBackend(backend)

    def setBackend(self, backend):
        self.__backend = backend

    @property
    def backend(self):
        return self.__backend

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

        nik = self.getIdCardData(self.__config["filename"], "nik")
        recipients = self.backend.getAvailableRecipients(self.__config["bansos_id"])

        ratios = [
            list([self.__model.similar(x["nik"], nik), x["nama"], x["id"]])
            for x in recipients
        ]
        ratios = sorted(ratios)[0]

        # Push the ID Card out
        self.runServo(4)

        # Wait for all process finished
        self.joinThreads()

        if len(ratios) > 0:
            isVerified = ratios[0] > 0.8
            return (isVerified, list([ratios[1], ratios[2]]) if isVerified else nik)
        else:
            return None

    def openSpace(self):
        """
        Rotate the servo to let the
        ID Card get into the cartridge
        """
        self.runServo(11)

    def getIdCardData(self, image, what: str):
        x1, y1, x2, y2 = self.__config[what]
        return self.__model.getKtpData(image, x1, y1, x2, y2)

    def scanFace(self, callback_function):
        self.__camthread = CameraThread(self.__model, self.__config)
        self.__camthread._signal.connect(callback_function)
        self.__camthread.start()

        while True:
            if self.__camthread.__result != None:
                return self.__camthread.__result


class Backend:
    def __init__(self, username, password):
        self.login(username, password)
        self.setupConnection()

    def setUid(self, uid):
        self.__uid = uid

    @property
    def uid(self):
        return self.__uid

    def setCookie(self, cookie):
        self.__cookie = cookie

    @property
    def cookie(self):
        return self.__cookie

    def setupConnection(self):
        transport = RequestsHTTPTransport(
            url="https://anantara.hasura.app/v1/graphql",
            verify=True,
            retries=3,
            headers={
                "content-type": "application/json",
                "Authorization": "Bearer {}".format(self.cookie),
            },
        )
        self.__client = Client(transport=transport, fetch_schema_from_transport=True)

    @property
    def client(self):
        return self.__client

    def login(self, username, password):
        data = json.dumps({"username": username, "password": password})

        response = requests.post(
            "https://us-central1-anantara-dream-team-cap0236.cloudfunctions.net/userlogin",
            headers={
                "Content-Type": "application/json",
            },
            data=data,
        )

        self.setCookie(response.text)

    def addTransaction(self, bansos_id):
        data = json.dumps({"bansos_id": bansos_id, "receipient_id": self.uid})

        _ = requests.post(
            "https://anantara.hasura.app/api/rest/add/transaction",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.cookie),
            },
            data=data,
        )

    def getAvailableRecipients(self, bansos_id) -> list:
        data = json.dumps({"_eq": bansos_id})

        response = requests.post(
            "https://anantara.hasura.app/api/rest/get/bansos_transaction",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.cookie),
            },
            data=data,
        )

        notAvailableRecipients = [
            x["receipient_id"] for x in json.loads(response.text)["transactions"]
        ]

        query = gql(
            r"""
                query MyQuery {
                    receipientMap(where: {bansos_id: {_eq: %(eq)s}, _and: {receipient_id: {_nin: %(nin)s}}}) {
                        receipient {
                        id
                        nik
                        nama
                        }
                    }
                }
            """
            % {"eq": bansos_id, "nin": notAvailableRecipients}
        )

        result = self.client.execute(query)
        if len(result["receipientMap"]) > 0:
            return [x["receipient"] for x in result["receipientMap"]]
        else:
            return None


class UI(QMainWindow):
    def __init__(self, backend):
        super(UI, self).__init__()
        uic.loadUi("ui-components/application.ui", self)

        self.__condition = dict()

        self.setState(0)
        self.initializeUI()
        self.setBackend(backend)
        self.setupSensor(backend)

    def setBackend(self, backend):
        self.__backend = backend

    @property
    def backend(self):
        return self.__backend

    def setupSensor(self, backend):
        self.__sensor = Sensor(backend)

    @property
    def sensor(self):
        return self.__sensor

    def setCondition(self, state: int, condition: bool):
        if 0 <= state <= 4:
            self.__condition[state] = condition

        self.checkCondition(state)

    def checkCondition(self, state):
        if state == 1:
            if self.condition(state):
                self.uidata["failed_text"].hide()
                self.uidata["success_text"].show()
                self.uidata["back_button"].hide()
                self.uidata["next_button"].show()
            else:
                self.uidata["failed_text"].show()
                self.uidata["success_text"].hide()
                self.uidata["back_button"].show()
                self.uidata["next_button"].hide()
        elif state == 3:
            if self.condition(state):
                self.uidata["not_verified_text"].hide()
                self.uidata["verified_text"].show()
            else:
                self.uidata["not_verified_texts"].show()
                self.uidata["verified_text"].hide()

    def condition(self, state):
        try:
            res = self.__condition[state]
            return res
        except:
            return False

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
        self.__uidata["container"].currentChanged.connect(self.checkPage)
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

        # Failed and Success Text
        self.__uidata["failed_text"] = getChild(
            getChild(self.__uidata["container"], QWidget, "VerificationPage"),
            QLabel,
            "FailedText",
        )
        self.__uidata["success_text"] = getChild(
            getChild(self.__uidata["container"], QWidget, "VerificationPage"),
            QLabel,
            "SuccessText",
        )

        # Next and Back Button
        self.__uidata["next_button"] = getChild(
            getChild(self.__uidata["container"], QWidget, "VerificationPage"),
            QPushButton,
            "NextButton",
        )
        self.__uidata["back_button"] = getChild(
            getChild(self.__uidata["container"], QWidget, "VerificationPage"),
            QPushButton,
            "BackButton",
        )
        self.__uidata["next_button"].clicked.connect(partial(self.nextPage, 3))
        self.__uidata["back_button"].clicked.connect(partial(self.nextPage, 0))

        # Image Viewer and Progress Bar
        self.__uidata["image_viewer"] = getChild(
            getChild(self.__uidata["container"], QWidget, "PhotoScanPage"),
            QGraphicsView,
            "ImageViewer",
        )
        self.__uidata["progress_bar"] = getChild(
            getChild(self.__uidata["container"], QWidget, "PhotoScanPage"),
            QProgressBar,
            "ScanLoader",
        )
        self.__uidata["progress_bar"].setMinimum(0)
        self.__uidata["progress_bar"].setMaximum(5)
        self.__uidata["progress_bar"].setValue(0)

        # Not Verified and Verified Text
        self.__uidata["not_verified_text"] = getChild(
            getChild(self.__uidata["container"], QWidget, "FinalPage"),
            QLabel,
            "NotVerifiedText",
        )
        self.__uidata["verified_text"] = getChild(
            getChild(self.__uidata["container"], QWidget, "FinalPage"),
            QLabel,
            "VerifiedText",
        )

    @property
    def uidata(self):
        return self.__uidata

    def checkPage(self):
        currentPage = self.__uidata["container"].currentIndex()

        if currentPage == 4:
            time.sleep(5)

            self.uidata["container"].setCurrentIndex(0)
            self.setState(0)

        elif currentPage == 3:
            self.nextPage(4)
            
        elif currentPage == 0:
            # Let another ID Card in
            self.__sensor.runServo(4)

            # Wait for all process finished
            self.__sensor.joinThreads()

    def nextPage(self, nextState):

        # Scan the ID Card first
        if nextState == 0:
            self.sensor.openSpace()
        elif nextState == 2:
            result = self.sensor.runScanSequence()

            try:
                isVerified, data = result
            except:
                self.sensor.runServo(12)
                self.sensor.joinThreads()
                sys.exit("Error happened, call engineer")

            self.setCondition(self.state, isVerified)

            if isVerified:
                nik, uid = data
                self.backend.setUid(uid)
            else:
                nik = data

            self.uidata["failed_text"].setText(
                self.uidata["failed_text"].text().replace(r"{{ receipient }}", nik)
            )
            self.uidata["success_text"].setText(
                self.uidata["success_text"].text().replace(r"{{ receipient }}", nik)
            )
        elif nextState == 4:
            res = self.sensor.scanFace(self.updateCamera)
            self.setCondition(self.state, res)

            # Send transaction to the cloud
            # if it completed successfully
            if self.condition(self.state):
                config = Config().configuration
                self.backend.addTransaction(config["bansos_id"])

        # Go to next state if every process above completed successfully
        self.uidata["container"].setCurrentIndex(nextState)
        self.setState(nextState)

    @pyqtSlot(int, QImage)
    def updateCamera(self, progress, image):
        scene = QGraphicsScene(self)
        item = QGraphicsPixmapItem(QPixmap.fromImage(image))

        scene.addItem(item)

        self.__uidata["image_viewer"].setScene(scene)
        self.__uidata["progress_bar"].setValue(progress)


def cleanup():
    GPIO.cleanup()


def main():
    app = QApplication(sys.argv)

    username = input("Username = ")
    password = input("Password = ")
    backend = Backend(username, password)

    window = UI(backend)
    window.show()

    # Open the window in fullscreen mode
    window.showMaximized()

    # Start the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    atexit.register(cleanup)

    main()
