from .config import pins

import RPi.GPIO as GPIO
import time
import sys


def rotateServo(to_rotation: float):
    """
    Rotate the servo

    Param:
        to_rotation = In our hardware,
            4 means push the ID Card off
            12 means let the ID Card in
    """
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(pins["servo"], GPIO.OUT)

    pwm_freq = 50
    servo = GPIO.PWM(pins["servo"], pwm_freq)
    servo.start(0)

    servo.ChangeDutyCycle(to_rotation)
    time.sleep(0.5)
    servo.stop()

    GPIO.cleanup()

if __name__ == "__main__":
    rotateServo(float(sys.argv[1]))
