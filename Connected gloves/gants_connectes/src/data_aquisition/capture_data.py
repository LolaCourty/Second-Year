
import pickle
import sys
from gpiozero import MCP3008
from icm20948 import ICM20948
import time
import numpy as np
import integration_algo


#Function that measures the data over an extended period of time and returns it as one line
def measure_data(ident, adcs, nb_data, multi_data, IMU ):

    data = [ident]
    for j in range(nb_data*multi_data):

        for i in range(5):
            adc = adcs[i]
            data.append(3.3 * adc.value)
        mxRaw, myRaw,mzRaw = IMU.read_magnetometer_data()
        axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw = IMU.read_accelerometer_gyro_data()

        data.extend([axRaw, ayRaw, azRaw, gxRaw, gyRaw, gzRaw, mxRaw, myRaw, mzRaw])


        #time.sleep(0.1*nb_data/(15*multi_data))


    print("data captured")
    return data

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
            liste_oriy.append(col[i])
            liste_oriz.append(col[i])

    datadef.extend(liste_orix)
    datadef.extend(liste_oriy)
    datadef.extend(liste_oriz)
    return datadef



def append_new_line(file_name, text_to_append):
    """Append given text as a new line at the end of file"""
    # Open the file in append & read mode ('a+')
    with open(file_name, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(text_to_append)


if __name__ == '__main__':
    try:
        filename = str(sys.argv[1]) + ".txt"
        filename2 =  str(sys.argv[1]) + "_Raw" + ".txt"
    except:
        filename = 'learning_data.txt'
        filename2 = 'learning_data_Raw.txt'
    print('Storing data in', filename)

    data = []
    unprocessed_data = []
    adcs = []
    tracker = integration_algo.IMUTracker(sampling=100)
    IMU = ICM20948()

    nb_data = 15
    multi_data = 3
    for i in range(5):
        adcs.append(MCP3008(channel=i))
    i = -1
    while i < 1:
        ident = input("Enter character to be learned:")
        if ident == "del":
            i = -1
            print("not saving", data)
        elif ident == "$":
            if i != -1:
                print("appending")
                append_new_line(filename, ', '.join([str(dat) for dat in data]))
                append_new_line(filename2, ', '.join([str(dat) for dat in unprocessed_data]))
            print("Data saved, stopping now!")
            i = 1
        else:
            if i != -1:
                print("appending")
                append_new_line(filename, ', '.join([str(dat) for dat in data]))
                append_new_line(filename2, ', '.join([str(dat) for dat in unprocessed_data]))
            i = 0
            print("Capturing values...")
            unprocessed_data = measure_data(ident, adcs, nb_data, multi_data, IMU)
            data = traitement_avec_algo(tracker, unprocessed_data, nb_data, multi_data)
            print(unprocessed_data[0:14])
            print("done.", i)
