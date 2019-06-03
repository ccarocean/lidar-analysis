import gzip, lzma, os, sys
import numpy as np
import pandas as pd


############## Functions for Loading Data ############################################################
def load_raw(d, rawdir):
    """ Function to determine filetype and load raw LiDAR data. """
    fgzbin = d.strftime(rawdir + '/uls_%Y%m%d.bin.gz')
    fxzbin = d.strftime(rawdir + '/uls_%Y%m%d.bin.xz')
    dtype = np.dtype([(str('time'), np.uint32), (str('range'), np.uint32), (str('rpw'), np.uint32)])
    if os.path.isfile(fgzbin):
        return load_gzbin(fgzbin, dtype)
    elif os.path.isfile(fxzbin):
        return load_xzbin(fxzbin, dtype)
    else:
        return None


def load_gzbin(f, dtype):
    """ Function to load binary data file from LIDAR sensor using gz compression. """
    if os.path.isfile(f):  # Ensures file exists
        with gzip.open(f, 'rb') as nf:  # Open file
            try:
                file_content = nf.read()  # Read file
            except EOFError:
                print('File is still being transfered from LiDAR Station.')
                sys.exit(0)
        filesize = len(file_content)
        data = np.frombuffer(file_content, dtype, count=filesize // 12)  # returns data from file
        data = {'time': data['time'].astype(float) / 10000, 'range': data['range'].astype(float) / 1000,
                'rpw': data['rpw']}  # data organization
        data = pd.DataFrame.from_dict(data)  # creates dataframe
        data.set_index('time', inplace=True, drop=True)  # sets index as time
        print('LiDAR Data loaded from:', f[-19:])
        return data
    else:
        return None


def load_xzbin(f, dtype):
    """ Function to load binary data file from LIDAR sensor using xz compression. """
    if os.path.isfile(f):  # Ensures file exists
        with lzma.open(f, 'rb') as nf:  # Open file
            try:
                file_content = nf.read()  # Read file
            except EOFError:
                print('File is still being transfered from LiDAR Station.')
                sys.exit(0)
        filesize = len(file_content)
        data = np.frombuffer(file_content, dtype, count=filesize // 12)  # returns data from file
        data = {'time': data['time'].astype(float) / 10000, 'range': data['range'].astype(float) / 1000,
                'rpw': data['rpw']}  # data organization
        data = pd.DataFrame.from_dict(data)  # creates dataframe
        data.set_index('time', inplace=True, drop=True)  # sets index as time
        print('LiDAR Data loaded from:', f[-19:])
        return data
    else:
        return None


# def load_dat(f, rawdir):
#     """ Function to load .dat file from LIDAR sensor. """
#     if os.path.isfile(f):  # ensures file exists
#         data = pd.read_csv(f, names=['time', 'range', 'rpw'], parse_dates=True, index_col=0, error_bad_lines=False)
#         day = dt.datetime.strptime(f, rawdir + '/uls_%Y%m%d.dat.gz')  # gets day from filename
#         data.index = [(i-day).total_seconds() for i in data.index]
#         print('LiDAR Data loaded from:', f[-19:])
#         return data
#     else:
#         return None


def load_output(d, loc, outdir):
    """ Function to load output data. """
    names_cata_saved = ['time', 'A1', 'A1_t1', 'A1_t2', 'B1', 'E1', 'F1', 'L1_1', 'L1_2', 'P6', 'U1',
                        'W1', 'l', 'l_Hs', 'l_rpw', 'l_max', 'l_mean', 'l_median', 'l_min', 'l_n', 'l_skew', 'l_std']
    names_harv_saved = ['time', 'D1', 'F1', 'L1_1', 'L1_2', 'N1_1', 'N1_1_ssh', 'N1_2', 'P6', 'U1', 'W1',
                        'Y1_1', 'Y1_1_ssh', 'Y1_2', 'l', 'l_Hs', 'l_rpw', 'l_max', 'l_mean', 'l_median', 'l_min',
                        'l_n', 'l_skew', 'l_ssh', 'l_std']
    f = os.path.join(outdir, loc + '_' + d.strftime('%Y%m') + '.csv')
    if loc == 'harv':
        try:
            filedata = pd.read_csv(f, header=0, usecols=range(0, 25), names=names_harv_saved, parse_dates=True,
                                   index_col=0, na_values='   -   ')
            return filedata
        except IOError:
            data = pd.DataFrame(columns=names_harv_saved)
            data.set_index('time', inplace=True, drop=True)
            return data
    else:
        try:
            filedata = pd.read_csv(f, header=0, usecols=range(0, 22), names=names_cata_saved, parse_dates=True,
                                   index_col=0, na_values='   -   ')
            return filedata
        except IOError:
            data = pd.DataFrame(columns=names_cata_saved)
            data.set_index('time', inplace=True, drop=True)
            return data


def load_coops(d, loc, coopsdir):
    """ Function to load coops data from file. """
    names_harv_coops = ['time', 'D1', 'F1', 'L1_1', 'L1_2', 'N1_1', 'N1_2', 'U1', 'Y1_1', 'Y1_2', 'P6', 'W1']
    names_cata_coops = ['time', 'A1', 'A1_t1', 'A1_t2', 'B1', 'E1', 'F1', 'L1_1', 'L1_2', 'U1', 'P6', 'W1']
    month = d.strftime('%Y%m')
    f = os.path.join(coopsdir, loc + '_' + str(month) + '.csv')
    if loc == 'harv':
        try:
            coops = pd.read_csv(f, header=0, usecols=range(0, 12), names=names_harv_coops,
                                parse_dates=True, index_col=0, na_values='   -   ')  # Read coops data
            print('Co-ops data loaded from:', f)
            return coops
        except IOError:
            return None
    else:
        try:
            coops = pd.read_csv(f, header=0, usecols=range(0, 12), names=names_cata_coops,
                                parse_dates=True, index_col=0, na_values='   -   ')  # Read coops data
            print('Co-ops data loaded from:', f)
            return coops
        except IOError:
            return None
