

import RPi.GPIO as GPIO
import pickle
import sys

import time
from gpiozero import MCP3008
from icm20948 import ICM20948

import sklearn
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

def quick_process(data): #without magnoetometer
    processed_data = list(data)
    indexes = [i % 5 + 14 * (i // 5) for i in range(0, 20 * 5)]
    indexes.extend([i % 3 + 14 * (i // 3) + 11 for i in range(0, 20 * 5)])
    indices = sorted(indexes, reverse=True)

    for idx in indices:
        if idx < len(processed_data):
            processed_data.pop(idx)
    return processed_data

if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(LED_GPIO,GPIO.OUT)
    GPIO.output(LED_GPIO,GPIO.LOW)
    model_restricted_names= []
    modelnames = []
    models = []
    models_restricted = []
    try:
        model_file = str(sys.argv[1])
    except:
        modelnames.append('models/model_both_raw_GaussianNB.sav')
        modelnames.append('models/model_both_raw_KNN.sav')
        modelnames.append('models/model_both_raw_LDA.sav')
        modelnames.append('models/model_both_raw_Tree.sav')
        modelnames.append('models/model_final_raw_GaussianNB.sav')
        modelnames.append('models/model_final_raw_KNN.sav')
        modelnames.append('models/model_final_raw_LDA.sav')
        modelnames.append('models/model_final_raw_Tree.sav')
        modelnames.append('models/model_button_raw_GaussianNB.sav')
        modelnames.append('models/model_button_raw_KNN.sav')
        modelnames.append('models/model_button_raw_LDA.sav')
        model_restricted_names.append('models/model_button_raw_restricted_GaussianNB.sav')
        model_restricted_names.append('models/model_button_raw_restricted_KNN.sav')
        model_restricted_names.append('models/model_button_raw_restricted_LDA.sav')

    for i in range(len(modelnames)):
        print('loading model from', modelnames[i])
        models.append(load(modelnames[i]))

    for i in range(len(model_restricted_names)): #without magnetometer
        print('loading model from', model_restricted_names[i])
        models_restricted.append(load(model_restricted_names[i]))


    adcs = []

    IMU = ICM20948()

    nb_data = 15
    multi_data = 3

    for j in range(5):
        adcs.append(MCP3008(channel=j, device=0))


    while True :
        ##Button and led :
        if not GPIO.input(BUTTON_GPIO):
            #time.sleep(0.2)
            GPIO.output(LED_GPIO,GPIO.HIGH)
            print("Measuring")
            data = []# measure_data(adcs)
            data_restricted = []
            data = measure_data(adcs, nb_data, multi_data, IMU)

            for j in range(len(models)):
                prediction = models[j].predict([data])
                print('model:', modelnames[j] ,'Last predicted character:', prediction)
            for i in range(len(models_restricted)):
                data_restricted = quick_process(data) #data has not the same shape withou magnetometer so we separate
                prediction = models_restricted[i].predict([data_restricted])
                print('model:', model_restricted_names[i] ,'Last predicted character:', prediction)
            GPIO.output(LED_GPIO,GPIO.LOW)

        prediction = ''#model.predict([data])
        #print('Last predicted character:', prediction)

