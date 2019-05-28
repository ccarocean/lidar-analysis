import os
import pandas as pd
import datetime as dt
from . import loading

#################### Combine Data ##########################################################################
def combinedata(loc, outDir):
    """ Function for combining all LiDAR data into one csv file """
    print('Combining All Data:')
    fileDir = os.path.dirname(os.path.realpath('__file__'))
    data = pd.DataFrame()
    for root, dirs, files in os.walk(outDir):
        files.sort()
        for f in files:
            if f.startswith(loc + '_2'):
                d = dt.datetime.strptime(f, loc + '_%Y%m.csv')
                data = pd.concat([data, loading.load_output(d, loc, outDir)])

    if loc == 'harv':
        bias = (data['l_mean'] - data['N1_1']).mean()
    if loc == 'cata':
        bias = (data['l_mean'] - data['A1']).mean()

    file = open(os.path.join(fileDir, 'lidar_analysis_files', 'bias_' + str(loc) + '.txt'), 'w')
    file.write(str(bias))
    file.close()
    print('Bias = ' + str(bias) + ' m' + ', Written to bias_' + str(loc) + '.txt')

    data.to_csv(os.path.join(outDir, loc + '_all.csv'), na_rep='NaN')
    print('Writing Data to:', str(loc) + '_all.csv')
    print('-------------------------------------')
