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

import re
import numpy as np
np.seterr(divide='ignore')


def __convertBandToArrayIdx(X, expression, n_comp,
                            date, band_order, condition=False, nodata=-9999):
    X = np.copy(X)
#    bandsToChange = re.findall('B[0-9]*',str(expression))
    bandsToChange = re.findall('B[0-9]*[A-Z]*', str(expression))
    out = np.zeros(X[:, 0].shape)
    out[:] = nodata

    for band in set(bandsToChange):
        originalBand = band[1:]  # to remove B
        while originalBand[0] == '0':
            originalBand = originalBand[1:]
        bandIdx = np.where(np.in1d(band_order, originalBand) == True)[0]
        newBand = n_comp * (date) + (bandIdx)
        if condition:
            condition = condition.replace(band, "X[:,{}]".format(newBand))
        expression = expression.replace(band, "X[:,{}]" .format(newBand))

    if condition:
        TF = eval(condition).flatten()
        out[TF] = eval(expression)[TF].flatten()
    else:
        out = eval(expression)
    return out.flatten()


def areBandsAvailables(band_order, expression, compulsory=True):
    """
    Check if band needed for expression are available

    Parameters
    -----------
    band_order : list
        list of bands (e.g. ['2','3','4','8'])
    expression : str
        expression (e.g. 'B08/B02*100')

    Examples
    ---------
    >>> indices.areBandsAvailables(['2','3','4','8'],'B08/B02*100')
    True
    >>> indices.areBandsAvailables(['2','3','4','8'],'B8A/B04*100')
    ValueError: Band ['B8A'] is missing.
    """
    bandsToChange = re.findall('B[0-9]*[A-Z]*', str(expression))
    band_order_withoutB = []
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


def generateIndice(X, band_order, expression, interpolate_nan=True,
                   divide_X_by=1, multiply_by=1, dtype=np.float32):
    """
    Generate indice from an array according to a band_order, and expression.

    The easiest way to use it is to choose a sensor from :class:`museopheno.sensors`.

    Parameters
    ----------
    X : array
        array where each line is a pixel.
    band_order : list
        list of band order (e.g. ['2','3','4','8'])
    expression : str or dict
        If str, contains only the expression (e.g. 'B8/B2')
        If dict, contains a expression key and can contain a condition key.
        See `museopheno.sensors.sensorManager.addIndice` function.
    inteprolate_nan : boolean, default True
        If nan value a linear interpolation is done.
    divide_X_by : integer or float, default 1
        Value to divide X before computing the indice
    multiply_by : integer or float, default 1.
        Value to multiply the result (e.g. 100 to set the NDVI between -100 and 100)
    dtype : numpy dtype, default np.float32
        dtype of the output (e.g. np.int16 to store the NDVI in integer value)

    Example
    --------
    >>> from museopheno import indices,datasets
    >>> X = datasets.Sentinel2_3a_2018(get_only_sample=True)
    >>> indices.generateIndice(X,band_order=['2','3','4','8','5','6','7','8A','11','12'],expression='B4/B8')


    """

    def __nan_helper(y):
        return np.isnan(y), lambda z: z.nonzero()[0]

    if X.ndim == 1:
        X = X.reshape(1, -1)
    X = X / divide_X_by

    nDates = X.shape[1] / len(band_order)
    if nDates != int(X.shape[1] / len(band_order)):
        raise ValueError(
            'band_order is not a multiple of the number of columns of your array which contains {} bands.'.format(
                X.shape[1]))
    else:
        n_comp = int(X.shape[1] / nDates)
        nDates = int(nDates)

    outIndice = np.zeros((X.shape[0], nDates), dtype=np.float64)

    if areBandsAvailables(band_order, expression):
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
            dateIndice = __convertBandToArrayIdx(
                X, mathExp, n_comp, date, band_order, condition=condition)
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
                nans, x = __nan_helper(outIndice[i, :])
                if not np.all(nans == False):
                    outIndice[i, nans] = np.interp(
                        x(nans), x(~nans), outIndice[i, ~nans])
        if multiply_by != 1:
            outIndice *= multiply_by

        if dtype:
            outIndice = outIndice.astype(dtype)

        return outIndice
