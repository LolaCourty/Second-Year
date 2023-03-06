import RPi.GPIO as GPIO
import pickle
import sys

import time
from gpiozero import MCP3008
from icm20948 import ICM20948
import integration_algo
import numpy as np
import sklearn
from joblib import dump, load

def noise():
    pi_pwm.ChangeDutyCycle(50)
    time.sleep(0.1)
    pi_pwm.ChangeDutyCycle(0)

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

def quick_process(data):
    processed_data = list(data)
    indexes = [i % 5 + 14 * (i // 5) for i in range(0, 20 * 5)]
    indexes.extend([i % 3 + 14 * (i // 3) + 11 for i in range(0, 20 * 5)])
    indices = sorted(indexes, reverse=True)

    for idx in indices:
        if idx < len(processed_data):
            processed_data.pop(idx)
    return processed_data

def traitement_avec_algo(tracker, data, nb_data, multi_data):

    tempcol = [data[i * 14 + 6:i * 14 + 15] for i in range(len(data) // 14)]


    datarray = np.array(tempcol)
    init_list = tracker.initialize(datarray[5:30])
    # EKF
    a_nav, orix, oriy, oriz = tracker.attitudeTrack(datarray[30:], init_list)
    # filter a_nav
    a_nav_filtered = tracker.removeAccErr(a_nav, filter=False)
    # get velocity
    v = tracker.zupt(a_nav_filtered, threshold=0.2)
    # get position
    p = tracker.positionTrack(a_nav_filtered, v)
    datadef = [data[0]]
    #plist = p.tolist()
    #On récupère les orientations
    orixlist = orix.tolist()
    oriylist = oriy.tolist()
    orizlist = oriz.tolist()
    accx = [data[i*14+7] for i in range(nb_data*multi_data)]
    max_acc_x = max(accx)
    min_acc_x =  min(accx)
    accy = [data[i * 14 + 8] for i in range(nb_data * multi_data)]
    max_acc_y = max(accy)
    min_acc_y = min(accy)
    accz = [data[i * 14 + 9] for i in range(nb_data * multi_data)]
    max_acc_z = max(accz)
    min_acc_z = min(accz)

    moyenne = [0]*nb_data*5
    for k in range(nb_data):
        for j in range(multi_data):
            for i in range(5):
                moyenne[k*5 +i] += tempcol[k*multi_data + j][i]/multi_data



    datadef.extend(moyenne)
    liste_orix = []
    liste_oriy = []
    liste_oriz= []


    datadef.extend([max_acc_x, min_acc_x, max_acc_y, min_acc_y, max_acc_z, min_acc_z]) #tempcol[j * multi_data + 30]])

    for col in orix:
        for i in range(3):
            liste_orix.append(col[i])

    for col in oriy:
        for i in range(3):
            liste_oriy.append(col[i])

    for col in oriz:
        for i in range(3):
            liste_oriz.append(col[i])

    datadef.extend(liste_orix)
    datadef.extend(liste_oriy)
    datadef.extend(liste_oriz)
    return datadef


if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.setup(LED_GPIO,GPIO.OUT)
    GPIO.output(LED_GPIO,GPIO.LOW)
    model_restricted_names= []
    model_processed_names = []
    modelnames = []
    models = []
    models_restricted = []
    models_processed = []
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
        model_processed_names.append('models/model_button_GaussianNB.sav')
        model_processed_names.append('models/model_button_KNN.sav')
        model_processed_names.append('models/model_button_LDA.sav')
        model_restricted_names.append('models/model_button_raw_restricted_GaussianNB.sav')
        model_restricted_names.append('models/model_button_raw_restricted_KNN.sav')
        model_restricted_names.append('models/model_button_raw_restricted_LDA.sav')

    for i in range(len(modelnames)):
        print('loading model from', modelnames[i])
        models.append(load(modelnames[i]))

    for i in range(len(model_processed_names)):
        print('loading model from', model_processed_names[i])
        models_processed.append(load(model_processed_names[i]))

    for i in range(len(model_restricted_names)):
        print('loading model from', model_restricted_names[i])
        models_restricted.append(load(model_restricted_names[i]))


    adcs = []

    IMU = ICM20948()
    tracker = integration_algo.IMUTracker(sampling=100)
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
            data = []  # measure_data(adcs)
            data_restricted = []
            data = measure_data(adcs, nb_data, multi_data, IMU)

            for j in range(len(models)):
                prediction = models[j].predict([data])
                print('model:', modelnames[j], 'Last predicted character:', prediction)

            for i in range(len(models_restricted)):
                data_restricted = quick_process(data)
                prediction = models_restricted[i].predict([data_restricted])
                print('model:', model_restricted_names[i], 'Last predicted character:', prediction)

            unprocessed_data = ["A"]
            unprocessed_data.extend(data)
            processed_data = traitement_avec_algo(tracker, unprocessed_data, nb_data, multi_data)[1:]


            for i in range(len(models_processed)):
                prediction = models_processed[i].predict([processed_data])
                print('model:', model_processed_names[i], 'Last predicted character:', prediction)

            GPIO.output(LED_GPIO,GPIO.LOW)

        prediction = ''#model.predict([data])
        #print('Last predicted character:', prediction)
