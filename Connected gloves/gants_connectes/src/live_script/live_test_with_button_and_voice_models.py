import RPi.GPIO as GPIO #button and LED library
import pickle #data arrangement library
import sys #to read arg in console
import gtts #google text to speech library
import os #save and execute lame
import time
from gpiozero import MCP3008 #ADC library
from icm20948 import ICM20948 #Accelerometer library

import sklearn #to interpret machine learning models
from joblib import dump, load



# Function that measures the data over an extended period of time and returns it as one line
def measure_data( adcs, nb_data, multi_data, IMU ):

    for j in range(nb_data * multi_data):

        for i in range(5):
            adc = adcs[i]
            data.append(3.3 * adc.value)
        mxRaw, myRaw, mzRaw = IMU.read_magnetometer_data()
        axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw = IMU.read_accelerometer_gyro_data()

        data.extend([axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw, mxRaw, myRaw, mzRaw])

        # time.sleep(0.1*nb_data/(15*multi_data))
    print(data[0:14])
    print("data captured")
    return data

BUTTON_GPIO = 16
LED_GPIO = 24



if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(LED_GPIO,GPIO.OUT)
    GPIO.output(LED_GPIO,GPIO.LOW)

    modelnames = []
    models = []

    try:
        model_file = str(sys.argv[1])
    except:
        modelnames.append('models/model_both_raw_GaussianNB.sav') #we select the models we want to load
        modelnames.append('models/model_both_raw_KNN.sav')


    for i in range(len(modelnames)):
        print('loading model from', modelnames[i])
        models.append(load(modelnames[i]))




    adcs = [] #to store the different adc input and use them in fonctions

    IMU = ICM20948() #accelerometer set up

    nb_data = 15 #measure 15 data
    multi_data = 3 #times 3 if you want to average things up post measure for example

    for j in range(5):
        adcs.append(MCP3008(channel=j, device=0))


    while True :
        ##Button and led :
        if not GPIO.input(BUTTON_GPIO): #we enter if we press the button
            #button set to 1 GPIO.input sends ones when button is NOT pressed
            #time.sleep(0.2)
            GPIO.output(LED_GPIO,GPIO.HIGH) #LED light up
            print("Measuring")
            data = []

            data = measure_data(adcs, nb_data, multi_data, IMU) #measure data
            GPIO.output(LED_GPIO, GPIO.LOW) #LED is turned off
            prediction = models[1].predict([data]) #we predict with KNN
            #KNN is very good for words not so much for letter
            if len(prediction[0]) == 1 : #if the prediction is a letter we let NBgaussian do the trick
                prediction = models[0].predict([data])

            print('Last predicted character:', prediction[0])#prediction is a numpy array with a string in it
            speech = gtts.gTTS(text=prediction[0], lang='fr') #transform it to speech recquires WIFI
            speech.save('speech.mp3') #save
            os.system("lame --decode speech.mp3 speech.wav") #change file from mp3 to wav
            os.system("aplay speech.wav") #read wav file





        prediction = ''#model.predict([data]) #reset prediction

