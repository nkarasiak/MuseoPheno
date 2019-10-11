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
Produce a new raster with indices stacked in new bands
=============================================================================

This example shows how to add to a raster spectral indices.
Here we add LChloC and ACORVI (a modified NDVI).

"""
########################################
# Import libraries
# ----------------------------

import numpy as np
from museopheno import sensors,datasets

# to add custom  creation of new raster, import rasterMath
from museotoolbox.raster_tools import rasterMath 

##############################
# Import dataset
# ----------------------

raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)
S2 = sensors.Sentinel2(n_bands=10)

print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')

###############################
# List of available indice : 

S2.available_indices.keys()

##############################################
# Define a custom function
# ---------------------------------------

def createSITSplusIndices(X):
    X1 = S2.generateIndice(X,S2.getIndiceExpression('LChloC'),multiply_by=100,dtype=np.int16)
    X2 = S2.generateIndice(X,S2.getIndiceExpression('ACORVI'),multiply_by=100,dtype=np.int16)
    
    return np.hstack((X,X1,X2)).astype(np.int16)

#########################################
# Use rasterMath to read and write block per block the raster according to a function

rM = rasterMath(raster)

X = rM.getRandomBlock()
print('Block has {} pixels and {} bands'.format(X.shape[0],X.shape[1]))

################################
# Now we can try our function

XwithIndices = createSITSplusIndices(X)
print('Raster+indice produced has {} pixels and {} bands'.format(XwithIndices.shape[0],XwithIndices.shape[1]))

##################################
# Now we add our function as the test was a success
rM.addFunction(createSITSplusIndices,'/tmp/SITSwithIndices.tif')

########################
# Produce raster

rM.run()

##################
# Plot image
from matplotlib import pyplot as plt
rM = rasterMath('/tmp/SITSwithIndices.tif')
X=rM.getRandomBlock() #randomly select a block
plt.plot(X[:20,:].T)
