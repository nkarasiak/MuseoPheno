#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#  __  __                        _____  _
# |  \/  |                      |  __ \| |
# | \  / |_   _ ___  ___  ___   | |__) | |__   ___ _ __   ___
# | |\/| | | | / __|/ _ \/ _ \  |  ___/| '_ \ / _ \ '_ \ / _ \
# | |  | | |_| \__ \  __/ (_) | | |    | | | |  __/ | | | (_) |
# |_|  |_|\__,_|___/\___|\___/  |_|    |_| |_|\___|_| |_|\___/
#
# @author:  Nicolas Karasiak
# @site:    www.karasiak.net
# @git:     www.github.com/nkarasiak/MuseoPheno
# =============================================================================
import numpy as np
import datetime as dt

def generateTemporalSampling(start_date, last_date,day_interval=5,save_csv=False,fmt='%Y%m%d'):
    """
    Generate a custom temporal sampling for Satellite Image Time Series.

    Parameters
    ----------    
    start_date : int, default False.
        If specified, format (YYYYMMDD).
    last_date : int, default False.
        If specified, format (YYYYMMDD).        
    day_interval : int, default 5
        Integer, days delta to between each date.
    save_csv : False or str.
        If str, path to save the csv.
    fmt : str, default '%Y%m%d'
        Format type of the input dates. 
        Default: '%Y%m%d' (e.g. 20181230)
        
    Example
    -------
    >>> generateTemporalSampling(20181203,20190326,day_interval=5) 
    array([20181203, 20181208, 20181213, 20181218, 20181223, 20181228,
       20190102, 20190107, 20190112, 20190117, 20190122, 20190127,
       20190201, 20190206, 20190211, 20190216, 20190221, 20190226,
       20190303, 20190308, 20190313, 20190318, 20190323, 20190328])
    >>> generateTemporalSampling('2018-03-12','2019-26-03',day_interval=15,fmt='%Y-%d-%m')
    array([20181203, 20181218, 20190102, 20190117, 20190201, 20190216,
       20190303, 20190318, 20190402])
    >>> generateTemporalSampling('2018-03-12','2019-26-03',day_interval=15,fmt='%Y-%d-%m',save_csv='/tmp/AcquisitionDates.csv')
    >>> np.loadtxt('/tmp/AcquisitionDates.csv',dtype=int)
    array([20181203, 20181218, 20190102, 20190117, 20190201, 20190216,
       20190303, 20190318, 20190402])
    """
    if isinstance(start_date,int):
        start_date = str(start_date)
    if isinstance(last_date,int):
        last_date = str(last_date)
        
    start_date = dt.datetime.strptime(start_date, fmt)
    last_date = dt.datetime.strptime(last_date, fmt)

    customeAcquisitionDates = [start_date.strftime('%Y%m%d')]
    newDate = start_date
    while newDate < last_date:
        newDate = newDate + dt.timedelta(day_interval)
        customeAcquisitionDates.append(newDate.strftime('%Y%m%d'))
        
    if save_csv:
        np.savetxt(save_csv, np.asarray(customeAcquisitionDates, dtype=np.int), fmt='%d')
    else:
        return np.asarray(customeAcquisitionDates, dtype=np.int)
