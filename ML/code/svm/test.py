import os
import csv
import re
import datetime
import numpy as np
import math
import Arrays as ar
import pandas as pd

# print(np.correlate([1, 2, 3], [0, 1, 0.5]))

subDirs = ['Knocker']
now = datetime.datetime.now()
# avgModelFileName = "\\..\\processed\\avgModel_hs_terrace"+' '+str(now).replace(':','-')+".csv"

motionTimeLen = 32
motionSampleRate = 400
motionFFTLen = 256

outFilePrefix = 'dataset'
dataTypeList = ['time']
normalization = True

TIME = False
MAIN = True
DIFF_NUM = False #different number of training data
SIMILAR_COMBINE = False #combine similar objects set (books and bottles) for CHI 19


def minMaxScaler(array1d, range=(1, 0)):
    scaleRange = range
    arrMax = max(array1d)
    arrMin = min(array1d)
    scaled = []
    for x in array1d:
        xScaled = (scaleRange[0] - scaleRange[1]) * (x - arrMin) / (arrMax - arrMin) + scaleRange[1]
        scaled.append(xScaled)
    return scaled


def logMag(inputF):
    # input: Freq domain data
    logFeatures = []
    for x in inputF:  # BZV, FAP
        if x == 0:
            print('fft output is zero')
            logFeatures.append(0)
            # csvRow.append(math.log10(sys.float_info.min * sys.float_info.epsilon))
        else:
            logFeatures.append(math.log10(x))
    return logFeatures


def MFCC(inputT):
    from python_speech_features import mfcc

    mfccFFTLen = 2048
    signal = np.asarray(inputT)
    signal.reshape((len(inputT), 1))
    mfccFeatures = []
    mfcc_feat = mfcc(signal, micSampleRate, nfft=mfccFFTLen)  # mfcc1

    for i in range(8):
        for j in range(13):
            mfccFeatures.append(mfcc_feat[i][j])
    return mfccFeatures


def FFTWithDummy(inputT, lenOri, lenFull):  # input: 4096 time, output: 4096+1 freq
    inputWithDummy = inputT + [0] * int(lenFull - lenOri)  # add dummy
    csvRow = abs(np.fft.fft(inputWithDummy))[:int(lenFull / 2) + 1]
    return csvRow


if __name__ == "__main__":

    ### for each file
    for dirname, dirnames, filenames in os.walk(dataPath):
        for i, filename in enumerate(filenames):
            if '.meta.csv' in filename: #ignore .meta.csv files from real world experiement
                continue
            if i % 100 == 0:
                print("Processing:" + str(i + 1) + "/" + str(len(filenames)))
            fpath = os.path.join(dirname, filename)

            ### get row of max magnitude
            with open(fpath, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar=' ')

                ### GT labeling
                nominalLabel, gtLabel = getGTLabel(fpath)

                if gtLabel == -1:
                    continue

                row = 0
                for x in reader:
                    row = x
                print(fpath)
                row = [float(x) for x in row[:-1]]  # remove last newline, convert datatype

                normRow = []
                if dataType == 'time':
                    freq = abs(np.fft.fft(row[0:micFFTLen])[:(micFFTLen / 2) + 1])
                    # TODO: minmax scale can be worse than dividing with max?

                    aX = row[micFFTLen:micFFTLen + motionTimeLen]
                    aY = row[micFFTLen + motionTimeLen:micFFTLen + motionTimeLen * 2]
                    aZ = row[micFFTLen + motionTimeLen * 2:micFFTLen + motionTimeLen * 3]
                    gX = row[micFFTLen + motionTimeLen * 3:micFFTLen + motionTimeLen * 4]
                    gY = row[micFFTLen + motionTimeLen * 4:micFFTLen + motionTimeLen * 5]
                    gZ = row[micFFTLen + motionTimeLen * 5:micFFTLen + motionTimeLen * 6]

                    accAbs = []
                    gyroAbs = []

                    for i in range(32):
                        accAbs.append(math.sqrt(aX[i] ** 2 + aY[i] ** 2 + aZ[i] ** 2))
                        gyroAbs.append(math.sqrt(gX[i] ** 2 + gY[i] ** 2 + gZ[i] ** 2))

                    micFeatures = []
                    logFeatures = []
                    mfccFeatures = []
                    accFeatures = []
                    gyroFeatures = []

                    if not dataLocation.endswith('A') and not dataLocation.endswith(
                            'G'):  # then include sound
                        if not dataLocation.endswith('Sb') and not dataLocation.endswith(
                            'Sc'):
                            micFeatures = minMaxScaler(freq)

                        if not dataLocation.endswith('Sa') and not dataLocation.endswith(
                                'Sc'):
                            logFeatures = minMaxScaler(logMag(freq))

                        if not dataLocation.endswith('Sa') and not dataLocation.endswith(
                                'Sb'):
                            mfccFeatures = minMaxScaler(MFCC(row[:micFFTLen]))

                    if not dataLocation.endswith('S') and not dataLocation.endswith('Sa') \
                            and not dataLocation.endswith(
                        'Sb') and not dataLocation.endswith('Sc') \
                            and not dataLocation.endswith('G'):  # then include acc:
                        # Ax Ay Az Gx Gy Gz
                        # accFeatures = np.asarray(FFTWithDummy(aX, 32, 256)).tolist() + np.asarray(FFTWithDummy(aY, 32,
                        #                                                        256)).tolist() + np.asarray(FFTWithDummy(
                        #     aZ, 32, 256)).tolist()

                        # sqrt(Ax^2+Ay^2+Az^2)
                        # accFeatures = minMaxScaler(FFTWithDummy(accAbs, 32, 256))

                        # only Ax -> for evaluation
                        accFeatures = minMaxScaler(
                            FFTWithDummy(aX, motionTimeLen, motionFFTLen))

                        #
                        # sqrt(Ax^2+Ay^2+Az^2)
                        # gyroFeatures = minMaxScaler(accAbs)

                    if not dataLocation.endswith('S') and not dataLocation.endswith('Sa') \
                            and not dataLocation.endswith(
                        'Sb') and not dataLocation.endswith('Sc') \
                            and not dataLocation.endswith('A'):  # then include gyro:
                        # Gx Gy Gz
                        # gyroFeatures = np.asarray(FFTWithDummy(gX, 32, 256)).tolist() + np.asarray(FFTWithDummy(gY, 32,
                        #                                                         256)).tolist() + np.asarray(FFTWithDummy(
                        #     gZ, 32, 256)).tolist()

                        # sqrt(Gx^2+Gy^2+Gz^2)
                        # gyroFeatures = minMaxScaler(FFTWithDummy(gyroAbs, 32, 256))

                        # only Gz -> for evaluation
                        gyroFeatures = minMaxScaler(
                            FFTWithDummy(gZ, motionTimeLen, motionFFTLen))
                        # gyroFeatures = minMaxScaler(gyroAbs)

                    normRow = (
                            micFeatures + logFeatures + mfccFeatures + accFeatures + gyroFeatures)
                # normRow.append(gtLabel)
                normRow.append(nominalLabel)

                wr.writerow(normRow)