import pandas as pd
import numpy as np
from statistics import mean


def some_func():
    # reading the data
    file = "Data.xls"
    data = pd.read_excel(file)
    val = []
    flag = 1
    # Assigning variables to columns of data sheet
    amp = data['Amplitude'].values
    freq = data['Frequency'].values
    print("\n")

    def mean_func(fq):
        amp_val = []
        global flag
        for i in range(0, len(freq)):
            if fq-12500.0 <= freq[i] <= fq+12500.0:
                flag = 1
                amp_val.append(amp[i])
            try:
                return mean(amp_val)
            except:
                pass
    # # checking the channel plan

    val.append([mean_func(865062500.0), 865062500.0])
    val.append([mean_func(865402500.0), 865402500.0])
    val.append([mean_func(865985000.0), 865985000.0])
    val.append([mean_func(865602500.0), 865602500.0])
    val.append([mean_func(866300000.0), 866300000.0])
    val.append([mean_func(866500000.0), 866500000.0])
    val.append([mean_func(866700000.0), 866700000.0])
    val.append([mean_func(865785000.0), 865785000.0])

    return flag, amp, val


if __name__ == '__main__':
    some_func()
