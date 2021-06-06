from config import pins

import RPi.GPIO as GPIO
import atexit
import time

def blinkLed(duration: float):
    RED.start(pwm_freq)
    GREEN.start(pwm_freq)
    BLUE.start(pwm_freq)

    time.sleep(duration)
    
    RED.stop()
    GREEN.stop()
    BLUE.stop()

def cleanup():
    GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

GPIO.setup(pins['r'], GPIO.OUT)
GPIO.setup(pins['g'], GPIO.OUT)
GPIO.setup(pins['b'], GPIO.OUT)

pwm_freq = 100

RED = GPIO.PWM(pins['r'], pwm_freq)
GREEN = GPIO.PWM(pins['g'], pwm_freq)
BLUE = GPIO.PWM(pins['b'], pwm_freq)

if __name__ == "__main__":
    atexit.register(cleanup)

    blinkLed(5)
