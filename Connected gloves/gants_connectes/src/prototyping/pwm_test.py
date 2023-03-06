import RPi.GPIO as GPIO
from time import sleep
import pandas as pd
from pandas import read_csv
import numpy as np

df = read_csv("new_tone.csv", header = 0, index_col = 0)

ledpin = 12  # PWM pin connected to LED
GPIO.setwarnings(False)  # disable warnings
GPIO.setmode(GPIO.BOARD)  # set pin numbering system
GPIO.setup(ledpin, GPIO.OUT)
pi_pwm = GPIO.PWM(ledpin, 1000)  # create PWM instance with frequency
pi_pwm.start(0)  # start PWM of required Duty Cycle

for freq, duty_cycle in zip(df['freq'], df['duty_cycle']):
    pi_pwm.ChangeFrequency(freq)
    pi_pwm.ChangeDutyCycle(duty_cycle)
    sleep(1/freq)
'''
pi_pwm.ChangeDutyCycle(50)
while True:
    for duty in range(50, 1001, 1):
        pi_pwm.ChangeFrequency(duty)  # provide duty cycle in the range 0-100
        sleep(0.01)
    sleep(0.5)

    for duty in range(1000, 49, -1):
        pi_pwm.ChangeFrequency(duty)
        sleep(0.01)
    sleep(0.5)
'''
