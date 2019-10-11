#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate time sampling (dates for time series) file with different day interval
================================================================================

This example shows how generate sample temporal sampling different delta day from the first date
"""

######################
# import library
# ---------------

from museopheno.time_series import generateTemporalSampling

###############################
# Generate acquistion date file
# ----------------------------------

start_date = '20171120'
last_date = '20180505'
delta = 5
acquisition_dates = generateTemporalSampling(start_date='20171120',last_date='20180505',day_interval=delta)

print('There are {} dates between {} and {} using an interval of {} days'.format(len(acquisition_dates),start_date,last_date,delta))

delta = 10
acquisition_dates = generateTemporalSampling(start_date='20171120',last_date='20180505',day_interval=delta)

print('There are {} dates between {} and {} using an interval of {} days'.format(len(acquisition_dates),start_date,last_date,delta))

#############################
# Save as a csv for gap-filling in OTB
# -----------------------------------------

# If you use otb ImageTimeSeriesGapFilling, you have to pass a csv with a line for each date using fmt '%Y%l%d'.
# You can directly save as csv with this format.

generateTemporalSampling(start_date='20171120',last_date='20180505',day_interval=delta,save_csv='/tmp/sample_time.csv')

############################
# Generate acquisition dates from Sentinel2 images
# -------------------------------------------------

from museopheno.sensors import Sentinel2
S2manager = Sentinel2()

####################
# For more information, see :class:`museopheno.sensors.Sentinel2.generateTemporalSampling`
