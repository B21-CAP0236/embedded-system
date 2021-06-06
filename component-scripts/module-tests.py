from led import blinkLed
from servo import rotateServo
from camera import capture
from threading import Thread

import RPi.GPIO as GPIO
import atexit

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

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    atexit.register(cleanup)

    led = ThreadWithReturnValue(target=blinkLed, args=(1.5,),)
    led.start()
    camera = ThreadWithReturnValue(target=capture,)
    camera.start()

    camera.join()
    led.join()

    servo = ThreadWithReturnValue(target=rotateServo, args=(4,),)
    servo.start()

    servo.join()
