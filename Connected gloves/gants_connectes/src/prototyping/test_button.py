import RPi.GPIO as GPIO
import pickle
import sys
from gpiozero import MCP3008
import time
import qwiic_icm20948
import sklearn
from joblib import dump, load


BUTTON_GPIO = 16
LED_GPIO = 24


if __name__ == '__main__':
    ##Decomment the code below to activate the button
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    pressed = False
    if not GPIO.input(BUTTON_GPIO):
       if not pressed:
           pressed = True
    else :
        pressed = False
    ## Code for indicator led:
    GPIO.setup(LED_GPIO,GPIO.OUT)
    GPIO.output(LED_GPIO,GPIO.LOW)
    time.sleep(0.5)    
    i = 0
    while i < 1:
        #noise()
        ##Button and led :
        pressed = False
        if not GPIO.input(BUTTON_GPIO):
            if not pressed:
                pressed = True
                GPIO.output(LED_GPIO,GPIO.HIGH)
                time.sleep(1.5)
                GPIO.output(LED_GPIO,GPIO.LOW)
                time.sleep(1.5)


