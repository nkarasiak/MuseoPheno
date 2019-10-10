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


def Sentinel2_3a_2018():
    """
    Parameters
    -----------
    return_dates : bool, default False.
        If True, will return list of dates.
    
    Returns
    -------
    raster : str.
        Return path of raster.


    Examples
    --------
    >>> raster = Sentinel2_3a_2018()
    >>> print(raster)
    /mnt/DATA/lib/MuseoPheno/museopheno/datasets/2018_3A_Theia_Bouconne.tif
    """
    raster = os.path.join(__pathFile, '2018_3A_Theia_Bouconne.tif')
	
    return raster
