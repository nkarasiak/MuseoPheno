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

from museopheno import sensors,datasets
from museotoolbox.raster_tools import rasterMath

raster = datasets.Sentinel2_3a_2018()
S2 = sensors.Sentinel2(n_bands=10)

print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')

# List of available indice : 
S2.available_indices.keys()

S2.setDescriptionDateMetadata('/mnt/DATAssd/S2/2018_3A/SITS_2018_BOUCONNE.tif',[20180429,20180513,20180708,20180815,20180915,20181015,20181115])
# Product raster

S2.produceRaster(input_raster=raster,output_raster='/tmp/S2.tif',expression=S2.getIndiceExpression('LChloC'),multiply_by=100,dtype=np.int16)

rM = rasterMath(raster)
X=rM.getRandomBlock()
LChloC = S2.generateIndice(X,S2.getIndiceExpression('LChloC'),dtype=np.float32)

plt.plot(LChloC[:5,:].T)

#S2.addIndice('NBR','(B08 - B12) / (B08 + B12)','(B08+B12)!=0')
#S2.convertX(np.asarray(([5,6,7,8,10,12,15,18],[8,9,10,11,8,9,10,11])).reshape(2,-1),S2.getIndiceExpression('NBR'))
