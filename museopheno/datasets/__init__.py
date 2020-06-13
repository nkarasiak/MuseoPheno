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
The :mod:`museopheno.datasets` module gathers available datasets for testing
`MuseoPheno`.
"""

import os
__pathFile = os.path.dirname(os.path.realpath(__file__))


def Sentinel2_3a_2018(return_dates=False, return_random_sample=False):
    """
    Sentinel2 sample dataset on Bouconne Forest (France, near Toulouse).
    Bands are ordered this way : '2','3','4','8','5','6','7','8','8A','11','12'.

    Parameters
    -----------
    return_dates : bool, default False
        If True, will return list of dates.
    return_random_sample : bool, default False
        If False, will return the path of the raster
        If True, will return a random block of the image

    Returns
    -------
    raster : str or array
        If get_only_sample is False, returns path of raster.
        If get_only_sample is True, returns array where each line is a pixel.
    dates : list
        List of integer


    Examples
    --------
    >>> raster,dates = Sentinel2_3a_2018(return_dates=True)
    >>> print(raster)
    /mnt/bigone/lib/MuseoPheno/museopheno/datasets/2018_3A_Theia_Bouconne.tif
    >>> print(dates)
    [20180429, 20180513, 20180708, 20180815, 20180915, 20181015, 20181115]
    >>> Sentinel2_3a_2018(get_only_sample=True)
    Total number of blocks : 246
    array([[ 122,  320,  109, ..., 2107, 1530,  751],
       [ 140,  370,  122, ..., 2107, 1530,  751],
       [ 148,  388,  117, ..., 2102, 1557,  761],
       ...,
       [ 167,  459,  195, ..., 2251, 1482,  664],
       [ 154,  470,  185, ..., 2251, 1482,  664],
       [ 184,  494,  213, ..., 2429, 1507,  670]], dtype=int16)

    References
    -----------
    This dataset is built using level 3A Sentinel-2 month syntheses :
    https://labo.obs-mip.fr/multitemp/sentinel-2-level-3a-products-syntheses-of-composites/
    """

    raster = os.path.join(__pathFile, '2018_3A_Theia_Bouconne.tif')
    dates = [
        20180429,
        20180513,
        20180708,
        20180815,
        20180915,
        20181015,
        20181115]
    if return_random_sample is True:
        from museotoolbox.processing import RasterMath
        raster = RasterMath(raster).get_random_block()
    if return_dates:
        return raster, dates
    else:
        return raster
