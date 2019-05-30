#!/usr/bin/env python3
############################################################################################################
# Author: Adam Dodge
# Date Created: 8/30/2017
# Date Modified: 5/23/2019
############################################################################################################
import datetime as dt
import os
from . import avg, combine, overflight, chng, plot
import sys
import argparse


def arg2dt(t):
    return dt.datetime.strptime(t, '%Y%m%d')


def main():
    """ Main function for loading each necessary day and saving files by month. """

    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', type=arg2dt, default=None, help='Start Date in YYYYMMDD format')
    parser.add_argument('-e', '--end', type=arg2dt, default=None, help='End Date in YYYYMMDD format')
    parser.add_argument('-l', '--location', type=str, default=None,
                        help="Location ('harv' or 'cata'). Required for all but plotting option.")
    parser.add_argument('-f', '--full', action="store_true", default=None,
                        help="Save all six minute data to single file (harv_all.csv or cata_all.csv)")
    parser.add_argument('-d', '--oneday', type=arg2dt, default=None, help="Single Date in YYYYMMDD format")
    parser.add_argument('-u', '--lastday', type=str, default=None,
                        help="Update last day run in file. Argument must be day in YYYYMMDD format")
    parser.add_argument('-c', '--coops', type=str, default=None,
                        help="Update last coops month run in file. Argument must be day in YYYYMM format")
    parser.add_argument('--out', type=str, default=None,
                        help="Change directory of output six minute data. Default is "
                             "/srv/data/harvest/[harv or cata]/six_minute")
    parser.add_argument('-p', '--plot', action="store_true", default=None,
                        help="Save Plots of data to /srv/data/harvest/plots. "
                             "Location does not matter; it will plot both.")

    args = parser.parse_args()
    if (not bool(args.plot)) and (not bool(args.location)):
        parser.error('"location" is required unless plotting. ')

    loc = args.location

    # Define directories
    datafile = os.getenv('LIDARDATAFILE', os.path.join('/', 'srv', 'data', 'harvest'))
    if loc is not None:
        rawdir = os.path.join(datafile, loc, 'uls')
        coopsdir = os.path.join(datafile, loc, 'co-ops')
        if args.out is None:
            outdir = os.path.join(datafile, loc, 'six_minute')
        else:
            outdir = args.out
        req_filedir = os.path.join(datafile, 'lidar_analysis_files')
    if args.plot is True:
        plot_dir = os.path.join(datafile, 'plots')

    # Initialize
    write_day = True
    data_yest = None

    # If plotting option is called
    if args.plot is True:
        datadir_harv = os.path.join(datafile, 'harv', 'six_minute')
        datadir_cata = os.path.join(datafile, 'cata', 'six_minute')
        # Find Date
        td = dt.datetime.utcnow()
        td = td - dt.timedelta(days=1, hours=td.hour,
                               minutes=td.minute, seconds=td.second, microseconds=td.microsecond)
        data_h = plot.load_harv(datadir_harv)
        data_c = plot.load_cata(datadir_cata)
        plot.plot_harv(td, data_h, plot_dir)
        plot.plot_cata(td, data_c, plot_dir)
        plot.plot_corr(data_h, data_c, plot_dir)
        sys.exit(0)

    # If change last day option is called
    if args.lastday is not None:
        try:
            tmp = dt.datetime(int(args.lastday[0:4]), int(args.lastday[4:6]), int(args.lastday[6:8]))
            assert (len(args.lastday) == 8)
        except:
            print('Input to new last day must be a working date.')
            sys.exit(0)
        chng.chng_day(args.lastday, loc, req_filedir)
        sys.exit(0)

    # If change coops month option is called
    if args.coops is not None:
        try:
            tmp = dt.datetime(int(args.coops[0:4]), int(args.coops[4:6]), 1)
            assert (len(args.coops) == 6)
        except:
            print('Input to new coops month must be a working month.')
            sys.exit(0)
        chng.chng_coops(args.coops, loc, req_filedir)
        sys.exit(0)

    # If only one day is being run
    if args.oneday is not None:
        # Create class for averaging day
        today_class = avg.LidarData(args.oneday, loc, rawdir, outdir, coopsdir, data_yest, req_filedir)
        if today_class.mark:  # if there is data
            today_class.data.to_csv(os.path.join(outdir, str(loc) + '_%s.csv' % args.oneday.strftime('%Y%m')),
                                   na_rep='NaN')  # write to file
            print('Writing Data to:', os.path.join(outdir, str(loc) + '_%s.csv' % args.oneday.strftime('%Y%m')))
        print('-------------------------------------')
        if args.full:  # Combine entire dataset into one file
            combine.combinedata(loc, outdir, req_filedir)
        sys.exit(0)

    # If start and end are specified, don't write day to last day file
    if args.start is not None and args.end is not None:
        write_day = False

    # No start date, find the last day that was ran in the file to start at
    curr_day = args.start
    if curr_day is None:
        with open(os.path.join(req_filedir, 'lastday_' + str(loc) + '.txt'), 'r') as f:
            start = f.read()
        print('Reading Date from:', 'lastday_' + str(loc) + '.txt')
        # first day to run
        curr_day = dt.datetime(int(start[0:4]), int(start[4:6]), int(start[6:8])) + dt.timedelta(days=1)
    print('Start Date:', curr_day)

    # If no end date, go until yesterday
    last_day = args.end
    if last_day is None:
        tmp = dt.datetime.today()
        last_day = dt.datetime(tmp.year, tmp.month, tmp.day) - dt.timedelta(days=1)  # final day to run
    print('End Date:', last_day)

    # If data is up to date
    if last_day < curr_day:
        print('Data is up to date. ')
        if args.full is True:
            combine.combinedata(loc, outdir, req_filedir)
        sys.exit(0)

    # Run loop over all days requested
    while last_day >= curr_day:  # while current running day is before the final day
        dayClass = avg.LidarData(curr_day, loc, rawdir, outdir, coopsdir, data_yest, req_filedir)
        if dayClass.mark is True:  # if there is data
            dayClass.data.to_csv(os.path.join(outdir, str(loc) + '_%s.csv' % curr_day.strftime('%Y%m')),
                                 na_rep='NaN')  # write to file
            print('Writing Data to:', os.path.join(outdir, str(loc) + '_%s.csv' % curr_day.strftime('%Y%m')))
            if write_day:
                file2 = open(os.path.join(req_filedir, 'lastday_' + str(loc) + '.txt'), 'w')
                file2.write(curr_day.strftime('%Y%m%d'))  # write last day run
                print('Writing Final Date to:', 'lastday_' + str(loc) + '.txt')
                file2.close()
            data_yest = dayClass.data_today
        curr_day = curr_day + dt.timedelta(days=1)  # move to next day
    print('-------------------------------------')

    # Add all new coops data to file
    dayClass.coops(last_day.strftime('%Y%m'))

    # If called, combine all data into one file
    if args.full:
        combine.combinedata(loc, outdir, req_filedir)
