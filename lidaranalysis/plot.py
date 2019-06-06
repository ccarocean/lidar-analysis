#!/usr/bin/env python3
############################################################################################################
# Author: Adam Dodge
# Date Created: 5/20/2019
# Date Modified: 5/29/2019
############################################################################################################
import pandas as pd
import datetime as dt
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
from lidaranalysis import loading


############################################################################################################
def load_harv(datadir_harv):
    """ Load All Harvest Data"""
    data_h = pd.DataFrame()
    for root, dirs, files in os.walk(datadir_harv):
        files.sort()
        for f in files:
            if f.startswith("harv_2"):
                tmp = loading.load_output(dt.datetime.strptime(f, 'harv_%Y%m.csv'), 'harv', datadir_harv)
                data_h = pd.concat([data_h, tmp])
                del tmp
    return data_h


############################################################################################################
def load_cata(datadir_cata):
    """ Load All Catalina Data """
    data_c = pd.DataFrame()
    for root, dirs, files in os.walk(datadir_cata):
        files.sort()
        for f in files:
            if f.startswith("cata_2"):
                tmp = loading.load_output(dt.datetime.strptime(f, 'cata_%Y%m.csv'), 'cata', datadir_cata)
                data_c = pd.concat([data_c, tmp])
                del tmp
    return data_c


def plot_harv(td, data_h, save_dir):
    # Find Today's Data
    timedelt1 = dt.timedelta(days=1)
    ind = data_h.index >= td
    data_today_h = data_h[ind]

    # Find Week Data
    timedelt7 = dt.timedelta(days=7)
    ind = data_h.index >= (td - timedelt7)
    data_rec_h = data_h[ind]

    # Plot All Harvest Pulse Width Data
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_h.index, data_h['l_rpw'], 'bo', markersize=3)
    plt.title('All Harvest LIDAR Received Pulse Width Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Received Pulse Width')
    plt.savefig(os.path.join(save_dir, 'Harvest_PW.png'), bbox_inches='tight')

    # Plot all Harvest Height Data
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_h.index, data_h['l_mean'], 'bo', markersize=3)
    plt.title('All Harvest LIDAR Height Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Harvest_All.png'), bbox_inches='tight')

    # Plot all harvest height data without outliers
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_h.index, data_h['l_mean'], 'bo', markersize=3)
    plt.title('All Harvest LIDAR Height Data - No Outliers')
    plt.xticks(rotation=90)
    plt.ylim([10, 14.5])
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Harvest_All_NO.png'), bbox_inches='tight')

    # Plot weeks harvest height data
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_rec_h.index, data_rec_h['l_mean'], 'bo')
    plt.title('Recent Harvest LIDAR Height Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Harvest_Recent.png'), bbox_inches='tight')

    # Plot yesterday's harvest height data
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_today_h.index, data_today_h['l_mean'], 'bo')
    plt.title('Today\'s Harvest LIDAR Height Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Harvest_Today.png'), bbox_inches='tight')


def plot_cata(td, data_c, save_dir):
    # Find Today's Data
    timedelt1 = dt.timedelta(days=1)
    ind = data_c.index >= td
    data_today_c = data_c[ind]

    # Find Week Data
    timedelt7 = dt.timedelta(days=7)
    ind = data_c.index >= (td - timedelt7)
    data_rec_c = data_c[ind]

    # Plot Catalina Pulse Width Data
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_c.index, data_c['l_rpw'], 'ro', markersize=3)
    plt.title('All Catalina LIDAR ReceivedPulse Width Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Received Pulse Width')
    plt.savefig(os.path.join(save_dir, 'Catalina_PW.png'), bbox_inches='tight')

    # Plot All Catalina Height Data
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_c.index, data_c['l_mean'], 'ro', markersize=3)
    plt.title('All Catalina LIDAR Height Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Catalina_All.png'), bbox_inches='tight')

    # Plot Week Catalina Height
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_rec_c.index, data_rec_c['l_mean'], 'ro')
    plt.title('Recent Catalina LIDAR Height Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Catalina_Recent.png'), bbox_inches='tight')

    # Plot Day's Catalina Height
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(data_today_c.index, data_today_c['l_mean'], 'ro')
    plt.title('Today\'s Catalina LIDAR Height Data')
    plt.xticks(rotation=90)
    plt.grid(b=True)
    plt.xlabel('Date')
    plt.ylabel('Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Catalina_Today.png'), bbox_inches='tight')


def plot_corr(data_h, data_c, save_dir):
    # Plot harvest vs catalina scatter
    hl = data_h['l_mean'][~data_h.index.duplicated()]
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(hl[data_c.index], data_c['l_mean'], 'bo')
    plt.title('Scatter Harvest vs. Catalina')
    plt.xlim([6, 14])
    plt.ylim([0, 8])
    plt.grid(b=True)
    plt.xlabel('Harvest Distance from LIDAR (m)')
    plt.ylabel('Catalina Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Harv_Cata_Scatter.png'), bbox_inches='tight')

    # Plot harvest vs catalina scatter without outliers
    plt.figure(figsize=(12, 10), dpi=80, facecolor='w')
    plt.plot(hl[data_c.index], data_c['l_mean'], 'bo')
    plt.title('Scatter Harvest vs. Catalina - No Outliers')
    plt.xlim([11, 14])
    plt.ylim([0.9, 4])
    plt.grid(b=True)
    plt.xlabel('Harvest Distance from LIDAR (m)')
    plt.ylabel('Catalina Distance from LIDAR (m)')
    plt.savefig(os.path.join(save_dir, 'Harv_Cata_Scatter_NO.png'), bbox_inches='tight')
