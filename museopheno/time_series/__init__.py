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
import datetime as dt

from scipy import signal
from scipy import interpolate

class smoothSignal:
    def __init__(self,dates,band_order=False,order_by='date',output_dates=False,fmt='%Y%m%d'):
        """
        Smooth time series signal.
        
        Parameters
        -----------
        dates : list
            list of dates. E.g. ['20180101','20180201']
        band_order : list, optional.
        order_by : str
            Default is 'date', 
            'band'.
        output_dates
        fmt : str, optional.
            Input format of dates. Default is '%Y%m%d', so '20181231'
            
        Example
        --------
        >>> x = np.asarray([3.4825737, 4.27786  , 5.0373, 4.7196426, 4.1233397, 4.0338645,2.7735472])
        >>> y = [20180429, 20180513, 20180708, 20180815, 20180915, 20181015, 20181115]
        >>> new_dates = generateTemporalSampling(y[0],y[-1],10) # temporal sampling every 10 days
        >>> timeseries = smoothSignal(dates=y,output_dates=new_dates)
        >>> timeseries.interpolation(x,kind='cubic')
        array([3.4825737 , 4.08649468, 4.516693  , 4.80103881, 4.96740226,
       5.0436535 , 5.0576627 , 5.0373    , 5.00281393, 4.94396649,
       4.84289809, 4.68186017, 4.46665263, 4.25561504, 4.11417114,
       4.07489294, 4.07273781, 4.02461571, 3.84743661, 3.45811045,
       2.7735472 ])
        >>> timeseries.savitzski_golay(x)
        array([3.52581844, 3.96414587, 4.30156892, 4.49484286, 4.63045714,
       4.76607143, 4.90168571, 4.96423055, 4.95370595, 4.87011189,
       4.77926706, 4.65216832, 4.48881567, 4.30187759, 4.16911641,
       4.09053213, 4.04814943, 3.88019043, 3.58665514, 3.18010117,
       2.7735472 ])
        """
        self.band_order = band_order
        self.init_dates = dates
        self.init_datetime = self.convertToDatetime(dates,fmt=fmt)
        self.init_dates_int = self._convertDateToInteger(self.init_datetime,fmt=fmt)
        
        if output_dates is False:
            output_dates  = dates
        self.output_dates = output_dates
        self.output_datetime = self.convertToDatetime(output_dates,fmt=fmt)
        self.output_dates_int = self._convertDateToInteger(self.output_datetime,fmt=fmt,start_date=self.init_datetime[0])
    
    def _getTimeSeriesPositionPerBand(self):
        """
        Yields the time series for each band (all the blues, all the reds...)
        """
        if self.band_order:
            if self.order_by == 'date':
                input_bands_position = 'empty'
            elif self.order_by == 'band':
                input_bands_position = 'empty'
            output_bands_position = False
            yield input_bands_position,output_bands_position
        else:
            input_bands_position = np.arange(len(self.init_dates))
            output_bands_position = np.arange(len(self.output_dates))
            
            yield input_bands_position,output_bands_position
    
    def _resizeIfFlatten(self,X):
        if X.ndim == 1:
            X = X.reshape(-1,1)    
        return X
    
    def _getEmptyOutputArray(self,X):
        """
        
        """
        X=self._resizeIfFlatten(X)
        out_x = np.empty((len(self.output_dates),X.shape[1]),X.dtype)
        self._resizeIfFlatten(out_x)
                
        return out_x
            
    def _convertDateToInteger(self,dates,fmt='%Y%m%d',convert_to_datetime=False,start_date=False):
        if convert_to_datetime:
            dates = self.convertToDateTime(dates,fmt)
            
        if start_date :
            if convert_to_datetime:
                day0 = dt.datetime.strptime(str(start_date),fmt=fmt)
            else:
                day0 = start_date
        else:
            day0 = dates[0]
        dates_start_at_zero  = [[date-day0][0].days for date in dates]
        
        return dates_start_at_zero
    
    def convertToDatetime(self,dates,fmt='%Y%m%d'):
        """
        Convert list of dates to a list of dates with datetime type.
        
        Parameters
        -----------
        dates : list
            List of dates
        fmt : str
            Format type of each date
        """
        return [dt.datetime.strptime(str(date),fmt) for date in dates]        

    def whiitaker(self,X):
        print('TODO')
         
    def interpolation(self,X,kind='linear',**params):
        """
        Based on :class:`scipy.interpolate.interp1d`
        
        
        Parameters
        -----------
        X : array_like
            A N-D array of real values. The length of y along the interpolation axis must be equal to the length of dates.
        kind : str, default 'linear'
            Specifies the kind of interpolation as a string ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next', where 'zero', 'slinear', 'quadratic' and 'cubic' refer to a spline interpolation of zeroth, first, second or third order; 'previous' and 'next' simply return the previous or next value of the point) or as an integer specifying the order of the spline interpolator to use. Default is 'linear'.
        
        References
        ----------
        :class:`scipy.interpolate.interp1d`
        """
        
        f = interpolate.interp1d(self.init_dates_int,X,kind=kind,**params)
            
        return (f(self.output_dates_int))
         
    def savitzski_golay(self,X,window_length=3,polyorder=1,interpolation_params={},**params):
        """
        Savitzski golay 
        Based on :class:`scipy.signal.savgol_filter`
        
        References
        ----------
        :class:`scipy.signal.savgol_filter`
        """
        X_linear = self.interpolation(X,**interpolation_params)
        return signal.savgol_filter(X_linear,window_length,polyorder,**params)
                

def generateTemporalSampling(start_date, last_date, day_interval=5, save_csv=False, fmt='%Y%m%d'):
    """
    Generate a custom temporal sampling for Satellite Image Time Series.

    Parameters
    ----------    
    start_date : int, default False.
        If specified, format (YYYYMMDD).
    last_date : int, default False.
        If specified, format (YYYYMMDD).        
    day_interval : int, default 5
        Integer, days delta to between each date.
    save_csv : False or str.
        If str, path to save the csv.
    fmt : str, default '%Y%m%d'
        Format type of the input dates. 
        Default: '%Y%m%d' (e.g. 20181230)

    Example
    -------
    >>> generateTemporalSampling(20181203,20190326,day_interval=5) 
    array([20181203, 20181208, 20181213, 20181218, 20181223, 20181228,
       20190102, 20190107, 20190112, 20190117, 20190122, 20190127,
       20190201, 20190206, 20190211, 20190216, 20190221, 20190226,
       20190303, 20190308, 20190313, 20190318, 20190323, 20190328])
    >>> generateTemporalSampling('2018-03-12','2019-26-03',day_interval=15,fmt='%Y-%d-%m')
    array([20181203, 20181218, 20190102, 20190117, 20190201, 20190216,
       20190303, 20190318, 20190402])
    >>> generateTemporalSampling('2018-03-12','2019-26-03',day_interval=15,fmt='%Y-%d-%m',save_csv='/tmp/AcquisitionDates.csv')
    >>> np.loadtxt('/tmp/AcquisitionDates.csv',dtype=int)
    array([20181203, 20181218, 20190102, 20190117, 20190201, 20190216,
       20190303, 20190318, 20190402])
    """
    if isinstance(start_date, int):
        start_date = str(start_date)
    if isinstance(last_date, int):
        last_date = str(last_date)

    start_date = dt.datetime.strptime(start_date, fmt)
    last_date = dt.datetime.strptime(last_date, fmt)

    customeAcquisitionDates = [start_date.strftime('%Y%m%d')]
    newDate = start_date
    while newDate < last_date:
        newDate = newDate + dt.timedelta(day_interval)
        customeAcquisitionDates.append(newDate.strftime('%Y%m%d'))

    if save_csv:
        np.savetxt(save_csv, np.asarray(
            customeAcquisitionDates, dtype=np.int), fmt='%d')
    else:
        return np.asarray(customeAcquisitionDates, dtype=np.int)