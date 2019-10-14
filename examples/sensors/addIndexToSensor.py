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
"""
Add or modify an spectral index of a sensor
=============================================================================

This example shows how to add or modify an index for a specific sensor.
Here we add/modify the NBR index (Normalized Burn-Ratio), then we generate a raster.
"""

####################################"
# Import libraries
# ------------------
import numpy as np
from museopheno import sensors,datasets


####################################"
# Import dataset
# ------------------
X,dates = datasets.Sentinel2_3a_2018(return_dates=True,get_only_sample=True)

S2 = sensors.Sentinel2(n_bands=10)

print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')

################################
# Look at available S2 index
S2.available_index

#################################
# add the NBR index
# ------------------------

#######################################
# This index is already in MuseoPheno, but if you change the expression it will overwrite the previous one

S2.addIndex('NBR',expression='(B08 - B12) / (B08 + B12)',condition='(B08+B12)!=0')

################################
# compute NBR from an array
# -----------------------------------
NBR = S2.generateIndex(X,S2.getIndexExpression('NBR'))

#############################
# Produce the index raster
# ---------------------------

# We multiply by 100 to save with int16 datatype

raster = datasets.Sentinel2_3a_2018()
S2.generateRaster(raster,output_raster='/tmp/NBR.tif',expression=S2.getIndexExpression('NBR'),multiply_by=100,dtype=np.int16)

###################
# plot result

from matplotlib import pyplot as plt
from datetime import datetime
dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
plt.plot_date(dateToDatetime,NBR[:20,:].T,'-o')
plt.ylabel('Normalized Burn Ratio')
