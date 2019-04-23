import os
import time
from ctypes import *

import numpy as np

import xlwt

#
os.chdir("C:\\Tektronix\\RSA_API\\lib\\x64")
rsa = cdll.LoadLibrary("RSA_API.dll")
# ctypes.windll.LoadLibrary("C:\\Tektronix\\RSA_API\\lib\\x64\\RSA_API.dll")

# create Spectrum_Settings data structure


class Spectrum_Settings(Structure):
    _fields_ = [('span', c_double),
                ('rbw', c_double),
                ('enableVBW', c_bool),
                ('vbw', c_double),
                ('traceLength', c_int),
                ('window', c_int),
                ('verticalUnit', c_int),
                ('actualStartFreq', c_double),
                ('actualStopFreq', c_double),
                ('actualFreqStepSize', c_double),
                ('actualRBW', c_double),
                ('actualVBW', c_double),
                ('actualNumIQSamples', c_double)]


class Spectrum_TraceInfo(Structure):
    _fields_ = [('timestamp', c_int64), ('acqDataStatus', c_uint16)]


def search_connect():
    # search/connect variables
    numFound = c_int(0)
    intArray = c_int * 10
    deviceIDs = intArray()
    # this is absolutely asinine, but it works
    deviceSerial = c_char_p("longer than the longest serial number".encode('utf-8'))        
    deviceType = c_char_p("longer than the longest device type".encode('utf-8'))
    apiVersion = c_char_p("api".encode('utf-8'))

    # get API version
    rsa.DEVICE_GetAPIVersion(apiVersion)
    print('API Version {}'.format(apiVersion.value))

    # search
    ret = rsa.DEVICE_Search(byref(numFound), deviceIDs,
                            deviceSerial, deviceType)

    if ret != 0:
        print('Error in Search: ' + str(ret))
        exit()
    if numFound.value < 1:
        print('No instruments found. Exiting script.')
        exit()
    elif numFound.value == 1:
        print('One device found.')
        print('Device type: {}'.format(deviceType.value))
        print('Device serial number: {}'.format(deviceSerial.value))
        ret = rsa.DEVICE_Connect(deviceIDs[0])
        if ret != 0:
            print('Error in Connect: ' + str(ret))
            exit()
    else:
        print('2 or more instruments found. Enumerating instruments, please wait.')
        for inst in range(numFound.value):
            rsa.DEVICE_Connect(deviceIDs[inst])
            rsa.DEVICE_GetSerialNumber(deviceSerial)
            rsa.DEVICE_GetNomenclature(deviceType)
            print('Device {}'.format(inst))
            print('Device Type: {}'.format(deviceType.value))
            print('Device serial number: {}'.format(deviceSerial.value))
            rsa.DEVICE_Disconnect()
        # note: the API can only currently access one at a time
        selection = 1024
        while (selection > numFound.value - 1) or (selection < 0):
            selection = int(input('Select device between 0 and {}\n> '.format(numFound.value - 1)))
        rsa.DEVICE_Connect(deviceIDs[selection])
        return selection

    # connect to the first RSA


def print_spectrum_settings(specSet):
    # print out spectrum settings for a sanity check
    print('Span: ' + str(specSet.span))
    print('RBW: ' + str(specSet.rbw))
    print('VBW Enabled: ' + str(specSet.enableVBW))
    print('VBW: ' + str(specSet.vbw))
    print('Trace Length: ' + str(specSet.traceLength))
    print('Window: ' + str(specSet.window))
    print('Vertical Unit: ' + str(specSet.verticalUnit))
    print('Actual Start Freq: ' + str(specSet.actualStartFreq))
    print('Actual End Freq: ' + str(specSet.actualStopFreq))
    print('Actual Freq Step Size: ' + str(specSet.actualFreqStepSize))
    print('Actual RBW: ' + str(specSet.actualRBW))
    print('Actual VBW: ' + str(specSet.actualVBW))


def main():
    """#################INITIALIZE VARIABLES#################"""
    # main SA parameters
    specSet = Spectrum_Settings()
    enable = c_bool(True)  # spectrum enable
    cf = c_double(866e6)  # center freq
    refLevel = c_double(0)  # ref level
    ready = c_bool(False)  # ready
    timeoutMsec = c_int(100)  # timeout
    acqTime = 10   # time to run script in seconds
    end = -1

    """#################SEARCH/CONNECT#################"""
    selection = search_connect()

    """#################CONFIGURE INSTRUMENT#################"""
    rsa.CONFIG_Preset()
    rsa.CONFIG_SetCenterFreq(cf)
    rsa.CONFIG_SetReferenceLevel(refLevel)
    rsa.SPECTRUM_SetEnable(enable)
    rsa.SPECTRUM_SetDefault()
    rsa.SPECTRUM_GetSettings(byref(specSet))
    # configure desired spectrum settings
    # some fields are left blank because the default
    # values set by SPECTRUM_SetDefault() are acceptable
    specSet.span = c_double(2e6)
    specSet.rbw = c_double(200)
    # specSet.enableVBW =
    # specSet.vbw =
    specSet.traceLength = c_int(801)
    # specSet.window =
    # specSet.verticalUnit =
    specSet.actualStartFreq = c_double(865e6)
    specSet.actualFreqStepSize = c_double(200e3)
    # specSet.actualRBW =
    # specSet.actualVBW =
    # specSet.actualNumIQSamples =

    # set desired spectrum settings
    rsa.SPECTRUM_SetSettings(specSet)
    rsa.SPECTRUM_GetSettings(byref(specSet))

    """#################INITIALIZE DATA TRANSFER VARIABLES#################"""
    # initialize variables for GetTrace
    traceArray = c_float * specSet.traceLength
    traceData = traceArray()
    outTracePoints = c_int()
    # generate frequency array for plotting the spectrum
    freq = np.arange(specSet.actualStartFreq,
                     specSet.actualStartFreq + specSet.actualFreqStepSize * specSet.traceLength,
                     specSet.actualFreqStepSize)

    """#################ACQUIRE/PROCESS DATA#################"""

    spectrums = 0
    rsa.DEVICE_Run()
    start = time.clock()
    book = xlwt.Workbook()                                          # Create Excel Workbook

    sheet = book.add_sheet('Sheet 1')                               # Create Sheet in above workbook
    m = 0
    data = []
    print('Calculating noise floor......')

    while end - start < 5:
        rsa.SPECTRUM_AcquireTrace()
        while not ready.value:
            rsa.SPECTRUM_WaitForDataReady(timeoutMsec, byref(ready))
        ready.value = False
        rsa.SPECTRUM_GetTrace(c_int(0), specSet.traceLength,
                              byref(traceData), byref(outTracePoints))
        spectrums += 1
        peakPower = np.amax(traceData)
        peakPowerFreq = freq[np.argmax(traceData)]
        print('Peak power in spectrum: %4.3f dBm @ %d Hz' %
              (peakPower, peakPowerFreq))
        data.append(peakPower)
        m += 1
        end = time.clock()
    global noise_Floor
    noise_Floor = max(set(data), key=data.count)
    print('Noise floor is: {} dBm'.format(noise_Floor))
    time.sleep(5)

    spectrums = 0
    powerData = np.zeros(10000)
    end = -1
    i = 1                                                           # Variable to increment rows
    k = 1
    start = time.clock()
    sheet.write(0, 0, 'Amplitude')
    sheet.write(0, 1, 'Frequency')

    while end - start < acqTime:

        rsa.SPECTRUM_AcquireTrace()
        while not ready.value:
            rsa.SPECTRUM_WaitForDataReady(timeoutMsec, byref(ready))
        ready.value = False
        rsa.SPECTRUM_GetTrace(c_int(0), specSet.traceLength,
                              byref(traceData), byref(outTracePoints))
        spectrums += 1

        peakPower = np.amax(traceData)
        peakPowerFreq = freq[np.argmax(traceData)]
        for j in range(0, len(traceData)-1):
            if traceData[j] > noise_Floor+40:
                powerData[j] = traceData[j]
                sheet.write(k, 0, str(powerData[j]))
                sheet.write(k, 1, str(freq[j]))
                k += 1
        print('Peak power in spectrum: %4.3f dBm @ %d Hz' %
              (peakPower, peakPowerFreq))

        i += 1                                                        # incrementing to move to next row

        end = time.clock()

    rsa.DEVICE_Stop()
    book.save('Data.xls')
    print('Disconnecting.')
    print('{} spectrums in {} seconds: {} spectrums per second.'.format(spectrums, acqTime, spectrums / acqTime))
    sps = float(acqTime) / spectrums
    print('Also {} seconds per trace.'.format(sps))

    return noise_Floor


if __name__ == '__main__':
    main()
