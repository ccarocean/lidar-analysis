import os


def chng_coops(month, loc, dir):
    """ Function for changing last run coops month to change coops data in files. """
    with open(os.path.join(dir, 'lastcoopsmonth_'+loc+'.txt'), 'w') as f:
        f.write(str(month))
    print('lastcoopsmonth_'+loc+'.txt updated to ' + str(month))


def chng_day(day, loc, dir):
    """ Function for changing last run day to change LiDAR data in files. """
    print(os.path.join(dir, 'lastday_'+loc+'.txt'))
    with open(os.path.join(dir, 'lastday_'+loc+'.txt'), 'w') as f:
        f.write(str(day))
    print('lastday_' + loc + '.txt updated to ' + str(day))
