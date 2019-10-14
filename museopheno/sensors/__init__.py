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
The :mod:`museopheno.sensors` module gathers sensors to ease index and time series computation.
`MuseoPheno`.
"""
import glob
import numpy as np
import gdal
from museotoolbox.raster_tools import rasterMath as _rasterMath
from ..time_series import _areBandsAvailables, expressionManager


class sensorManager:
    """
    Manage sensor in order to produce temporal index and metadata.

    Parameters
    -----------
    sensor_name : str
        ex : 'Sentinel2'
    band_order : list
        list on how band are ordered (e.g. ['2','3','4','8'])
    band_name : list
        list on band names (e.g. ['Blue','Green','Red','NIR']). Used to setraster metadata.
    wavelengths : list
        list on wavelenghts (e.g. [490,560,665,842]). Used to set raster metadata.

    Example
    --------
    >>> modis = sensorManager(band_order=['1','2'],wavelengths=['620-670','841-876'])
    >>> modis.addIndex('FirstBandRatio',expression='B1/(B1+B2)',condition='(B1+B2)!=0')
    """

    def __init__(self, band_order,
                 band_name=False, wavelengths=False):
        self.band_name = band_name
        self.band_order = band_order
        self.n_bands = len(self.band_order)
        self.wavelengths = wavelengths
        self.available_index = dict()

        self.configureBandsOrder()  # useless for now

    def configureBandsOrder(self, order_by='date'):
        """
        Configure how bands are ordered (by date or by band)

        Parameters
        -----------
        order_by : str, default 'date'.
            if 'date', means your raster is stacked in this way : B1, B2 to Bx for the first date, then B1,B2 to Bx for the second date...
            if 'band', means your raster is stacked in this way : B1 first date, B1 second date... to B1 last date, then B2 first date...
        """
        if not order_by.lower() in ['date', 'band']:
            raise ValueError(
                'Sorry, but MuseoPheno only manages raster organized by date or band')

        self.order_by = order_by

    def __checkIndexExist(self, index_name):
        if index_name not in self.available_index.keys():
            raise ValueError(
                str(index_name) +
                ' is not an available index. Please select one of them : ' +
                ', '.join(
                    self.available_index.keys()))
        else:
            return True

    def getIndexExpression(self, index_name):
        """
        Return index expression

        Parameters
        -----------
        index_name : str, mandatory

        Example
        --------
        >>> getIndexExpression('NDVI')
        {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
        """
        if self.__checkIndexExist(index_name):
            return self.available_index[index_name]

    def addIndex(self, index_name, expression,
                 condition=False, compulsory=True):
        """
        Add index for the current sensor, verify if band is available before adding the script.

        Parameters
        -----------
        index_name : str
            name of the index
        expression : str
            When calling a band, start with B (e.g. 'B8/B3+0.5')
        condition : str
            Condition to respect when computing the index (e.g. 'B3!=0')
        compulsory : boolean, default True.
            If compulsory, will return an error if band is not available with the current sensor.

        Example
        --------
        >>> addIndex('NBR',expression='(B08 - B12) / (B08 + B12)',condition='(B08+B12)!=0')
        >>> dataset.getIndexExpression('NBR')
        {'expression': '(B08 - B12) / (B08 + B12)', 'condition': '(B08+B12)!=0'}
        """
        if _areBandsAvailables(
                self.band_order, expression, compulsory=compulsory):
            self.available_index[index_name] = dict(expression=expression)
            if condition:
                self.available_index[index_name]['condition'] = condition

    def _addEachBandAsIndex(self):
        for band in self.band_order:
            self.available_index['B' +
                                 str(band)] = dict(expression='B' + str(band))

    def generateIndex(self, X, expression, interpolate_nan=True,
                      divide_X_by=1, multiply_by=1, dtype=np.float32):
        """
        Generate index from array

        Parameters
        -----------
        X : array
            array where each line is a pixel.
        expression : str or dict
            If str, contains only the expression (e.g. 'B8/B2')
            If dict, please generate it from addIndex function.
        inteprolate_nan : boolean, default True
            If nan value a linear interpolation is done.
        divide_X_by : integer or float, default 1
            Value to divide X before computing the index
        multiply_by : integer or float, default 1.
            Value to multiply the result (e.g. 100 to set the NDVI between -100 and 100)
        dtype : numpy dtype, default np.float32
            dtype of the output (e.g. np.int16 to store the NDVI in integer value)

        Example
        --------
        >>> generateIndex(X,expression='B8/B2')
        """
        X_ = expressionManager(
            X,
            self.band_order,
            expression=expression,
            interpolate_nan=interpolate_nan,
            dtype=dtype,
            multiply_by=multiply_by,
            order_by=self.order_by)
        return X_

    def generateRaster(self, input_raster, output_raster, expression,
                       interpolate_nan=True, divide_X_by=1, multiply_by=1, dtype=np.float32):
        """
        Generate index from raster

        Parameters
        -----------
        intput_raster : path
            path of the raster file.
        output_raster : path
            path to save the raster file. (e.g. '/tmp/myIndex.tif')
        expression : str or dict
            If str, contains only the expression (e.g. 'B8/B2')
            If dict, please generate it from addIndex function.
        inteprolate_nan : boolean, default True
            If nan value a linear interpolation is done.
        divide_X_by : integer or float, default 1
            Value to divide X before computing the index
        multiply_by : integer or float, default 1.
            Value to multiply the result (e.g. 100 to set the NDVI between -100 and 100)
        dtype : numpy dtype, default np.float32
            dtype of the output (e.g. np.int16 to store the NDVI in integer value)

        Example
        --------
        >>> generateRaster(raster,'/tmp/myIndex.tif',expression='B8/B2')
        """
        rM = _rasterMath(input_raster, message='Computing index')
        rM.addFunction(
            expressionManager,
            output_raster,
            outNumpyDT=dtype,
            band_order=self.band_order,
            expression=expression,
            interpolate_nan=interpolate_nan,
            multiply_by=multiply_by,
            order_by=self.order_by)
        rM.run()

    def setDescriptionMetadata(self, input_raster, dates):
        """
        Write metadata (band and date) in raster.

        Parameters
        -----------
        input_raster : str.
            Path of the raster to write in the metadata each band number and date.
        dates : list.
            list of each date :
                - If integer, use YYYYMMDD (e.g. 20181225).
                - If str, use YYYY-MM-DD (e.g. '2018-12-25').

        Example
        ---------
        >>> setDescriptionMetadata(raster,[20180429,20180513,20180708,20180815,20180915,20181015,20181115])

        References
        -----------
        https://raster-timeseries-manager.readthedocs.io/en/latest/content.html#data-format
        """
        ds = gdal.Open(input_raster)

        def convertDateFormat(date):
            if not isinstance(date, str):
                date = str(date)[:4] + '-' + \
                    str(date)[4:6] + '-' + str(date)[6:]

            return date

        for idx, band in enumerate(self.band_order):
            for date in range(len(dates)):
                if self.order_by == 'date':
                    band_pos = (idx+1) + (len(self.band_order) * date)
                elif self.order_by == 'band':
                    band_pos = int(idx*(len(dates))+date)+1
                ds.GetRasterBand(band_pos).SetDescription(
                    convertDateFormat(dates[date]) + ' - ' + band)
        if self.band_name:
            ds.SetMetadataItem(
                'names',
                '{' +
                ', '.join(
                    self.band_name) +
                '}',
                'TIMESERIES')
        if self.wavelengths:
            ds.SetMetadataItem(
                'wavelength',
                '{' +
                ', '.join(
                    str(x) for x in self.wavelengths) +
                '}',
                'TIMESERIES')

        ds.SetMetadataItem(
            'dates',
            '{' +
            ', '.join(
                convertDateFormat(date) for date in dates) +
            '}',
            'TIMESERIES')

        ds.FlushCache()
        ds = None


class Sentinel2(sensorManager):
    """
    Use Sentinel2 as sensor via :class:`museopheno.sensors.sensorManager`.


    Parameters
    -----------
    n_bands : int, default 4
        4 or 10.
    band_order : str or list, default 'default'
        If 'default', band_order is the first 10m-bands (2,3,4 and 8), and if n_bands is 10 bands, the first 20-m bands (5,6,...11,12)

    Example
    --------
    >>> dataset = Sentinel2(n_bands=10)
    >>> dataset.band_name
    ['Blue',
     'Green',
     'Red',
     'NIR',
     'Vegetation Red Edge 1',
     'Vegetation Red Edge 2',
     'Vegetation Red Edge 3',
     'Vegetation Red Edge 4',
     'SWIR1',
     'SWIR2']
    >>> dataset.getIndexExpression('NDVI')
    {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
    """

    def __init__(self, n_bands=4, band_order='default'):

        self.n_bands = n_bands

        self.band_order = band_order
        if self.band_order == 'default':
            if self.n_bands == 4:
                self.band_order = np.array(['2', '3', '4', '8'])
            elif self.n_bands == 10:
                self.band_order = np.array(
                    ['2', '3', '4', '8', '5', '6', '7', '8A', '11', '12'])
            else:
                raise ValueError(
                    'If your Sentinel-2 raster has not 4 or 10 bands, please define band_order parameter.')

        super().__init__(self.band_order)

        self.wavelengths = [490, 560, 665, 842, 705, 740,
                            783, 865, 945, 1610, 2190][:self.n_bands]
        self.band_name = ['Blue',
                          'Green',
                          'Red',
                          'NIR',
                          'Vegetation Red Edge 1',
                          'Vegetation Red Edge 2',
                          'Vegetation Red Edge 3',
                          'Vegetation Red Edge 4',
                          'SWIR1',
                          'SWIR2'][:self.n_bands]

        index = dict(
            ACORVI=['( B8 - B4 + 0.05 ) / ( B8 + B4 + 0.05 ) ',
                    '(B8+B4+0.05) != 0'],
            ACORVInarrow=[
                '( B8A - B4 + 0.05 ) / ( B8A + B4 + 0.05 ) ',
                '(B8A+B4+0.05) != 0'],
            SAVI=['1.5 * (B8 - B4) / ( B8 + B4 + 0.5 )'],
            EVI=['( 2.5 * ( B8 - B4 ) ) / ( ( B8 + 6 * B4 - 7.5 * B2 ) + 1 )'],
            EVI2=[
                '( 2.5 * (B8 - B4) ) / (B8 + 2.4 * B4 + 1) ',
                'B8+2.4*B4+1 != 0'],
            PSRI=['( (B4 - B2) / B5 )', 'B5 != 0'],
            ARI=[
                '( 1 / B3 ) - ( 1 / B5 )',
                'np.logical_and(B3 != 0, B5 != 0)'],
            ARI2=[
                '( B8 / B2 ) - ( B8 / B3 )',
                ' np.logical_and(B2 != 0, B3 != 0)'],
            MARI=['( (B5 - B5 ) - 0.2 * (B5 - B3) ) * (B5 / B4)', 'B4 != 0'],
            CHLRE=['np.power(B5 / B7,-1.0)', 'B5!=0'],
            MCARI=[
                ' ( ( B5 - B4 ) - 0.2 * ( B5 - B3 ) ) * ( B5 / B4 )',
                'B4 != 0'],
            MSI=['B11 / B8', 'B8 != 0'],
            MSIB12=['B12 / B8', 'B8 != 0'],
            NDrededgeSWIR=['( B6 - B12 ) / ( B6 + B12 )', '( B6 + B12 ) != 0'],
            SIPI2=['( B8 - B3 ) / ( B8 - B4 )', 'B8 - B4 != 0'],
            NDWI=['(B8-B11)/(B8+B11)', '(B8+B11) != 0'],
            LCaroC=['B7 / ( B2-B5 )', '( B7 ) != 0'],
            LChloC=['B7 / B5', 'B5 != 0'],
            LAnthoC=['B7 / (B3 - B5) ', '( B3-B5 ) !=0'],
            Chlogreen=['B8A / (B3 + B5)'],
            NDVI=['(B8-B4)/(B8+B4)', '(B8+B4) != 0'],
            NDVInarrow=['(B8A-B4)/(B8A+B4)', '(B8A+B4) != 0'],
            NDVIre=['(B8A-B5)/(B8A+B5)', '(B8A+B5) != 0'],
            RededgePeakArea=['B4+B5+B6+B7+B8A'],
            Rratio=['B4/(B2+B3+B4)'],
            MTCI=['(B6 - B5)/(B5 - B4)', '(B5-B4) != 0'],
            S2REP=['35 * ((((B7 + B4)/2) - B5)/(B6 - B5))'],
            IRECI=['(B7-B4)/(B5/B6)', 'np.logical_and(B5 != 0, B6 != 0)'],
            NBR=['(B08 - B12) / (B08 + B12)', '(B08+B12)!=0']
        )

        for idx in index.keys():
            if len(index[idx]) == 1:
                self.addIndex(idx, index[idx], compulsory=False)
            else:
                self.addIndex(
                    idx,
                    index[idx][0],
                    index[idx][1],
                    compulsory=False)

    def generateTemporalSampling(S2_dir, start_date=False, last_date=False, day_interval=5, save_csv=False):
        """
        Generate sample time for gap-filling of Time Series

        Parameters
        -----------
        S2_dir : str
            path of the folder where zip or unzipped S2 tiles are.
        start_date : False str or int, default false.
            If str or int, use %Y%m%d format, e.g. '20180130'.
        end_date : False, str or int, default False.
            If str or int, use %Y%m%d format, e.g. '20181230'.
        day_interval : int, default 5
            The delta days interval from the first acquistion to the last
        save_csv : False or str, default False
            If str, path where the csv file will be saved.
        """
        # =============================================================================
        #     List all subfolders which begins with SENTINEL2
        #     if no last_date and start_date given
        # =============================================================================
        AcquisitionDates = [start_date, last_date]
        if last_date is False or start_date is False:
            S2 = glob.glob(glob.os.path.join(S2_dir, 'SENTINEL2*/'))

            # if no folder, looking for zip files
            if S2 == []:
                S2 = glob.glob(glob.os.path.join(S2_dir, 'SENTINEL2*.zip'))

            else:
                S2 = [glob.os.path.basename(glob.os.path.dirname(S2Folder))
                      for S2Folder in S2]

            # ==========================================================================
            #     Detecting YYYYMMDD date format
            # ==========================================================================

            import re
            regexYYYYMMDD = r"(?<!\d)(?:(?:20\d{2})(?:(?:(?:0[13578]|1[02])31)|(?:(?:0[1,3-9]|1[0-2])(?:29|30)))|(?:(?:20(?:0[48]|[2468][048]|[13579][26]))0229)|(?:20\d{2})(?:(?:0?[1-9])|(?:1[0-2]))(?:0?[1-9]|1\d|2[0-8]))(?!\d)"
            p = re.compile(regexYYYYMMDD)

            AcquisitionDates = sorted(
                [p.findall(S2folder)[0] for S2folder in S2])

        if start_date is False:
            start_date = AcquisitionDates[0]
        if last_date is False:
            last_date = AcquisitionDates[-1]

        from museopheno.time_series import generateTemporalSampling

        return generateTemporalSampling(AcquisitionDates[0], AcquisitionDates[-1], day_interval=day_interval, save_csv=save_csv)

    def computeSITS(self, S2dir, out_SITS, resample_CSV=False, interpolation='linear', unzip=False,
                    out_cloudMask=False, check_outlier=False, use_flatreflectance=True, n_jobs=1, ram=4000):
        """
        Compute Satellite Image Time Series from Sentinel2 level 2A.
        This script has only been tested on Theia distributed images.

        You can also use the following command line : `museopheno.computeS2SITS`.

        Parameters
        ----------
        S2Dir : Directory
            Directory where zip files from THEIA L2A are unzipped, or zipped.
        out_SITS : Output raster
            Output name of your raster (tif format, int16)
        resample_20mbands : boolean, default True
            If True, resample the six 20m band at 10m.
            If False, use only the four 10m bands.
        interpolation : str, default 'linear'
            Two choices : 'linear' or 'spline'
        unzip : Bool, default False.
            If True, unzip only mandatory images, plus xml and jpg thumbnails.
        out_cloudMask : False or str.
            If False, cloud mask won't be saved.
            Else, path of the output raster file.
        check_outliers : bool, default True.
            If True, check outliers (values below 0 in red band are considered as invalid).
        use_flatreflectance ; boolean, default True
            If False, ou Surface Reflectance (SRE)
        n_jobs : int, default 1.
            Number of cores used.
        ram : int, default 2048
            Available ram in mb.


        References
        -----------

        - For the gap-filling, see https://zenodo.org/record/45572#.XaBjs3UzaV4
        - For the level 2A images, see https://theia.cnes.fr/atdistrib/rocket/

        """
        from __computeS2SITS import computeSITS
        if self.n_bands == 4:
            resample_20mbands = False
        else:
            resample_20mbands = True
        computeSITS(
            S2dir,
            out_SITS,
            resample_20mbands,
            resample_CSV,
            interpolation,
            unzip,
            out_cloudMask,
            check_outlier,
            use_flatreflectance,
            n_jobs,
            ram)


class Formosat2(sensorManager):
    """
    Use Formosat2 as sensor.

    Parameters
    -----------
    n_bands : int, default 4

    band_order : str or list, default 'default'
        If 'default', band_order is the first 10m-bands (2,3,4 and 8), and if n_bands is 10 bands, the first 20-m bands (5,6,...11,12)

    Example
    --------
    >>> dataset = Sentinel2(n_bands=10)
    >>> dataset.band_name
    ['Blue',
     'Green',
     'Red',
     'NIR',
     'Vegetation Red Edge 1',
     'Vegetation Red Edge 2',
     'Vegetation Red Edge 3',
     'Vegetation Red Edge 4',
     'SWIR1',
     'SWIR2']
    >>> dataset.getIndexExpression('NDVI')
    {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
    >>>
    """

    def __init__(self, n_bands=4, band_order='default'):

        self.n_bands = n_bands
        self.band_order = band_order

        if band_order == 'default':
            if self.n_bands == 4:
                self.band_order = np.array(['1', '2', '3', '4'])
            else:
                raise ValueError(
                    'If your FormoSat2 raster has not 4 bands, please define band_order parameter.')
            super().__init__(band_order)

            self.wavelengths = [470, 565, 660, 830]
            self.band_name = ['Blue', 'Green', 'Red', 'NIR']
        else:
            super().__init__('FormoSat2', n_bands, band_order)

        index = dict(ACORVI=['( B4 - B3 + 0.05 ) / ( B4 + B3 + 0.05 ) ', '(B4+B3+0.05) != 0'],
                     SAVI=['1.5 * (B4 - B3) / ( B4 + B3 + 0.5 )'],
                     EVI=[
            '( 2.5 * ( B4 - B3 ) ) / ( ( B4 + 6 * B3 - 7.5 * B1 ) + 1 )'],
            EVI2=['( 2.5 * (B4 - B3) ) / (B4 + 2.4 * B3 + 1) ',
                  'B4+2.4*B3+1 != 0'],
            ARI2=['( B4 / B1 ) - ( B4 / B2 )',
                  ' np.logical_and(B1 != 0, B2 != 0)'],
            NDVI=['(B4-B3)/(B4+B3)', '(B4+B3) != 0'],
            Rratio=['B3/(B1+B2+B3)'])

        for idx in index.keys():
            if len(index[idx]) == 1:
                self.addIndex(idx, index[idx], compulsory=False)
            else:
                self.addIndex(
                    idx,
                    index[idx][0],
                    index[idx][1],
                    compulsory=False)
