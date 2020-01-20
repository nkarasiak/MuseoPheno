#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smooth index or one band time series
================================================================================
This example shows how to smooth a time series using linear, cubic interpolation or savitzski_golay.

"""

######################
# import library
# ---------------
import numpy as np
from museopheno import time_series

###############################
# Create example values
# ----------------------------------------------------

#######################################
# Initially these values came from the LCHloC spectral index
x = np.asarray([3.4825737, 4.27786  , 5.0373, 4.7196426, 4.1233397, 4.0338645,2.7735472])    

dates = [20180429, 20180513, 20180708, 20180815, 20180915, 20181015, 20181115]

#########################################
# Resample to every 5 days
# ----------------------------
dates_5days = time_series.generate_temporal_sampling(dates[0],dates[-1],5)

    
ts_manager = time_series.SmoothSignal(dates=dates,output_dates = dates_5days)


#######################
# linear interpolation

x_linear = ts_manager.interpolation(x,kind='linear')
print(x_linear)

#######################
# cubic interpolation

x_cubic = ts_manager.interpolation(x,kind='cubic')
print(x_cubic)

#######################
# savitzski golay
# ----------------------------

# Savitzski golay can use several interpolation type before smoothing the trend

#######################
# Savitzski golay from linear interpolation

x_savgol_linear = ts_manager.savitzski_golay(x,window_length=9,polyorder=1,interpolation_params=dict(kind='linear'))

#######################
# Savitzski golay from cubic interpolation

x_savgol_cubic = ts_manager.savitzski_golay(x,window_length=9,polyorder=1,interpolation_params=dict(kind='cubic'))

x_doublelogistic= ts_manager.double_logistic(x)


#################
# Plot results
from matplotlib import pyplot as plt
plt.plot_date(ts_manager.output_datetime,x_savgol_linear.flatten(),'--',linewidth=3,color='C3',label='savitzski golay from linear interpolation',alpha=.7)    
plt.plot_date(ts_manager.output_datetime,x_savgol_cubic.flatten(),'--',linewidth=3,color='black',label='savitzski golay from cubic interpolation',alpha=.8)

plt.plot_date(ts_manager.output_datetime,x_doublelogistic.flatten(),'--',linewidth=3,color='C1',label='double logistic from cubic interpolation',alpha=.8)

plt.plot_date(ts_manager.output_datetime,x_linear.flatten(),'--',linewidth=2,color='C2',label='original with cubic interpolation',alpha=.8)

plt.plot_date(ts_manager.init_datetime,x,'o',color='C0',markersize=8,label='Original data')
plt.legend(loc='best')