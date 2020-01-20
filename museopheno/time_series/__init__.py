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
The :mod:`museopheno.time_series` module gathers functions to compute expression and 
smooth time series.
"""
import datetime as dt

import math
import numpy as np
np.seterr(divide='ignore')

from scipy import signal
from scipy.optimize import minimize, Bounds
from museopheno.time_series import __dl as fun_dl # double logistic by M. Fauvel
from scipy import interpolate

import re

def get_phenology_metrics(X,sos=0.2,eos=0.8):
    feat = PhenologyMetrics(X,sos,eos)
    
    return feat.sos,feat.eos

class PhenologyMetrics:
    """
    Get phenology metrics from one feature.
    start of season, end of season, length of season and amplitude.
    
    Parameters
    ------------
    X : array
        array (1 dim)
    sos : float
        Percentage
    eos : float
        Percentage 
    """
    def __init__(self,X,sos=0.2,eos=0.8):
        self._argmax = np.argmax(X)
        self._argmin = np.argmin(X)
        self.sos_thresold = sos
        self.eos_thresold = eos

        self.n_features = 1
        if X.ndim ==2:
            if X.shape[0] != 1:
                raise ValueError('only one feature at a time')
    
        self.X = X.flatten()
            
        self._get_sos()
        self._get_eos()
        self._get_los()
        self._get_amp()
        
    def _get_sos(self):
        val = np.amin(self.X[...,:self._argmax])+self.sos_thresold*(self.X[...,self._argmax]-np.amin(self.X[...,:self._argmax]))
        idx = np.searchsorted(self.X,val)
        self.sos = idx
    def _get_eos(self):
        val = np.amin(self.X[...,self._argmax:])+self.eos_thresold*(self.X[...,self._argmax]-np.amin(self.X[...,self._argmax:]))
        idx = np.searchsorted(self.X[::-1],val,side='right')
        self.eos = len(self.X)-idx
    def _get_los(self):
        self.los = self.eos-self.sos
    def _get_amp(self):
        self.amp = self.X[self._argmax]-self.X[self._argmin]
        
        
def _convert_band_to_array_idx(X, expression, n_comp,
                            date, bands_order, condition=False, order_by='date', nodata=-9999):
    X = np.copy(X)
#    bandsToChange = re.findall('B[0-9]*',str(expression))
    bandsToChange = re.findall('B[0-9]*[A-Z]*', str(expression))
    out = np.zeros(X[:, 0].shape)
    out[:] = nodata

    for band in set(bandsToChange):  # set to order band
        originalBand = band[1:]  # to remove B
        while originalBand[0] == '0':
            originalBand = originalBand[1:]
        bandIdx = np.where(np.in1d(bands_order, originalBand) == True)[0]

        if order_by == 'date':
            newBand = n_comp * date + bandIdx
        elif order_by == 'band':
            newBand = bandIdx*date+n_comp

        if condition:
            condition = condition.replace(band, "X[:,{}]".format(newBand))
        if isinstance(expression,list):
            expression = expression[0]
        expression = expression.replace(band, "X[:,{}]" .format(newBand))

    if condition:
        TF = eval(condition).flatten()
        out[TF] = eval(expression)[TF].flatten()
    else:
        out = eval(expression)
    return out.flatten()


def _are_bands_availables(bands_order, expression, compulsory=True):
    """
    Check if band needed for expression are available

    Parameters
    -----------
    bands_order : list
        list of bands (e.g. ['2','3','4','8'])
    expression : str
        expression (e.g. 'B08/B02*100')

    Examples
    ---------
    >>> _are_bands_availables(['2','3','4','8'],'B08/B02*100')
    True
    >>> _are_bands_availables(['2','3','4','8'],'B8A/B04*100')
    ValueError: Band ['B8A'] is missing.
    """
    bandsToChange = re.findall('B[0-9]*[A-Z]*', str(expression))
    bands_order_withoutB = []
    for b in bands_order:
        if b.capitalize().startswith('B'):
            b = b[1:]
        while b[0] == '0':
            b = b[1:]
        bands_order_withoutB.append(str(b).capitalize())

    missing_bands = []

    for band in bandsToChange:
        band_withoutBand0 = band[1:]
        while str(band_withoutBand0).find('0') == 0:
            band_withoutBand0 = band_withoutBand0[1:]

        if str(band_withoutBand0).capitalize() in bands_order_withoutB:
            pass
        else:
            missing_bands.append(band)
    if len(missing_bands) > 0:
        if compulsory:
            if len(missing_bands) > 1:
                verb, s = ['are', 's']
            else:
                verb, s = ['is', '']
            raise ValueError(
                'Band{} {} {} missing.'.format(
                    s, missing_bands, verb))
        else:
            return False
    else:
        return True


def ExpressionManager(X, bands_order, expression, interpolate_nan=True,
                      divide_X_by=1, multiply_by=1, order_by='date', dtype=np.float32):
    """
    Generate expression/index from an array according to a bands_order, and expression.

    The easiest way to use it is to choose a sensor from :class:`museopheno.sensors`.

    Parameters
    ----------
    X : array.
        array where each line is a pixel.
    bands_order : list
        list of band order (e.g. ['2','3','4','8'])
    expression : str or dict.
        If str, contains only the expression (e.g. 'B8/B2')
        If dict, contains a expression key and can contain a condition key.
        See `museopheno.sensors.sensorManager.addIndice` function.
    inteprolate_nan : boolean, default True, optional.
        If nan value a linear interpolation is done.
    divide_X_by : integer or float, default 1, optional.
        Value to divide X before computing the indice
    multiply_by : integer or float, default 1, optional.
        Value to multiply the result (e.g. 100 to set the NDVI between -100 and 100)
    order_by : str, default 'date', optional.
        if 'date', means your raster is stacked in this way : B1, B2 to Bx for the first date, then B1,B2 to Bx for the second date...
        if 'band', means your raster is stacked in this way : B1 first date, B1 second date... to B1 last date, then B2 first date...
    dtype : numpy dtype, default np.float32, optional.
        dtype of the output (e.g. np.int16 to store the NDVI in integer value)

    Example
    --------
    >>> from museopheno import datasets, expressionManager
    >>> X = datasets.Sentinel2_3a_2018(get_only_sample=True)
    >>> indices.generateIndice(X,bands_order=['2','3','4','8','5','6','7','8A','11','12'],expression='B4/B8')


    """

    def _nan_helper(y):
        return np.isnan(y), lambda z: z.nonzero()[0]

    if X.ndim == 1:
        X = X.reshape(1, -1)
    X = X / divide_X_by

    nDates = X.shape[1] / len(bands_order)
    if nDates != int(X.shape[1] / len(bands_order)):
        raise ValueError(
            'bands_order is not a multiple of the number of columns of your array which contains {} bands.'.format(
                X.shape[1]))
    else:
        n_comp = int(X.shape[1] / nDates)
        nDates = int(nDates)

    outIndice = np.zeros((X.shape[0], nDates), dtype=np.float64)

    if _are_bands_availables(bands_order, expression):
        for date in range(nDates):
            if isinstance(expression, str):
                mathExp = expression
                condition = False
            else:
                mathExp = expression['expression']
                if 'condition' in expression.keys():
                    condition = expression['condition']
                else:
                    condition = False
            dateIndice = _convert_band_to_array_idx(
                X, mathExp, n_comp, date, bands_order, condition=condition, order_by=order_by)
            outIndice[:, date] = dateIndice

        if interpolate_nan:
            outIndice = np.where(
                np.logical_or(
                    outIndice == np.inf,
                    outIndice == -
                    np.inf),
                np.nan,
                outIndice)

            for i in range(outIndice.shape[0]):
                nans, x = _nan_helper(outIndice[i, :])
                if not np.all(nans == False):
                    outIndice[i, nans] = np.interp(
                        x(nans), x(~nans), outIndice[i, ~nans])
        if multiply_by != 1:
            outIndice *= multiply_by

        if dtype:
            outIndice = outIndice.astype(dtype)

        return outIndice


class SmoothSignal:
    def __init__(self, dates, bands_order=False, order_by='date', output_dates=False, fmt='%Y%m%d'):
        """
        Smooth time series signal.

        Parameters
        -----------
        dates : list
            list of dates. E.g. ['20180101','20180201']
        bands_order : list, optional.
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
        >>> new_dates = generate_temporal_sampling(y[0],y[-1],10) # temporal sampling every 10 days
        >>> timeseries = SmoothSignal(dates=y,output_dates=new_dates)
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
        self.bands_order = bands_order
        self.order_by = order_by

        # input dates
        self.init_dates = dates
        self.init_n_dates = len(dates)
        self.init_datetime = self.convert_to_datetime(dates, fmt=fmt)
        self.init_dates_int = self._convert_date_to_integer(
            self.init_datetime, fmt=fmt)

        # output dates
        if output_dates is False:
            output_dates = dates
        self.output_dates = output_dates
        self.output_n_dates = len(output_dates)
        self.output_datetime = self.convert_to_datetime(output_dates, fmt=fmt)
        self.output_dates_int = self._convert_date_to_integer(
            self.output_datetime, fmt=fmt, start_date=self.init_datetime[0])
        
        self.output_dates_delta = self.output_dates_int[1]-self.output_dates_int[0]
    def _get_time_series_position_per_band(self, X):
        """
        Yields the time series for each band (all the B2, all the B8...)
        """
        if self.bands_order is not False:
            if int(X.shape[1]/self.init_n_dates) != len(self.bands_order):
                raise ValueError('mismatch')
            for idx_band in range(len(self.bands_order)):
                if self.order_by == 'date':
                    input_bands_position = [
                        idx_band*self.init_n_dates+d for d in range(self.init_n_dates)]
                    output_bands_position = [
                        idx_band*self.output_n_dates+d for d in range(self.output_n_dates)]
                elif self.order_by == 'band':
                    input_bands_position = [
                        idx_band+len(self.init_dates)*d for d in range(self.init_n_dates)]
                    output_bands_position = [
                        idx_band+len(self.output_dates)*d for d in range(self.output_n_dates)]
                yield input_bands_position, output_bands_position
        else:
            input_bands_position = np.arange(len(self.init_dates))
            output_bands_position = np.arange(len(self.output_dates))

            yield input_bands_position, output_bands_position

    def _resize_if_flatten(self, X):
        if X.ndim == 1:
            X = X.reshape(1, -1)
        return X

    def _get_empty_output_array(self, X):
        X = self._resize_if_flatten(X)
        if self.bands_order is not False:
            multiply_by = len(self.bands_order)
        else:
            multiply_by = 1
        out_x = np.empty(
            (X.shape[0], len(self.output_dates)*multiply_by), X.dtype)
        self._resize_if_flatten(out_x)

        return out_x

    def _convert_date_to_integer(self, dates, fmt='%Y%m%d', convert_to_datetime=False, start_date=False):
        if convert_to_datetime:
            dates = self.convert_to_datetime(dates, fmt)

        if start_date:
            if convert_to_datetime:
                day0 = dt.datetime.strptime(str(start_date), fmt=fmt)
            else:
                day0 = start_date
        else:
            day0 = dates[0]
        dates_start_at_zero = [[date-day0][0].days for date in dates]

        return dates_start_at_zero

    def convert_to_datetime(self, dates, fmt='%Y%m%d'):
        """
        Convert list of dates to a list of dates with datetime type.

        Parameters
        -----------
        dates : list
            List of dates
        fmt : str
            Format type of each date
        """
        return [dt.datetime.strptime(str(date), fmt) for date in dates]

    def double_logistic(self, X, kind='cubic'):
        """
        Generate a double logistic curve similar to those of the MODIS phenology product.
        
        Parameters
        ------------
        X : array_like
            A N-D array of real values. The length of y along the interpolation axis must be equal to the length of dates.
        kind : str, default 'linear'
            Specifies the kind of interpolation as a string ('linear', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'previous', 'next', where 'zero', 'slinear', 'quadratic' and 'cubic' refer to a spline interpolation of zeroth, first, second or third order; 'previous' and 'next' simply return the previous or next value of the point) or as an integer specifying the order of the spline interpolator to use. Default is 'linear'.

        """
        x = self._get_empty_output_array(X)
        X = self._resize_if_flatten(X)
        if X.ndim == 2:    
            if X.shape[-1] != self.output_dates_int:
                X = self.interpolation(X,kind=kind)
        else:
            raise ValueError('X array must be of shape [2,-1].')
        print(X)
        
        params = np.asarray([1.0, 0.0, 75.0, 8.0, 250.0, 1.0])+ 10*np.random.rand(6)
        
        for n_row in range(X.shape[0]):
            
            solver = fun_dl.minimize(fun_dl.cost_function,
                              params,
                              args=(np.asarray(self.output_dates_int), X[n_row,:]),
                              method='L-BFGS-B',
                              jac=fun_dl.cost_function_grad,
                              options={'gtol': 1e-10,
                                       'ftol': 1e-10,
                                       'maxiter':1000,
                                       'maxcor':1000,
                                       'maxfun':1000})
        
            # Show estimated function
            x[n_row,:] = fun_dl.double_logistique(solver.x, np.asarray(self.output_dates_int))
    
        return x
        
    def interpolation(self, X, kind='linear', **params):
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
        x = self._get_empty_output_array(X)
        X = self._resize_if_flatten(X)
        for in_band, out_band in self._get_time_series_position_per_band(X):
            tmp = interpolate.interp1d(
                self.init_dates_int, X[:, in_band], kind=kind, **params)
            tmp = self._resize_if_flatten(tmp(self.output_dates_int))
            x[:, out_band] = tmp
        return (x)

    def savitzski_golay(self, X, window_length=3, polyorder=1, interpolation_params={}, **params):
        """
        Savitzski golay 
        Based on :class:`scipy.signal.savgol_filter`

        References
        ----------
        :class:`scipy.signal.savgol_filter`
        """
        x = self._get_empty_output_array(X)
        X = self._resize_if_flatten(X)
        for in_band, out_band in self._get_time_series_position_per_band(X):
            tmp = interpolate.interp1d(
                self.init_dates_int, X[:, in_band], **interpolation_params)
            x[:, out_band] = self._resize_if_flatten(signal.savgol_filter(
                tmp(self.output_dates_int), window_length, polyorder, **params))
        return x


def generate_temporal_sampling(start_date, last_date, day_interval=5, save_csv=False, fmt='%Y%m%d'):
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

    custom_acquisition_dates = [start_date.strftime('%Y%m%d')]
    newDate = start_date
    while newDate < last_date:
        newDate = newDate + dt.timedelta(day_interval)
        custom_acquisition_dates.append(newDate.strftime('%Y%m%d'))

    if save_csv:
        np.savetxt(save_csv, np.asarray(
            custom_acquisition_dates, dtype=np.int), fmt='%d')
    else:
        return np.asarray(custom_acquisition_dates, dtype=np.int)
