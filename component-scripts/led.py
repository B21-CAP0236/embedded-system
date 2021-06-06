import RPi.GPIO as GPIO
import atexit
import time

def blinkLed(duration: int):
    RED.start(pwm_freq)
    GREEN.start(pwm_freq)
    BLUE.start(pwm_freq)

    time.sleep(duration)
    
    RED.start(0)
    GREEN.start(0)
    BLUE.start(0)

def cleanup():
    GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

pins = {
    'r': 17,
    'g': 27,
    'b': 22
}

GPIO.setup(pins['r'], GPIO.OUT)
GPIO.setup(pins['g'], GPIO.OUT)
GPIO.setup(pins['b'], GPIO.OUT)

pwm_freq = 100

RED = GPIO.PWM(pins['r'], pwm_freq)
GREEN = GPIO.PWM(pins['g'], pwm_freq)
BLUE = GPIO.PWM(pins['b'], pwm_freq)

atexit.register(cleanup)

if __name__ == "__main__":
    blinkLed(5)
