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
import collections
from museotoolbox.processing import RasterMath as _RasterMath
from ..time_series import _are_bands_availables, ExpressionManager

class SensorManager:
    """
    Manage sensor in order to produce temporal index and metadata.

    Parameters
    -----------
    sensor_name : str
        ex : 'Sentinel2'
    bands_order : list
        list on how band are ordered (e.g. ['2','3','4','8'])
    bands_names : list
        list on band names (e.g. ['Blue','Green','Red','NIR']). Used to setraster metadata.
    wavelengths : list
        list on wavelenghts (e.g. [490,560,665,842]). Used to set raster metadata.

    Example
    --------
    >>> modis = SensorManager(bands_order=['1','2'],wavelengths=['620-670','841-876'])
    >>> modis.add_index('FirstBandRatio',expression='B1/(B1+B2)',condition='(B1+B2)!=0')
    """

    def __init__(self, bands_order,
                 bands_names=False, wavelengths=False):
        
        self.bands_names = bands_names
        self.bands_order = bands_order
        
        self.n_bands = len(self.bands_order)
        self.wavelengths = wavelengths
        self.available_indices = dict()
        
        self._add_each_band_as_index()
        
        self.configure_bands_order()  # useless for now

    def configure_bands_order(self, order_by='date'):
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

    def _check_index_exists(self, index_name):
        if index_name not in self.available_indices.keys():
            raise ValueError(
                str(index_name) +
                ' is not an available index. Please select one of them : ' +
                ', '.join(
                    self.available_indices.keys()))
        else:
            return True

    def get_index_expression(self, index_name):
        """
        Return index expression

        Parameters
        -----------
        index_name : str, mandatory

        Example
        --------
        >>> get_index_expression('NDVI')
        {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
        """
        if self._check_index_exists(index_name):
            return self.available_indices[index_name]

    def SmoothSignal(self,input_dates,output_dates=False,fmt='%Y%m%d'):
        from museopheno.time_series import SmoothSignal
        return SmoothSignal(dates=input_dates,output_dates=output_dates, bands_order=self.bands_order, fmt=fmt)
    
    def add_index(self, index_name, expression,
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
        >>> add_index('NBR',expression='(B08 - B12) / (B08 + B12)',condition='(B08+B12)!=0')
        >>> dataset.get_index_expression('NBR')
        {'expression': '(B08 - B12) / (B08 + B12)', 'condition': '(B08+B12)!=0'}
        """
        if _are_bands_availables(
                self.bands_order, expression, compulsory=compulsory):
            self.available_indices[index_name] = dict(expression=expression)
            if condition:
                self.available_indices[index_name]['condition'] = condition

    def _add_each_band_as_index(self):
        for band in self.bands_order:
            self.available_indices['B' +
                                 str(band)] = dict(expression='B' + str(band))

    def generate_index(self, X, expression, interpolate_nan=True,
                      divide_X_by=1, multiply_by=1, dtype=np.float32):
        """
        Generate index from array

        Parameters
        -----------
        X : array
            array where each line is a pixel.
        expression : str or dict
            If str, contains only the expression (e.g. 'B8/B2')
            If dict, please generate it from add_index function.
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
        >>> generate_index(X,expression='B8/B2')
        """
        X_ = ExpressionManager(
            X,
            self.bands_order,
            expression=expression,
            interpolate_nan=interpolate_nan,
            dtype=dtype,
            multiply_by=multiply_by,
            order_by=self.order_by)
        return X_

    def generate_raster(self, input_raster, output_raster, expression,
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
            If dict, please generate it from add_index function.
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
        >>> generateRaster(raster,'/tmp/my_index.tif',expression='B8/B2')
        """
        rM = _RasterMath(input_raster, message='Computing index')
        rM.add_function(
            ExpressionManager,
            output_raster,
            dtype=dtype,
            bands_order=self.bands_order,
            expression=expression,
            interpolate_nan=interpolate_nan,
            multiply_by=multiply_by,
            order_by=self.order_by)
        rM.run()

    def set_description_metadata(self, input_raster, dates):
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

        def convert_date_format(date):
            if not isinstance(date, str):
                date = str(date)[:4] + '-' + \
                    str(date)[4:6] + '-' + str(date)[6:]

            return date

        for idx, band in enumerate(self.bands_order):
            for date in range(len(dates)):
                if self.order_by == 'date':
                    band_pos = (idx+1) + (len(self.bands_order) * date)
                elif self.order_by == 'band':
                    band_pos = int(idx*(len(dates))+date)+1
                ds.GetRasterBand(band_pos).SetDescription(
                    convert_date_format(dates[date]) + ' - ' + band)
        if self.bands_names is not False:
            ds.SetMetadataItem(
                'names',
                '{' +
                ', '.join(
                    self.bands_names) +
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
                convert_date_format(date) for date in dates) +
            '}',
            'TIMESERIES')

        ds.FlushCache()
        ds = None


class Sentinel2(SensorManager):
    """
    Use Sentinel2 as sensor via :class:`museopheno.sensors.sensorManager`.


    Parameters
    -----------
    n_bands : int, default 4
        4 or 10.
    bands_order : str or list, default 'default'
        If 'default', bands_order is the first 10m-bands (2,3,4 and 8), and if n_bands is 10 bands, the first 20-m bands (5,6,...11,12)

    Example
    --------
    >>> dataset = Sentinel2(n_bands=10)
    >>> dataset.bands_names
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
    >>> dataset.get_index_expression('NDVI')
    {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
    """

    def __init__(self, n_bands=10, bands_order='default'):

        self.n_bands = n_bands

        self.bands_order = bands_order
        if not isinstance(self.bands_order, np.ndarray) and self.bands_order == 'default':
            if self.n_bands == 4:
                self.bands_order = np.array(['2', '3', '4', '8'])
            elif self.n_bands == 10:
                self.bands_order = np.array(
                    ['2', '3', '4', '8', '5', '6', '7', '8A', '11', '12'])
            else:
                raise ValueError(
                    'If your Sentinel-2 raster has not 4 or 10 bands, please define bands_order parameter.')

        super().__init__(self.bands_order)

        self.wavelenghts = np.array([443, 490, 560, 665, 842, 705, 740,
                            783, 865, 945, 1375, 1610, 2190])
        
        self._bands  = np.array(['1','2', '3', '4', '8', '5', '6', '7', '8A', '9', '10', '11', '12'])
        
        self._bands_idx = np.isin(self._bands,self.bands_order)
    
        self.wavelenghts = self.wavelenghts[self._bands_idx]
        
        self.bands_names = np.array(['Coastal aerosol',
                           'Blue',
                          'Green',
                          'Red',
                          'NIR',
                          'Vegetation Red Edge 1',
                          'Vegetation Red Edge 2',
                          'Vegetation Red Edge 3',
                          'Vegetation Red Edge 4',
                          'Water vapour',
                          'SWIR - Cirrus',
                          'SWIR1',
                          'SWIR2'])
        self.bands_names = self.bands_names[self._bands_idx]
        
        del self._bands,self._bands_idx
        
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
            NBR=['(B08 - B12) / (B08 + B12)', '(B08+B12)!=0'],
            REP=['700 + 40 * (( ( B4 + B7 ) / B2) -5) / ( B6 - B5 ) ']
        )

        for idx in index.keys():
            if len(index[idx]) == 1:
                self.add_index(idx, index[idx], compulsory=False)
            else:
                self.add_index(
                    idx,
                    index[idx][0],
                    index[idx][1],
                    compulsory=False)

    def generate_temporal_sampling(S2_dir, start_date=False, last_date=False, day_interval=5, save_csv=False):
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

        from museopheno.time_series import generate_temporal_sampling

        return generate_temporal_sampling(AcquisitionDates[0], AcquisitionDates[-1], day_interval=day_interval, save_csv=save_csv)

    def compute_SITS(self, S2dir, out_SITS, resample_CSV=False, interpolation='linear', unzip=False,
                    out_cloud_mask=False, check_outlier=False, use_flatreflectance=True, n_jobs=1, ram=4000):
        """
        Compute Satellite Image Time Series from Sentinel2 level 2A.
        This script has only been tested on Theia distributed images.

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
        out_cloud_mask : False or str.
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
        from museopheno.sensors.__computeS2SITS import _computeSITS
        if self.n_bands == 4:
            resample_20mbands = False
        else:
            resample_20mbands = True
        _computeSITS(
            S2dir,
            out_SITS,
            resample_20mbands=resample_20mbands,
            resample_CSV=resample_CSV,
            interpolation=interpolation,
            unzip=unzip,
            onlyROI=False,
            out_cloudMask=out_cloud_mask,
            checkOutliers=check_outlier,
            use_flatreflectance=use_flatreflectance,
            n_jobs=n_jobs,
            ram=ram)


class Formosat2(SensorManager):
    """
    Use Formosat2 as sensor.

    Parameters
    -----------
    n_bands : int, default 4

    bands_order : str or list, default 'default'
        If 'default', bands_order is the first 10m-bands (2,3,4 and 8), and if n_bands is 10 bands, the first 20-m bands (5,6,...11,12)

    Example
    --------
    >>> dataset = Sentinel2(n_bands=10)
    >>> dataset.bands_names
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
    >>> dataset.get_index_expression('NDVI')
    {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
    >>>
    """

    def __init__(self, n_bands=4, bands_order='default'):

        self.n_bands = n_bands
        self.bands_order = bands_order

        if bands_order == 'default':
            if self.n_bands == 4:
                self.bands_order = np.array(['1', '2', '3', '4'])
            else:
                raise ValueError(
                    'If your FormoSat2 raster has not 4 bands, please define bands_order parameter.')
            super().__init__(bands_order)

            self.wavelengths = [470, 565, 660, 830]
            self.bands_names = ['Blue', 'Green', 'Red', 'NIR']
        else:
            super().__init__(n_bands, bands_order)

        indices = dict(ACORVI=['( B4 - B3 + 0.05 ) / ( B4 + B3 + 0.05 ) ', '(B4+B3+0.05) != 0'],
                     SAVI=['1.5 * (B4 - B3) / ( B4 + B3 + 0.5 )'],
                     EVI=[
            '( 2.5 * ( B4 - B3 ) ) / ( ( B4 + 6 * B3 - 7.5 * B1 ) + 1 )'],
            EVI2=['( 2.5 * (B4 - B3) ) / (B4 + 2.4 * B3 + 1) ',
                  'B4+2.4*B3+1 != 0'],
            ARI2=['( B4 / B1 ) - ( B4 / B2 )',
                  ' np.logical_and(B1 != 0, B2 != 0)'],
            NDVI=['(B4-B3)/(B4+B3)', '(B4+B3) != 0'],
            Rratio=['B3/(B1+B2+B3)'])
        
        collections.OrderedDicted(sorted(indices.items()))


        for idx in indices.keys():
            if len(indices[idx]) == 1:
                self.add_index(idx, indices[idx], compulsory=False)
            else:
                self.add_index(
                    idx,
                    indices[idx][0],
                    indices[idx][1],
                    compulsory=False)


class Venus(SensorManager):
    """
    Use Venus as sensor.

    Parameters
    -----------
    n_bands : int, default 12

    bands_order : str or list, default 'default'
        If 'default', bands_order is the first 10m-bands (2,3,4 and 8), and if n_bands is 10 bands, the first 20-m bands (5,6,...11,12)

    Example
    --------
    >>> dataset = Venus()
    >>> dataset.bands_names
    >>> dataset.get_index_expression('NDVI')
    {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
    >>>
    """

    def __init__(self, n_bands=12, bands_order='default'):

        self.n_bands = n_bands
        self.bands_order = bands_order

        if bands_order == 'default':
            if self.n_bands == 4:
                self.bands_order = np.array(['1', '2', '3', '4','5','6','7','8','9','10','11','12'])
            else:
                raise ValueError(
                    'If your FormoSat2 raster has not 4 bands, please define bands_order parameter.')
            super().__init__(bands_order)

            self.wavelengths = [420, 443, 490, 555, 638, 638, 672, 702, 742, 782, 865, 910]
            self.bands_order = ['B'+i for i in self.bands_order]
            
        else:
            super().__init__(n_bands, bands_order)
    

        indices = dict(ACORVI=['( B4 - B3 + 0.05 ) / ( B4 + B3 + 0.05 ) ', '(B4+B3+0.05) != 0'],
                     SAVI=['1.5 * (B4 - B3) / ( B4 + B3 + 0.5 )'],
                     EVI=[
            '( 2.5 * ( B4 - B3 ) ) / ( ( B4 + 6 * B3 - 7.5 * B1 ) + 1 )'],
            EVI2=['( 2.5 * (B4 - B3) ) / (B4 + 2.4 * B3 + 1) ',
                  'B4+2.4*B3+1 != 0'],
            ARI2=['( B4 / B1 ) - ( B4 / B2 )',
                  ' np.logical_and(B1 != 0, B2 != 0)'],
            NDVI=['(B4-B3)/(B4+B3)', '(B4+B3) != 0'],
            Rratio=['B3/(B1+B2+B3)'])
        
        collections.OrderedDicted(sorted(indices.items()))


        for idx in indices.keys():
            if len(indices[idx]) == 1:
                self.add_index(idx, indices[idx], compulsory=False)
            else:
                self.add_index(
                    idx,
                    indices[idx][0],
                    indices[idx][1],
                    compulsory=False)
