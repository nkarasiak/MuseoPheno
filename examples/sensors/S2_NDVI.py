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
Compute a spectral index from S2 Time Series
=============================================================================

This example shows how to compute an index (here NDVI) from a S2 with 10 bands.
The raster is order date per date (blue,green,red...date 1 then blue,green,red... date 2...)
"""

###########################################################
# Import libraries
# ---------------------------

import numpy as np
from museopheno import sensors,datasets
from museotoolbox.processing import RasterMath

###########################################################
# Import dataset
# ---------------------------
raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)

###########################################################
# Define an instance of sensors.Sentinel2()

S2 = sensors.Sentinel2(n_bands=10)

# check default band_order
print('Default band order for 10 bands is : '+', '.join(S2.bands_order)+'.')

# List of available index : 
S2.available_indices.keys()

###########################################################
# Write metadata in each band (date + band name)
# ------------------------------------------------------

S2.set_description_metadata(raster,dates)

###########################################################
# Generate a raster with NDVI index
# ---------------------------------------------

# show expression and condition of NDVI index
print(S2.get_index_expression('NDVI'))

# generate raster
S2.generate_raster(input_raster=raster,output_raster='/tmp/S2.tif',expression=S2.get_index_expression('NDVI'),dtype=np.float32)

######################################"
# Plot image

rM = RasterMath(raster)
X=rM.get_random_block()
NDVI = S2.generate_index(X,S2.get_index_expression('NDVI'),dtype=np.float32)

from matplotlib import pyplot as plt
from datetime import datetime
dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
plt.plot_date(dateToDatetime,NDVI[:10,:].T,'-o')
plt.ylabel('Leaf Chlorophyll Content')