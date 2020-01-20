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
Compute Leaf Chlorophyll Content from S2 Time Series
=============================================================================

This example shows how to compute an index (here LChloC) from a S2 with 10 bands.
The raster is order date per date (blue,green,red...date 1 then blue,green,red... date 2...)

"""


###########################################################
# Import libraries

import numpy as np
from museopheno import sensors,datasets

###########################################################
# Import raster dataset with list of dates

raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)

###########################################################
# Create an instance of sensors.Sentinel2 with 10bands

S2 = sensors.Sentinel2(n_bands=10)

print('Default band order for 10 bands is : '+', '.join(S2.bands_order)+'.')

# List of available index : 
S2.available_indices.keys()

###########################################################
# Write metadata in each band (date + band name)
# ------------------------------------------------------

###########################################################
# Write metadata in each band (date + band name) in order to use
# raster timeseries manager plugin on QGIS or to have the date and the band in
# the list of bands QGIS.

S2.set_description_metadata(raster,dates)

#########################################
# Generate index from array
# ---------------------------------

X = datasets.Sentinel2_3a_2018(return_random_sample=True)
LChloC = S2.generate_index(X,S2.get_index_expression('LChloC'),dtype=np.float32)
print(LChloC)

#########################################
# Generate index from and to a raster
# ---------------------------------------

S2.generate_raster(input_raster=raster,output_raster='/tmp/LChloC.tif',expression=S2.get_index_expression('LChloC'),dtype=np.float32)


#########################################
# Plot example of LChloC

from matplotlib import pyplot as plt
from datetime import datetime
dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
plt.plot_date(dateToDatetime,LChloC[:10,:].T,'-o')
plt.ylabel('Leaf Chlorophyll Content')
import os
os.remove('/tmp/LChloC.tif')