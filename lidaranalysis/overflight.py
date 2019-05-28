import numpy as np
import pandas as pd
import datetime as dt
import sys
from scipy import stats
from dateutil.relativedelta import relativedelta
from . import reg, loading


def ovavg(ovfile, loc, outDir, rawdir):
    """ This funcion finds LiDAR data at specific times inputted in a file. """
    print('-------------------------------------')
    print(ovfile)
    ovflight_times = pd.read_csv(ovfile, names=['time'], parse_dates=True, index_col=0)
    timedelta_2h = dt.timedelta(hours=2)
    timedelta_1100s = dt.timedelta(seconds=1100)
    for i in ovflight_times:
        if not isinstance(i, dt.date):
            print("""Incorrect Data Format:
                     Input must be vertical list of dates in standard format
                     so that pandas date parser can detect type. """)
            sys.exit(0)

    data_ov = ovflight_times
    for t in ovflight_times.index:
        t = t.to_pydatetime()
        print(t)
        # Load LiDAR Data
        datamark = True
        data = loading.load_raw(t, rawdir, loc)
        day_dt = (t - timedelta_2h)
        day = dt.datetime(day_dt.year, day_dt.month, day_dt.day)
        if (t - timedelta_2h).date() != t.date():  # If data will span current and previous day
            data_before = loading.load_raw(t - dt.timedelta(days=1), rawdir, loc)
            if data is None and data_before is None:
                print('No data for this overflight.')
                datamark = False
            else:
                data.index = data.index + 24 * 60 * 60
                data = pd.concat([data_before, data])

        elif (t + timedelta_2h).date() != t.date():  # if data will span current and next day
            data_after = loading.load_raw(t + dt.timedelta(days=1), rawdir, loc)
            if data is None and data_after is None:
                print('No LiDAR data for this overflight.')
                datamark = False
            else:
                data_after.index = data_after.index + 24 * 60 * 60
                data = pd.concat([data_before, data])

        elif data is None:
            print('No LiDAR data for this overflight.')
            datamark = False

        if datamark:
            # LiDAR Averaging for 2 hour quadratic
            t1 = ((t - timedelta_2h) - day).total_seconds()
            t2 = ((t + timedelta_2h) - day).total_seconds()
            ind = (data.index >= t1) & (data.index <= t2)
            r_range_2h = data['range'][ind]
            r_amp_2h = data['amp'][ind]
            time_2h = data.index[ind]
            std_int = np.std(r_range_2h)
            mean_int = np.mean(r_range_2h)
            ind_good = ((np.abs(r_range_2h - mean_int)) < (5 * std_int))
            r_range_2h = r_range_2h[ind_good]
            r_amp_2h = r_amp_2h[ind_good]
            time_2h = time_2h[ind_good]

            # LiDAR Averaging for 1100s
            t1 = ((t - timedelta_1100s) - day).total_seconds()
            t2 = ((t + timedelta_1100s) - day).total_seconds()
            ind = (data.index >= t1) & (data.index <= t2)
            r_range_1100 = data['range'][ind]
            r_amp_1100 = data['amp'][ind]
            time_1100 = data.index[ind]
            std_int = np.std(r_range_1100)
            mean_int = np.mean(r_range_1100)
            ind_good = ((np.abs(r_range_1100 - mean_int)) < (5 * std_int))
            r_range_1100 = r_range_1100[ind_good]
            r_amp_1100 = r_amp_1100[ind_good]
            time_1100 = time_1100[ind_good]

            l_r = len(r_range_1100)
            if l_r > 0:
                print('LiDAR Data Points (+-2h window): ', l_r)
                data_ov.loc[t, 'l_mean'] = np.mean(r_range_1100)
                data_ov.loc[t, 'l_median'] = np.median(r_range_1100)
                data_ov.loc[t, 'l_std'] = np.std(r_range_1100)
                data_ov.loc[t, 'l_skew'] = stats.skew(r_range_1100)
                data_ov.loc[t, 'l_n'] = l_r
                data_ov.loc[t, 'l_min'] = np.min(r_range_1100)
                data_ov.loc[t, 'l_max'] = np.max(r_range_1100)
                data_ov.loc[t, 'l_amp'] = np.mean(r_amp_1100)
                data_ov.loc[t, 'l_quad2h'] = reg.quadreg(time_2h, r_range_2h, t, day)
                data_ov.loc[t, 'l_lin1100s'] = reg.linreg(time_1100, r_range_1100, t, day)
            else:
                print('No LiDAR data for this overflight.')
            del r_range_2h, r_amp_2h

        # Bubbler and Radar Data
        filedata = loading.load_output(t, loc, outDir)
        if (t - timedelta_2h).month != t.month:  # If data will span current and previous month
            filedata2 = loading.load_output(t - relativedelta(months=1), loc, outDir)
            filedata = pd.concat([filedata, filedata2])

        elif (t + timedelta_2h).month != t.month:  # If data will span current and next month
            filedata2 = loading.load_output(t + relativedelta(months=1), loc, outDir)
            filedata = pd.concat([filedata, filedata2])

        if loc == 'harv':
            t1 = (t - timedelta_2h)
            t2 = (t + timedelta_2h)
            ind = (filedata.index >= t1) & (filedata.index <= t2)
            bub = filedata['N1_1'][ind].astype(float)
            rad = filedata['Y1_1'][ind].astype(float)
            lid = filedata['l_mean'][ind].astype(float)
            time = filedata.index[ind]

            std_bub = np.std(bub)
            std_rad = np.std(rad)
            std_lid = np.std(lid)
            mean_bub = np.mean(bub)
            mean_rad = np.mean(rad)
            mean_lid = np.mean(lid)
            ind_good_bub = ((np.abs(bub - mean_bub)) < (5 * std_bub))
            ind_good_rad = ((np.abs(rad - mean_rad)) < (5 * std_rad))
            ind_good_lid = ((np.abs(lid - mean_lid)) < (5 * std_lid))

            bub = bub[ind_good_bub]
            timebub = time[ind_good_bub]
            rad = rad[ind_good_rad]
            timerad = time[ind_good_rad]
            lid = lid[ind_good_lid]
            time_lid = time[ind_good_lid]

            l_r = len(rad)
            l_b = len(bub)
            l_l = len(lid)
            if l_b > 0:
                print('Bubbler Data Points (+-2h window): ', l_b)
                data_ov.loc[t, 'bub'] = reg.quadreg(timebub, bub, t, day)
            else:
                print('No Bubbler data for this overflight.')
            if l_r > 0:
                print('Radar Data Points (+-2h window): ', l_r)
                data_ov.loc[t, 'rad'] = reg.quadreg(timerad, rad, t, day)
            else:
                print('No Radar data for this overflight.')
            if l_l > 0:
                print('LiDAR 6 minute Data Points (+-2h window): ', l_l)
                data_ov.loc[t, 'l_6m_quad2h'] = reg.quadreg(time_lid, lid, t, day)
            else:
                print('No 6 minute LiDAR data for this overflight.')

        elif loc == 'cata':
            t1 = (t - timedelta_2h)
            t2 = (t + timedelta_2h)
            ind = (filedata.index >= t1) & (filedata.index <= t2)
            acoust = filedata['A1'][ind].astype(float)
            lid = filedata['l_mean'][ind].astype(float)
            time = filedata.index[ind]
            std_acoust = np.std(acoust)
            mean_acoust = np.mean(acoust)
            std_lid = np.std(lid)
            mean_lid = np.mean(lid)
            ind_good_acoust = ((np.abs(acoust - mean_acoust)) < (5 * std_acoust))
            ind_good_lid = ((np.abs(lid - mean_lid)) < (5 * std_lid))

            acoust = acoust[ind_good_acoust]
            time_acoust = time[ind_good_acoust]
            lid = lid[ind_good_lid]
            time_lid = time[ind_good_lid]
            l_a = len(acoust)
            l_l = len(lid)
            if l_a > 0:
                data_ov.loc[t, 'acoust'] = reg.quadreg(time_acoust, acoust, t, day)
                print('Acoustic Data Points (+-2h window): ', l_a)
            else:
                print('No Acoustic data for this overflight.')
            if l_l > 0:
                print('LiDAR 6 minute Data Points (+-2h window): ', l_l)
                data_ov.loc[t, 'l_6m_quad2h'] = reg.quadreg(time_lid, lid, t, day)
            else:
                print('No 6 minute LiDAR data for this overflight.')
        print('-------------------------------------')
    return data_ov
