#!/usr/bin/env python3
############################################################################################################
# Author: Adam Dodge
# Date Created: 8/30/2017
# Date Modified: 5/23/2019
############################################################################################################
import numpy as np
import pandas as pd
from scipy import stats
import datetime as dt
import os, sys
from dateutil.relativedelta import relativedelta
from . import loading

############################################################################################################
class LidarData:
    """ This is a class for loading and analyzing lidar data from a single day. """

    def __init__(self, date, loc, rawdir, outdir, coopsDir, dataYest, req_fileDir):
        self.date = dt.datetime.strftime(date, '%Y%m%d')
        self.td = date  # self.date in datetime
        self.yd = self.td - dt.timedelta(days=1)
        self.loc = loc  # Location - catalina ('cata') or harvest ('harv')
        self.rawDir = rawdir  # Directory with raw lidar data
        self.outDir = outdir  # Directory of output averaged data
        self.req_fileDir = req_fileDir
        self.coopsDir = coopsDir  # Directory containing coops data
        self.dataYest = dataYest  # Data from previous day, if already loaded
        self.mark = True  # Mark for whether or not to write data
        self.main()  # Call averaging

    def main(self):
        """ Function for creating filenames and calling loading and averaging functions. """

        data = loading.load_output(self.td, self.loc, self.outDir)
        
        print('-------------------------------------')
        print('Date:            ', self.td)
        if self.dataYest is None:
            raw1 = loading.load_raw(self.yd, self.rawDir)
            if raw1 is None:
                raw1 = pd.DataFrame()
        else:
            raw1 = self.dataYest
            raw1.index = raw1.index - 24*60*60
        raw2 = loading.load_raw(self.td, self.rawDir)
        if raw2 is None:
            print('Data file does not exist.')
            self.mark = False  # if there is no data file do not write anything
            self.data_today = None
        else:
            raw2.index = raw2.index + 24*60*60
        if self.mark:
            raw = pd.concat([raw1, raw2])  # combine previous and current days
            del raw1, raw2
            print('Data Points:     ', len(raw['range']), '\n')
            ind = (data.index >= (self.td)) & (data.index < (self.td + dt.timedelta(days=1)))  # indicies of current day
            self.data = self.sixminavg(raw, data, ind)  # call averaging function
            ind = raw.index > 24*60*60
            self.data_today = raw[ind]

    def sixminavg(self, raw, data, ind):
        """ Averaging and Data Merging Function. """
        if data.index[ind].empty:  # if today does not exist in the csv file
            data = self.createFile(data)
            timedelt = dt.timedelta(days=1)
            ind = (data.index >= self.td) & (data.index < (self.td + timedelt))  # indicies of todays data

        for t in data.index[ind]:  # for all of todays data
            timedelt = dt.timedelta(minutes=3)
            t1 = ((t - timedelt) - self.yd).total_seconds()
            t2 = ((t + timedelt) - self.yd).total_seconds()
            
            # indices of the raw data in a 6 minute interval around each final data point
            ind2 = (raw.index >= t1) & (raw.index <= t2)
            r_range = raw['range'][ind2]  # range in interval
            r_rpw = raw['rpw'][ind2]  # received pulse width in interval

            if self.loc == 'cata':
                m = np.median(r_range)
                mad = 1.4826 * np.median(np.absolute(np.array([i - m for i in r_range])))
                ind_good = np.where((r_range > (m - 6 * mad)) & (r_range < (m + 6 * mad)))[0]
            else:
                std_int = np.std(r_range)  # find overall standard deviation
                mean_int = np.mean(r_range)  # find overall mean
                ind_good = ((np.abs(r_range - mean_int)) < (5 * std_int))
            r_range = r_range[ind_good]
            r_rpw = r_rpw[ind_good]
            
            try:
                file = open(os.path.join(self.req_fileDir, 'bias_' + str(self.loc) + '.txt'), 'r')
            except IOError:
                print('bias_' + str(self.loc) + '.txt is required. ')
                sys.exit(0)
            bias = file.read()
            bias = float(bias)
            file.close()

            l_r = len(r_range)
            if l_r > 0:  # if there is data, add to line in finalized data
                data.loc[t, 'l_mean'] = np.mean(r_range)
                data.loc[t, 'l_median'] = np.median(r_range)
                data.loc[t, 'l_std'] = np.std(r_range)
                data.loc[t, 'l_skew'] = stats.skew(r_range)
                data.loc[t, 'l_n'] = l_r
                data.loc[t, 'l_min'] = np.min(r_range)
                data.loc[t, 'l_max'] = np.max(r_range)
                data.loc[t, 'l_rpw'] = np.mean(r_rpw)
                data.loc[t, 'l_Hs'] = 4 * data.loc[t, 'l_std']
                data.loc[t, 'l'] = -data.loc[t, 'l_mean'] + bias
                if self.loc == 'harv':
                    data.loc[t, 'l_ssh'] = 20.150 - data.loc[t, 'l'] - 0.05
                    data.loc[t, 'N1_1_ssh'] = data.loc[t, 'N1_1'] - 0.05
                    data.loc[t, 'Y1_1_ssh'] = 20.150 - data.loc[t, 'Y1_1'] - 0.05
        return data

    def createFile(self, data):
        """ Function for creating output averaging DataFrame for data to be saved in. """
        names_cata_saved = ['time', 'A1', 'A1_t1', 'A1_t2', 'B1', 'E1', 'F1', 'L1_1', 'L1_2', 'P6', 'U1',
                            'W1', 'l', 'l_Hs', 'l_rpw', 'l_max', 'l_mean', 'l_median', 'l_min', 'l_n', 'l_skew',
                            'l_std']
        names_harv_saved = ['time', 'D1', 'F1', 'L1_1', 'L1_2', 'N1_1', 'N1_1_ssh', 'N1_2', 'P6', 'U1', 'W1',
                            'Y1_1', 'Y1_1_ssh', 'Y1_2', 'l', 'l_Hs', 'l_rpw', 'l_max', 'l_mean', 'l_median', 'l_min',
                            'l_n', 'l_skew', 'l_ssh', 'l_std']
        timevec = []
        if self.loc == 'harv':
            data_new = pd.DataFrame(columns=names_harv_saved)  # create DataFrame
        if self.loc == 'cata':
            data_new = pd.DataFrame(columns=names_cata_saved)  # create DataFrame
        if data.index.empty:  # if the csv file does not exist yet
            temp = self.td  # start with the beginning of the current date being run
            while temp < (self.td + dt.timedelta(days=1)):  # create lines every 6 minutes
                timevec.append(temp)
                temp = temp + dt.timedelta(minutes=6)
            data_new.loc[:, 'time'] = timevec  # put time in dataframe
            data_new.set_index('time', inplace=True)  # set time as index
            data = pd.concat([data, data_new],
                             sort=True)  # combine new dataframe with existing dataframe of final data from csv
        elif self.td > data.index[-1]:  # if the final index of the csv file is before today
            temp = data.index[-1] + dt.timedelta(minutes=6)  # start with the final index
            while temp < (self.td + dt.timedelta(days=1)):  # create lines every 6 minutes
                timevec.append(temp)
                temp = temp + dt.timedelta(minutes=6)
            data_new.loc[:, 'time'] = timevec  # put time in dataframe
            data_new.set_index('time', inplace=True)  # set time as index
            data = pd.concat([data, data_new],
                             sort=True)  # combine new dataframe with existing dataframe of final data from csv
        elif self.td < data.index[0]:  # if today is before the first index of the csv
            temp = self.td  # start with the beginning of today
            while (temp < data.index[0]):  # create lines every 6 minutes
                timevec.append(temp)
                temp = temp + dt.timedelta(minutes=6)
            data_new.loc[:, 'time'] = timevec  # put time in dataframe
            data_new.set_index('time', inplace=True)  # set time as index
            data = pd.concat([data_new, data],
                             sort=True)  # combine new dataframe with existing dataframe of final data from csv
        return data

    def addcoops(self, d):
        """ Function for adding co-ops data to output files """
        print(d.strftime('%Y'))
        coops = loading.load_coops(d, self.loc, self.coopsDir)
        data = loading.load_output(d, self.loc, self.outDir)
        f_data = os.path.join(self.outDir, self.loc + '_' + d.strftime('%Y%m') + '.csv')
        if coops is None:
            return None
        if self.loc == 'harv':
            # COMBINE
            data.loc[:, 'D1'] = coops['D1']
            data.loc[:, 'F1'] = coops['F1']
            data.loc[:, 'L1_1'] = coops['L1_1']
            data.loc[:, 'L1_2'] = coops['L1_2']
            data.loc[:, 'N1_1'] = coops['N1_1']
            data.loc[:, 'N1_2'] = coops['N1_2']
            data.loc[:, 'U1'] = coops['U1']
            data.loc[:, 'Y1_1'] = coops['Y1_1']
            data.loc[:, 'Y1_2'] = coops['Y1_2']
            data.loc[:, 'P6'] = coops['P6']
            data.loc[:, 'W1'] = coops['W1']
        if self.loc == 'cata':
            # COMBINE
            data.loc[:, 'A1'] = coops['A1']
            data.loc[:, 'A1_t1'] = coops['A1_t1']
            data.loc[:, 'A1_t2'] = coops['A1_t2']
            data.loc[:, 'B1'] = coops['B1']
            data.loc[:, 'E1'] = coops['E1']
            data.loc[:, 'F1'] = coops['F1']
            data.loc[:, 'L1_1'] = coops['L1_1']
            data.loc[:, 'L1_2'] = coops['L1_2']
            data.loc[:, 'U1'] = coops['U1']
            data.loc[:, 'P6'] = coops['P6']
            data.loc[:, 'W1'] = coops['W1']
        data.to_csv(f_data, na_rep='NaN')  # write to file
        print('Writing output data to:', f_data[-15:])
        print('Co-Ops Data Updated for ', str(d.month) + '/' + str(d.year))
        print('-------------------------------------')
        return True

    def coops(self, tm):
        """ Function for looping through months of co-ops data files """
        tm = str(tm)  # final day being loaded
        try:
            file = open(os.path.join(self.req_fileDir, 'lastcoopsmonth_' + str(self.loc) + '.txt'),
                        'r')
        except IOError:
            print('lastcoopsmonth_' + str(self.loc) + '.txt is required. ')
            sys.exit(0)
        lm = str(file.read())  # Read last coops month updated
        file.close()
        lm_dt = dt.datetime(int(lm[0:4]), int(lm[4:6]), 1)
        lm_dt = lm_dt + dt.timedelta(days=32)
        lm_dt = dt.datetime(lm_dt.year, lm_dt.month, 1)
        tm_dt = dt.datetime(int(tm[0:4]), int(tm[4:6]), 1)
        while lm_dt < tm_dt:  # while current month is before final month
            a = self.addcoops(lm_dt)
            if a is None:
                break
            lm_dt = lm_dt + relativedelta(months=1)
        file = open(os.path.join(self.req_fileDir, 'lastcoopsmonth_' + str(self.loc) + '.txt'), 'w')
        file.write((lm_dt - relativedelta(months=1)).strftime('%Y%m'))
        file.close()