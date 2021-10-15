# Separate python script to implement FFT calculations on sensor data

# Import python modules:
# Array manipulation utility
import numpy as np
# Plotting library
import matplotlib.pyplot as plt
# FFT function from SciPy
from scipy.fftpack import fft
# Used to serialise data
import pickle

# Import functions from other python scripts
# Import ingestor functions
from ingestor import update_sensor_latest_threshold_breach
# Import firebase storage functions
from firebaseStorageHelper import uploadFFTFiles

import time

# FFT function
def fftFunction(clientNumber, machine_id, sensor_id, timestamp):
    print("~~~~Performing FFT~~~~")
    signalArray = []
    signalFile = open("recievedSignal" + clientNumber + ".txt","r")
    # Store signal data into this instance
    for line in signalFile:
        signalArray.append(line)
    # Declare FFT variables
    if clientNumber == "Test Rig":
        # number of samples in one file
        print(len(signalArray))
        length = len(signalArray)
        # sampling frequency
        Fs = 1592
        #hilbs_sig = hilbert(signalArray)
        #abs_hilbs_sig = [abs(x) for x in hilbs_sig]
        fLength = np.arange(0.0,length/2)
        xtFFT = fft(signalArray)
        print(len(xtFFT))
        down_sample = 1
    elif clientNumber != "PI_3":
        # number of samples in one file
        length = 97656*6
        # sampling frequency
        Fs = 102500
        fLength = np.arange(0.0,length/2)
        xtFFT = fft(signalArray)
        down_sample = 5
    else:
        # number of samples
        length = 839680
        # sampling frequency
        Fs = 20480
        #hilbs_sig = hilbert(signalArray)
        #abs_hilbs_sig = [abs(x) for x in hilbs_sig]
        fLength = np.arange(0.0,length/2)
        xtFFT = fft(signalArray)
        down_sample = 8
    
    # Get array for x-axis (frequency) and y-axis (Amplitude)
    P2 = [abs(x/length) for x in xtFFT]
    endIndex = int(length/2+1)
    P1 = P2[1:endIndex]
    P3 = [x*2 for x in P1]
    f = (Fs*fLength/length)
    fig, ax = plt.subplots()
    print("~~~~FFT Completed~~~~")
    # Make sure x and y axis arrays are equal sizes
    if len(f) != len(P3):  
        f = f[:-1]
    P3_array = np.array(P3)
    #downsample data for webserver plot
    ds_f = f[0:f.size:down_sample]
    ds_P3 = P3[0:P3_array.size:down_sample]
    ax.plot(ds_f,ds_P3)
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency(Hz)')
    plt.title('Spectrum in Python')
    # Combine amplitude and frequency arrays into single array & transpose into separate columns
    FFTdata = np.array([P3,f])
    FFTdata = FFTdata.T
    # Store figure // this chunk of code takes the most of time in FFT 
    with open(clientNumber+'_X.pickle', 'wb') as handle:
        pickle.dump(ds_f, handle)
    with open(clientNumber+'_Y.pickle', 'wb') as handle:
        pickle.dump(ds_P3, handle)
    plt.savefig("generated\\" + sensor_id + ".png" , bbox_inches='tight')
    with open("generated\\" + sensor_id + ".txt", "w") as txt_file:
        for line in FFTdata:
            txt_file.write("%s\n" % line)    
    ## Generated file will contain square brackets so need to remove it (so that can be analysed in Matlab)
    with open("generated\\" + sensor_id + ".txt", 'r') as my_file:
        text = my_file.read()
        text = text.replace("[", "")
        text = text.replace("]", "")
    uploadFFTFiles(sensor_id, timestamp)
    update_sensor_latest_threshold_breach(machine_id, sensor_id, timestamp)