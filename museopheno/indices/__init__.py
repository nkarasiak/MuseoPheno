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
np.seterr(divide='ignore')
import re

def areBandsAvailables(band_order,expression):

    bandsToChange = re.findall('B[0-9]*[A-Z]*',str(expression))
    band_order_withoutB  = []
    for b in band_order:
        if b.capitalize().startswith('B'):
            b = b[1:]
        while b[0] == '0':
            b = b[1:]
        band_order_withoutB.append(str(b).capitalize())
    
    missing_bands = []
    
    for band in bandsToChange:
        band_withoutBand0 = band[1:]
        while str(band_withoutBand0).find('0') == 0:
            band_withoutBand0 = band_withoutBand0[1:]
            
        if str(band_withoutBand0).capitalize() in band_order_withoutB:
            pass
        else:
            missing_bands.append(band)    
    if len(missing_bands)>0:
        if len(missing_bands)>1:
            verb,s= ['are','s']
        else:
            verb,s = ['is','']
        raise ValueError('Band{} {} {} missing.'.format(s,missing_bands,verb))
    else:
        return True
    

def generateIndice(X,band_order,expression,n_comp=False,interpolate_nan=True,divide_X_by=1,multiply_by=1,dtype=np.float64):
    """
    Parameters
    ----------
    indiceName : str.
        Indice Name
    X : array.
    n_comp : int or False, default False.
        If False, n_comp is the number of columns of your vector (X.shape[1]).
        If integer, should be the same size or a multiple of band_order length in order to manage time series.
    
    """
    
    def __nan_helper(y):
        """Helper to handle indices and logical indices of NaNs.
    
        Input:
            - y, 1d numpy array with possible NaNs
        Output:
            - nans, logical indices of NaNs
            - index, a function, with signature indices= index(logical_indices),
              to convert logical indices of NaNs to 'equivalent' indices
        Example:
            >>> # linear interpolation of NaNs
            >>> nans, x= nan_helper(y)
            >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
        """
    
        return np.isnan(y), lambda z: z.nonzero()[0]
    if X.ndim==1:
        X = X.reshape(1,-1)
    X = X/divide_X_by
    
    nDates = X.shape[1]/n_comp
    if nDates != int(nDates):
        raise ValueError('n_comp is {} but as there are a total of {} bands, there must be an error'.format(n_comp,X.shape[1]))
    else:
        nDates = int(nDates)
        
    outIndice = np.zeros((X.shape[0],nDates),dtype=np.float64)
    
    if areBandsAvailables(band_order,expression):
        for date in range(nDates):
            if isinstance(expression,str):
                mathExp = expression
                condition = False
            else:    
                mathExp = expression['expression']
                if 'condition' in expression.keys():
                    condition = expression['condition']
                else:
                    condition = False
            dateIndice = __convertBandToArrayIdx(X,mathExp,n_comp,date,band_order,condition=condition)
            outIndice[:,date] = dateIndice
    
        if interpolate_nan:
            outIndice = np.where(np.logical_or(outIndice==np.inf,outIndice==-np.inf),np.nan,outIndice)
            
            for i in range(outIndice.shape[0]):
                nans, x = __nan_helper(outIndice[i,:])
                if not np.all(nans==False):
                    outIndice[i,nans]= np.interp(x(nans), x(~nans), outIndice[i,~nans])
        if multiply_by != 1:
            outIndice *= multiply_by
        
        if dtype:
            outIndice = outIndice.astype(dtype)

        return outIndice
        
def __convertBandToArrayIdx(X,expression,n_comp,date,band_order,condition=False,nodata=-9999):
    X = np.copy(X)
#    bandsToChange = re.findall('B[0-9]*',str(expression))
    bandsToChange = re.findall('B[0-9]*[A-Z]*',str(expression))
    out = np.zeros(X[:,0].shape)
    out[:] = nodata
    
    for band in set(bandsToChange):    
        originalBand = band[1:] # to remove B
        while originalBand[0] == '0':
            originalBand = originalBand[1:]
        bandIdx = np.where(band_order == originalBand)[0][0]
        newBand = n_comp * (date) + (bandIdx)
        if condition:
            condition = condition.replace(band,"X[:,{}]".format(newBand))
        expression = expression.replace(band, "X[:,{}]" .format(newBand))
        
    if condition:
        TF = eval(condition)
        out[TF] = eval(expression)[TF]
    else:
        out = eval(expression)
    return out

