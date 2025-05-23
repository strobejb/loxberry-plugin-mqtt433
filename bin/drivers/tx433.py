import time
import sys
import RPi.GPIO as GPIO 


TRANSMIT_PIN = 27
NUM_ATTEMPTS = 15


#
#   code - binary string to transmit. 
#          i.e. '0000001111100' for power
#
#   times - number of attempts to transmit the code
#
def transmit_code(code, TRANSMIT_PIN=TRANSMIT_PIN, NUM_ATTEMPTS=NUM_ATTEMPTS,
                        LONG_DELAY=0.00058, 
                        SHORT_DELAY=0.000256, 
                        EXTENDED_DELAY=0.0162):
    '''Transmit a chosen code string using the GPIO transmitter'''
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRANSMIT_PIN, GPIO.OUT)
    for t in range(NUM_ATTEMPTS):
        for i in code:
            if i == '1':
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(SHORT_DELAY)
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(LONG_DELAY)
            elif i == '0':
                GPIO.output(TRANSMIT_PIN, 0)
                time.sleep(LONG_DELAY)
                GPIO.output(TRANSMIT_PIN, 1)
                time.sleep(SHORT_DELAY)
            else:
                continue
        GPIO.output(TRANSMIT_PIN, 0)
        time.sleep(EXTENDED_DELAY)
    GPIO.cleanup()

