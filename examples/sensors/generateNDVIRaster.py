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
Generate a NDVI time series
=============================================================================

This example shows how to produce a NDVI time series from a Sentinel-2 time series.
"""
###########################################################
# Import libraries
# ---------------------------
from museopheno import sensors,datasets
import numpy as np

###########################################################
# Import dataset
# ---------------------------
raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)

###########################################################
# Create an instance of sensors.Sentinel2()

S2 = sensors.Sentinel2(n_bands=10)

print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')

###########################################################
# List of available indice : 

print(S2.available_indices.keys())

###########################################################
# Write metadata in each band (date + band name)
# ------------------------------------------------------

###########################################################
# This is useful to show date in band number in Qgis

S2.setDescriptionMetadata(raster,dates)

###########################################################
# Produce NDVI time series from and to a raster
# ----------------------------------------------
S2.generateRaster(input_raster=raster,output_raster='/tmp/indice.tif',expression=S2.getIndiceExpression('NDVI'),dtype=np.float32)

##############################
# Plot NDVI indice
from museotoolbox.raster_tools import rasterMath
from matplotlib import pyplot as plt

rM = rasterMath('/tmp/indice.tif')
NDVI=rM.getRandomBlock() #randomly select a block
from datetime import datetime
dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
plt.plot_date(dateToDatetime,NDVI[:10,:].T,'-o')
plt.ylabel('NDVI')