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
import gdal
from ..indices import generateIndice
from museotoolbox.raster_tools import rasterMath as _rasterMath

class sensorManager:
    def __init__(self,sensor_name,n_bands,band_order):
        self.sensor_name = sensor_name
        self.n_bands = n_bands
        self.available_indices = dict()
        self._addEachBandAsIndice()
        self.configureTimeSeries()
        # add each band in list of indice
    
    def configureTimeSeries(self,order_by='date'):
        """
        If band are ordered by date or by band
        
        order_by : str, default 'date'.
            if 'date', means your raster is stacked in this way : B1, B2 to Bx for the first date, then B1,B2 to Bx for the second date...
            if 'band', means your raster is stacked in this way : B1 first date, B1 second date... to B1 last date, then B2 first date...
        """
        if not order_by in ['date','band']:
            raise ValueError('Sorry, but MuseoPheno only manages raster organized by date or band')
        if order_by == 'band':
            raise ValueError('Sorry, but MuseoPheno has not yet implemented stack per band')

        self.order_by = order_by
        
    def __checkIndiceExist(self,indiceName):
        if indiceName not in self.available_indices.keys():
            raise ValueError(str(indiceName)+' is not an available indice. Please select one of them : '+', '.join(self.available_indices.keys()))
        else:
            return True
    def getIndiceExpression(self,indiceName):
        if self.__checkIndiceExist(indiceName):
            return self.available_indices[indiceName]

    def addIndice(self,indice_name,expression,condition=False):
        self.available_indices[indice_name] = dict(expression=expression)
        if condition:
            self.available_indices[indice_name]['condition'] = condition
            
    def _addEachBandAsIndice(self):
        for band in self.band_order:
            self.available_indices['B'+str(band)] = dict(expression='B'+str(band))
    
    def generateIndice(self,X,expression,divide_X_by=1,interpolate_nan=True,dtype=np.float32,multiply_by=1):
        X_ = generateIndice(X,self.band_order,expression=expression,n_comp=self.n_bands,interpolate_nan=interpolate_nan,dtype=dtype,multiply_by=multiply_by)
        return X_
    
    def produceRaster(self,input_raster,output_raster,expression,divide_X_by=1,interpolate_nan=True,dtype=np.float32,multiply_by=1):
        rM = _rasterMath(input_raster,message='Computing indice')
        rM.addFunction(generateIndice,output_raster,outNumpyDT=dtype,band_order=self.band_order,expression=expression,n_comp=self.n_bands,interpolate_nan=interpolate_nan,multiply_by=multiply_by)
        rM.run()
        
    def setDescriptionMetadata(self,input_raster,dates):
        """
        input_raster : str.
            Path of the raster to write in the metadata each band number and date.
        dates : list.
            list of each date 
        
        Exemples
        ---------
        >>> setDescriptionMetadata(raster,[20180429,20180513,20180708,20180815,20180915,20181015,20181115])
        """
        ds = gdal.Open(input_raster)
        nb=ds.RasterCount
        
        def convertDateFormat(date,bandName):
            bandDesc = str(date)[:4]+'-'+str(date)[4:6]+'-'+str(date)[6:]
            bandDesc += ' - '+str(bandName)
            
            return bandDesc
        
        for idx,band in enumerate(self.band_order):
            for i in range(int(nb/self.n_bands)):
                bandPos = (idx+1)+(self.n_bands*i)
                bandDesc = convertDateFormat(dates[i],self.band_order[idx])
                ds.GetRasterBand(bandPos).SetDescription(bandDesc)
        ds.FlushCache()
        ds=None
            
    
class Sentinel2(sensorManager):

    def __init__(self, n_bands = 4, band_order='default'):
                
        self.n_bands = n_bands
        
        if band_order == 'default':
                if self.n_bands == 4:
                    self.band_order = np.array(['2', '3', '4', '8'])
                elif self.n_bands == 10:
                    self.band_order = np.array(['2', '3', '4', '8', '5', '6', '7', '8A', '11', '12'])
                else:
                    raise ValueError('If your Sentinel-2 raster has not 4 or 10 bands, please define band_order parameter.')
        
        super().__init__('Sentinel2',n_bands,self.band_order)            
        
        indices = dict(ACORVI=['( B8 - B4 + 0.05 ) / ( B8 + B4 + 0.05 ) ','(B8+B4+0.05) != 0'],
            ACORVInarrow=['( B8A - B4 + 0.05 ) / ( B8A + B4 + 0.05 ) ','(B8A+B4+0.05) != 0'],
            SAVI=['1.5 * (B8 - B4) / ( B8 + B4 + 0.5 )'],
            EVI=['( 2.5 * ( B8 - B4 ) ) / ( ( B8 + 6 * B4 - 7.5 * B2 ) + 1 )'],
            EVI2=['( 2.5 * (B8 - B4) ) / (B8 + 2.4 * B4 + 1) ','B8+2.4*B4+1 != 0'],
            PSRI=['( (B4 - B2) / B5 )','B5 != 0'],
            ARI=['( 1 / B3 ) - ( 1 / B5 )','np.logical_and(B3 != 0, B5 != 0)'],
            ARI2=['( B8 / B2 ) - ( B8 / B3 )',' np.logical_and(B2 != 0, B3 != 0)'],
            MARI=['( (B5 - B5 ) - 0.2 * (B5 - B3) ) * (B5 / B4)', 'B4 != 0'],
            CHLRE=['np.power(B5 / B7,-1.0)','B5!=0'],
            MCARI=[' ( ( B5 - B4 ) - 0.2 * ( B5 - B3 ) ) * ( B5 / B4 )','B4 != 0'],
            MSI=['B11 / B8','B8 != 0'],
            MSIB12=['B12 / B8','B8 != 0'],
            NDrededgeSWIR=['( B6 - B12 ) / ( B6 + B12 )','( B6 + B12 ) != 0'],
            SIPI2=['( B8 - B3 ) / ( B8 - B4 )','B8 - B4 != 0'],
            NDWI=['(B8-B11)/(B8+B11)','(B8+B11) != 0'],
            LCaroC=['B7 / ( B2-B5 )','( B7 ) != 0'],
            LChloC=['B7 / B5','B5 != 0'],
            LAnthoC=['B7 / (B3 - B5) ','( B3-B5 ) !=0'],
            Chlogreen=['B8A / (B3 + B5)'],
            NDVI=['(B8-B4)/(B8+B4)','(B8+B4) != 0'],
            NDVInarrow=['(B8A-B4)/(B8A+B4)','(B8A+B4) != 0'],
            NDVIre=['(B8A-B5)/(B8A+B5)','(B8A+B5) != 0'],
            RededgePeakArea=['B4+B5+B6+B7+B8A'],
            Rratio=['B4/(B2+B3+B4)'],
            MTCI=['(B6 - B5)/(B5 - B4)','(B5-B4) != 0'],
            S2REP=['35 * ((((B7 + B4)/2) - B5)/(B6 - B5))'],
            IRECI=['(B7-B4)/(B5/B6)','np.logical_and(B5 != 0, B6 != 0)'])
        
        for indice in indices.keys():
            if len(indices[indice])==1:
                self.addIndice(indice,indices[indice])
            else:
                self.addIndice(indice,indices[indice][0],indices[indice][1])
        
        
class Formosat2(sensorManager):

    def __init__(self, n_bands = 4, band_order='default'):
                
        self.n_bands = n_bands
        
        if band_order == 'default':
                if self.n_bands == 4:
                    self.band_order = np.array(['1', '2', '3', '4'])
                else:
                    raise ValueError('If your FormoSat-2 raster has not 4, please define band_order parameter.')
        
        super().__init__('FormoSat2',n_bands,self.band_order)            
        
        indices = dict(ACORVI=['( B4 - B3 + 0.05 ) / ( B4 + B3 + 0.05 ) ','(B4+B3+0.05) != 0'],
            SAVI=['1.5 * (B4 - B3) / ( B4 + B3 + 0.5 )'],
            EVI=['( 2.5 * ( B4 - B3 ) ) / ( ( B4 + 6 * B3 - 7.5 * B1 ) + 1 )'],
            EVI2=['( 2.5 * (B4 - B3) ) / (B4 + 2.4 * B3 + 1) ','B4+2.4*B3+1 != 0'],
            ARI2=['( B4 / B1 ) - ( B4 / B2 )',' np.logical_and(B1 != 0, B2 != 0)'],
            NDVI=['(B4-B3)/(B4+B3)','(B4+B3) != 0'],
            Rratio=['B3/(B1+B2+B3)'])
        
        for indice in indices.keys():
            if len(indices[indice])==1:
                self.addIndice(indice,indices[indice])
            else:
                self.addIndice(indice,indices[indice][0],indices[indice][1])    
