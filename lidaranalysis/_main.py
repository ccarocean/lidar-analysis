#!/usr/bin/env python3
############################################################################################################
# Author: Adam Dodge
# Date Created: 8/30/2017
# Date Modified: 5/23/2019
############################################################################################################
import datetime as dt
import os
from . import avg, combine, overflight, chng
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
    parser.add_argument('-o', '--ovfile', type=str, default=None, help="File with overflight times.")
    parser.add_argument('location', type=str, help="Location ('harv' or 'cata')")
    parser.add_argument('-f', '--full', action="store_true", default=None, help="Save full six minute dataset to file")
    parser.add_argument('-d', '--oneday', type=arg2dt, default=None, help="Single Date in YYYYMMDD format")
    parser.add_argument('-l', '--lastday', type=str, default=None, help="Change last day run. Argument must be day in YYYYMMDD format")
    parser.add_argument('-c', '--coops', type=str, default=None, help="Change last coops month run. Argument must be day in YYYYMM format")
    parser.add_argument('--out', type=str, default=None, help="Change directory of output six minute data")

    args = parser.parse_args()
    loc = args.location

    # Define directories
    dataFile = os.getenv('LIDARDATAFILE', os.path.join('/', 'srv', 'data', 'harvest'))
    rawDir = os.path.join(dataFile, loc,  'uls')
    coopsDir = os.path.join(dataFile, loc, 'co-ops')
    if args.out is None:
        outDir = os.path.join(dataFile, loc, 'six_minute')
    else:
        outDir = args.out
    req_fileDir = 'lidar_analysis_files'
    ov_outfile = os.path.join(dataFile, loc, 'lidardata_overflights.csv')

    # Initialize
    writeDay = True
    dataYest = None

    # If required files don't exist, write the first possible day/month to them so that the program
    #       will run all data
    if not os.path.isdir(req_fileDir):
        print("Writing required files. ")
        os.mkdir(req_fileDir)
        with open(os.path.join(req_fileDir, 'bias_cata.txt')) as f:
            f.write('0')
        with open(os.path.join(req_fileDir, 'bias_harv.txt')) as f:
            f.write('0')
        with open(os.path.join(req_fileDir, 'lastcoopsmonth_cata.txt')) as f:
            f.write('201705')
        with open(os.path.join(req_fileDir, 'lastcoopsmonth_harv.txt')) as f:
            f.write('201603')
        with open(os.path.join(req_fileDir, 'lastday_cata.txt')) as f:
            f.write('20170603')
        with open(os.path.join(req_fileDir, 'lastday_harv.txt')) as f:
            f.write('20160425')

    # If change last day option is called
    if args.lastday is not None:
        try:
            tmp = dt.datetime(int(args.lastday[0:4]), int(args.lastday[4:6]), int(args.lastday[6:8]))
            assert(len(args.lastday) == 8)
        except:
            print('Input to new last day must be a working date.')
            sys.exit(0)
        chng.chng_day(args.lastday, loc, req_fileDir)
        sys.exit(0)

    # If change coops month option is called
    if args.coops is not None:
        try:
            tmp = dt.datetime(int(args.coops[0:4]), int(args.coops[4:6]), 1)
            assert (len(args.coops) == 6)
        except:
            print('Input to new coops month must be a working month.')
            sys.exit(0)
        chng.chng_coops(args.coops, loc, req_fileDir)
        sys.exit(0)

    # If overflight averaging is required
    if args.ovfile is not None:
        print('Reading Overflight Data from:', args.ovfile)
        # Call overflight averaging function
        ovdata = overflight.ovavg(args.ovfile, loc, outDir, rawDir)
        ovdata.to_csv(ov_outfile, na_rep='NaN')
        print('Writing Overflight Data to:', ov_outfile)
        print('-------------------------------------')
        sys.exit(0)

    # If only one day is being run
    if args.oneday is not None:
        # Create class for averaging day
        todayClass = avg.lidarData(args.oneday, loc, rawDir, outDir, coopsDir, dataYest)
        if todayClass.mark:  # if there is data
            todayClass.data.to_csv(os.path.join(outDir, str(loc) + '_%s.csv' % args.oneday.strftime('%Y%m')),
                                   na_rep='NaN')  # write to file
            print('Writing Data to:', os.path.join(outDir, str(loc) + '_%s.csv' % args.oneday.strftime('%Y%m')))
        print('-------------------------------------')
        if args.full:  # Combine entire dataset into one file
            combine.combinedata(loc, outDir)
        sys.exit(0)

    # If start and end are specified, don't write day to last day file
    if args.start is not None and args.end is not None:
        writeDay = False

    # No start date, find the last day that was ran in the file to start at
    currDay = args.start
    if currDay is None:
        with open(os.path.join(req_fileDir, 'lastday_' + str(loc) + '.txt'), 'r') as f:
            start = f.read()
        print('Reading Date from:', 'lastday_' + str(loc) + '.txt')
        # first day to run
        currDay = dt.datetime(int(start[0:4]), int(start[4:6]), int(start[6:8])) + dt.timedelta(days=1)
    print('Start Date:', currDay)

    # If no end date, go until yesterday
    lastDay = args.end
    if lastDay is None:
        tmp = dt.datetime.today()
        lastDay = dt.datetime(tmp.year, tmp.month, tmp.day) - dt.timedelta(days=1)  # final day to run
    print('End Date:', lastDay)

    # If data is up to date
    if lastDay < currDay:
        print('Data is up to date. ')
        if args.full is True:
            combine.combinedata(loc, outDir)
        sys.exit(0)

    # Run loop over all days requested
    while lastDay >= currDay:  # while current running day is before the final day
        dayClass = avg.lidarData(currDay, loc, rawDir, outDir, coopsDir, dataYest)
        if dayClass.mark is True:  # if there is data
            dayClass.data.to_csv(os.path.join(outDir, str(loc) + '_%s.csv' % currDay.strftime('%Y%m')),
                                 na_rep='NaN')  # write to file
            print('Writing Data to:', os.path.join(outDir, str(loc) + '_%s.csv' % currDay.strftime('%Y%m')))
            if writeDay:
                file2 = open(os.path.join(req_fileDir, 'lastday_' + str(loc) + '.txt'), 'w')
                file2.write(currDay.strftime('%Y%m%d'))  # write last day run
                print('Writing Final Date to:', 'lastday_' + str(loc) + '.txt')
                file2.close()
            dataYest = dayClass.data_today
        currDay = currDay + dt.timedelta(days=1)  # move to next day
    print('-------------------------------------')

    # Add all new coops data to file
    dayClass.coops(lastDay.strftime('%Y%m'))

    # If called, combine all data into one file
    if args.full:
        combine.combinedata(loc, outDir)
