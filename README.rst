LiDAR Analysis
==============

Title: lidar-analysis

Options
-------

positional arguments:
  location              Location ('harv' or 'cata')

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        Start Date in YYYYMMDD format
  -e END, --end END     End Date in YYYYMMDD format
  -o OVFILE, --ovfile OVFILE
                        File with overflight times.
  -f, --full            Save all six minute data to single file (harv_all.csv
                        or cata_all.csv)
  -d ONEDAY, --oneday ONEDAY
                        Single Date in YYYYMMDD format
  -l LAST_DAY, --lastday LASTDAY
                        Update last day run in file. Argument must be day in
                        YYYYMMDD format
  -c COOPS, --coops COOPS
                        Update last coops month run in file. Argument must be
                        day in YYYYMM format
  --out OUT             Change directory of output six minute data. Default is
                        /srv/data/harvest/[harv or cata]/six_minute
Notes:
   - INPUT DATES MUST BE IN NUMERIC YYYYMMDD FORMAT
   - OVERFLIGHT DATES MUST BE ABLE TO BE READ BY PANDAS DATE PARSER
   - Final Data is stored in harv_YYYYMM.csv and cata_YYYYMM.csv.

How to run
----------
Running Ranges of dates:
    If only start date is specified, the function is run from this start
    date through yesterday, and yesterdays date is written to
    "lastday_harv.txt"or "lastday_cata.txt" depending on the location
    chosen. If only the end date is specified, the initial date is read
    from one of these files and the function is run through the end
    date which is written to this file. If neither is specified, the function
    is run from the date in the file until yesterday, and yesterdays date
    is written to the file. If both are specified, the range is run and
    the file with the last run date ("lastday_harv.txt"/"lastday_cata.txt")
    is not read or written.

Running single dates:
    If a single date is specified (-d), the file ("lastday_harv.txt" or
    "lastday_cata.txt") is not read or written. Only the single date is run.

Running Overflight times:
    If the overflight time file is specified, The function will be run for
    each date/time in ovfile. It will average a 6-minute window around the
    overflight to give an accurate reading.

Creating Full dataset:
    If -f is specified, all of the available final data files
    (data/harv_YYYYMM.csv or data/cata_YYYYMM.csv) are combined into one
    (data/harv_all.csv or data/cata_all.csv).
    This can be run with any other option.

Related Files
-------------

raw data in $LIDARDATAFILE **OR** /srv/data/harvest/**loc**/uls/

bias_harv.txt or bias_cata.txt in ./lidar_analysis_files

lastcoopsmonth_harv.txt or lastcoopsmonth_cata.txt in ./lidar_analysis_files

lastday_harv.txt or lastday_cata.txt in ./lidar_analysis_files

Final data in data/harv_YYYYMM.csv
  - time                Date and Time of Measurement
  - D1       (Deg C)    Air temperature
  - F1_1     (mbars)    Air pressure
  - L1_1     (Voltage)  DCP1 voltage
  - L1_2     (Voltage)  DCP2 voltage
  - N1_1     (Meters)   Bubbler 1 water level
  - N1_2     (Meters)   Bubbler 2 water level
  - U1       (Meters)   Bubbler Tsunami Water Level
  - Y1_1     (Meters)   Radar 1 water level
  - Y1_2     (Meters)   Radar 2 water level
  - P6       (Meters)   Predicted water level
  - W1       (Meters)   Verified water level (usually the same as Bubbler 1, except with a 5-cm correction)
  - l_mean   (Meters)   Mean LiDAR Range Measurement
  - l_median (Meters)   Median of LiDAR Range Measurement
  - l_std    (Meters)   Standard Deviation of LiDAR Range Measurement
  - l_skew   (Meters)   Skew of LiDAR Range Measurement
  - l_n      (No Units) Number of LiDAR points in 6 minute window
  - l_min    (Meters)   Minimum LiDAR measurement in 6 minute window
  - l_max    (Meters)   Maximum LiDAR measurement in 6 minute window
  - l_amp    (Photons)  Mean LiDAR amplitude meas. in 6 minute window
  - l_Hs     (Meters)   LiDAR Significant Wave Height (4*STD)
  - l        (Meters)   LiDAR measurement minus bias with Bubbler
  - l_ssh    (Meters)   20.150 - l - 0.05
  - N1_1_ssh (Meters)   20.150 - N1_1 - 0.05
  - Y1_1_ssh (Meters)   20.150 - Y1_1 - 0.05

Final data in data/cata_YYYYMM.csv
  - time                Date and Time of Measurement
  - A1       (Meters)   Acoustic Water Level Measurement
  - B1       (Meters)   Water Level Measurement (Acoustic 2?)
  - A1_t1    (Deg C)    Air Thermistor Number 1
  - A1_t2    (Deg C)    Air Thermistor Number 2
  - E1       (Deg C)    Temperature Measurement
  - F1       (mbars)    Air Pressure
  - L1_1     (Voltage)  DCP1 voltage
  - L1_2     (Voltage)  DCP2 voltage
  - U1       (Meters)   Acoustic Tsunami Water Level
  - P6       (Meters)   Predicted water level
  - W1       (Meters)   Verified water level (usually the same as Acoustic 1, except with a 5-cm correction)
  - l_mean   (Meters)   Mean LiDAR Range Measurement
  - l_median (Meters)   Median of LiDAR Range Measurement
  - l_std    (Meters)   Standard Deviation of LiDAR Range Measurement
  - l_skew   (Meters)   Skew of LiDAR Range Measurement
  - l_n      (No Units) Number of LiDAR points in 6 minute window
  - l_min    (Meters)   Minimum LiDAR measurement in 6 minute window
  - l_max    (Meters)   Maximum LiDAR measurement in 6 minute window
  - l_amp    (Photons)  Mean LiDAR amplitude meas. in 6 minute window
  - l_Hs     (Meters)   LiDAR Significant Wave Height (4*STD)
  - l        (Meters)   LiDAR measurement minus bias with Bubbler

Author
------
Adam Dodge

University of Colorado Boulder

Colorado Center for Astrodynamics Research

Jet Propulsion Laboratory

Purpose
-------

This python function is used to process the LiDAR data coming from either
the Harvest Oil Platform or Catalina Island. The data is averaged from
their input frequency to a data point every 6 minutes to compare to NOAA
data. Within each 6 minute interval, data points greater than 5 standard
deviations from the mean are removed. It also has the functionality to
take in a file with overflight times at a specific location and return
in-situ measurements from the respective tide gauges.