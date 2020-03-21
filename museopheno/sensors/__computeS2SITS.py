#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
#  __  __                         _____ _____ _______ _____
# |  \/  |                       / ____|_   _|__   __/ ____|
# | \  / |_   _ ___  ___  ___   | (___   | |    | | | (___
# | |\/| | | | / __|/ _ \/ _ \   \___ \  | |    | |  \___ \
# | |  | | |_| \__ \  __/ (_) |  ____) |_| |_   | |  ____) |
# |_|  |_|\__,_|___/\___|\___/  |_____/|_____|  |_| |_____/
#
# @author:  Nicolas Karasiak
# @site:    www.karasiak.net
# @git:     www.github.com/nkarasiak/MuseoSITS
# =============================================================================
import os
import numpy as np
import glob

def _computeSITS(
        S2Dir,
        out_SITS=False,
        resample_20mbands=True,
        resample_CSV=False,
        interpolation='linear',
        unzip=False,
        out_cloudMask=None,
        checkOutliers=True,
        onlyROI=False,
        ROIfield=False,
        use_flatreflectance=True,
        n_jobs=1,
        ram=2048):
    """
    Compute Satellite Image Time Series from Sentinel-2 A/B.

    Parameters
    ----------
    S2Dir : Directory
        Directory where zip files from THEIA L2A are unzipped, or zipped.
    out_SITS : Output raster
        Output name of your raster (tif format, int16)
    resample_20mbands : boolean, default True
        If True, resample the six 20m band at 10m.
        If False, use only the four 10m bands.
    resampleCSV : str, default False.
        If str, must be csv file with one line per date (YYYYMMDD format, i.e 20180223).
        If False, interpolation is made according to image dates.
    interpolation : str, default 'linear'
        Two choices : 'linear' or 'spline'
    unzip : Bool, default False.
        If True, unzip only mandatory images, plus xml and jpg thumbnails.
    out_cloudMask : False or str.
        If False, cloud mask won't be saved.
        Else, path of the output raster file.
    checkOutliers : bool, default True.
        If True, check outliers (values below 0 in red band are considered as invalid).
    onlyROI : False or str.
        If str, path to the vector files. Will only extract roi in vector file.
    ROIfield : False or str.
        ROIfield is used to save vector files with band raster and columns to avoid raster generation.
    use_flatreflectance ; boolean, default True
        If False, ou Surface Reflectance (SRE)
    n_jobs : int, default 1.
        Number of cores used.
    ram : int, default 2048
        Available ram in mb.


    References
    -----------
    https://zenodo.org/record/45572#.XaBjs3UzaV4
    """
    # OTB Number of threads
    os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = str(n_jobs)

    if use_flatreflectance:
        reflectance_type = 'FRE'
    else:
        reflectance_type = 'SRE'
    
    # =============================================================================
    #     The python module providing access to OTB applications is otbApplication
    # =============================================================================

    try:
        import otbApplication

    except BaseException:
        raise ImportError(
            "You need to have OTB available in python to use OTBPythonBinding")

    # =============================================================================
    #     Initiate variables and make dirs
    # =============================================================================

    if out_SITS:
        outDir = os.path.dirname(out_SITS)
    else:
        import tempfile
        out_SITS = tempfile.mktemp('SITS.tif')
    if onlyROI:
        outDir = os.path.dirname(onlyROI)

    if not os.path.exists(outDir):
        os.makedirs(outDir)

    band10m = ['2', '3', '4', '8']
    band20m = ['5', '6', '7', '8A', '11', '12']

    if resample_20mbands:
        bands = band10m + band20m
    else:
        bands = band10m

    # =============================================================================
    #     unzip only used bands
    # =============================================================================

    if isinstance(unzip, str):
        unzip = unzip
    if unzip:
        print('unzipping used bands')
        if isinstance(S2Dir,str):
            if resample_20mbands:
                formula = "parallel -j " + \
                    str(n_jobs) + " unzip -n {} *" + reflectance_type + "_B?.tif *" + reflectance_type + \
                    "_B??.tif *CLM_R1* *.xml *.jpg -d " + S2Dir + \
                    " ::: " + os.path.join(S2Dir, "*.zip")
            else:
                formula = "parallel -j " + \
                    str(n_jobs) + " unzip -n {} *" + reflectance_type + "_B2*.tif *" + reflectance_type + "_B3*.tif *" + reflectance_type + \
                    "_B4*.tif *" + reflectance_type + "_B8*.tif *CLM_R1* *.xml *.jpg -d " + \
                    S2Dir + " ::: " + os.path.join(S2Dir, "*.zip")
            print('executing : ' + formula)
            os.system(formula)
        else:
            for img in S2Dir:
                if img.endswith('zip'):
                    
                    if resample_20mbands:
                        formula = "parallel -j " + \
                            str(n_jobs) + " unzip -n {} *" + reflectance_type + "_B?.tif *" + reflectance_type + \
                            "_B??.tif *CLM_R1* *.xml *.jpg -d " + os.path.dirname(img)+ '/' + \
                            " ::: " + img
                    else:
                        formula = "parallel -j " + \
                            str(n_jobs) + " unzip -n {} *" + reflectance_type + "_B2*.tif *" + reflectance_type + "_B3*.tif *" + reflectance_type + \
                            "_B4*.tif *" + reflectance_type + "_B8*.tif *CLM_R1* *.xml *.jpg -d " + \
                            os.path.dirname(img)+ '/' + " ::: " + img
                    print('executing : ' + formula)
                    os.system(formula)
        

    # =============================================================================
    #     Get Date for each acquisition and save to sample_time.csv
    # =============================================================================

    if isinstance(S2Dir,str):
        S2 = glob.glob(os.path.join(S2Dir, 'SENTINEL2*/'))
    else:
        if S2Dir[0].endswith('zip'):
            print(S2Dir)
            S2 = [glob.glob(s[:-10]+'*/')[0] for s in S2Dir]
            print(S2)
        else:
            S2 = S2Dir
            print('no zip')
        
 
    import re
    regexYYYYMMDD = r"(?<!\d)(?:(?:20\d{2})(?:(?:(?:0[13578]|1[02])31)|(?:(?:0[1,3-9]|1[0-2])(?:29|30)))|(?:(?:20(?:0[48]|[2468][048]|[13579][26]))0229)|(?:20\d{2})(?:(?:0?[1-9])|(?:1[0-2]))(?:0?[1-9]|1\d|2[0-8]))(?!\d)"
    p = re.compile(regexYYYYMMDD)

    YYYYMMDDstart = p.search(S2[0]).start()
    YYYYMMDDend = p.search(S2[0]).end()

    AcquisitionDates = [p.findall(S2folder)[0] for S2folder in S2]
    AcquisitionDatesCsv = os.path.join(outDir, 'sample_time.csv')
    np.savetxt(
        AcquisitionDatesCsv,
        np.sort(
            np.asarray(
                AcquisitionDates,
                dtype=np.int)),
        fmt='%d')

    # =============================================================================
    #     Order directory according to date
    # =============================================================================
    
    orderedSITS = sorted(S2, key=lambda x: x[YYYYMMDDstart:YYYYMMDDend])
    
    print(orderedSITS)
    # =============================================================================
    #     Building cloud mask
    # =============================================================================

    cloudsToMask = [
        glob.glob(
            os.path.join(
                S2Date,
                'MASKS/*CLM_R1.tif'))[0] for S2Date in orderedSITS]

    appMask = otbApplication.Registry.CreateApplication(
        "ConcatenateImages")
    appMask.SetParameterStringList('il', cloudsToMask)
    if isinstance(out_cloudMask, str):
        appMask.SetParameterString("out", out_cloudMask)
        # appMask.ExecuteAndWriteOutput()

    appMask.Execute()

    # =============================================================================
    #     Building temporary SITS (with 4 bands at 10m, or 10 bands)
    # =============================================================================

    fourBandsToVrt = []

    if resample_20mbands:
        sixBandsToVrt = []
        refBands = []
    for i in orderedSITS:
        for j in band10m:
            fourBandsToVrt.append(
                glob.glob(
                    os.path.join(
                        i, '*' + reflectance_type + '_B{}.tif'.format(j)))[0])
        if resample_20mbands:
            for k in band20m:
                sixBandsToVrt.append(
                    glob.glob(
                        os.path.join(
                            i, '*' + reflectance_type + '_B{}.tif'.format(k)))[0])
                refBands.append(
                    glob.glob(
                        os.path.join(
                            i,
                            '*' +
                            reflectance_type +
                            '_B8.tif'))[0])

    appTempSITS = otbApplication.Registry.CreateApplication(
        "ConcatenateImages")

    appTempSITS.SetParameterStringList('il', fourBandsToVrt)

    appTempSITS.Execute()

    if checkOutliers:
        # =============================================================================
        #             Look for outliers (values below 0, check here in red band, are added in mask)
        # =============================================================================
        removeExp = ''
        for idx in range(1, len(cloudsToMask) + 1):
            removeExp += 'im1b{1} < 0 ? im2b{0} = 1 : im2b{0};'.format(
                idx, idx * 4)
        removeExp = removeExp[:-1]

        appRemoveOutliers = otbApplication.Registry.CreateApplication(
            "BandMathX")
        appRemoveOutliers.AddImageToParameterInputImageList(
            'il', appTempSITS.GetParameterOutputImage("out"))
        appRemoveOutliers.AddImageToParameterInputImageList(
            'il', appMask.GetParameterOutputImage("out"))
        appRemoveOutliers.SetParameterString('exp', removeExp)

        appRemoveOutliers.Execute()

    if resample_20mbands:
        # Concatenate Band 8 as reference
        appReference = otbApplication.Registry.CreateApplication(
            "ConcatenateImages")
        appReference.SetParameterStringList('il', refBands)
        appReference.Execute()
        # Concatenate 20m bands
        appToReproject = otbApplication.Registry.CreateApplication(
            "ConcatenateImages")
        appToReproject.SetParameterStringList('il', sixBandsToVrt)
        appToReproject.Execute()

        # Resample 20m bands at 10m with Band 8
        appResampleCompute = otbApplication.Registry.CreateApplication(
            "Superimpose")

        appResampleCompute.SetParameterInputImage(
            'inr', appReference.GetParameterOutputImage("out"))
        appResampleCompute.SetParameterInputImage(
            'inm', appToReproject.GetParameterOutputImage("out"))

        appResampleCompute.Execute()

        # ===================================================================================
        #   Generate expression to reorder bands as b02,b03,b04,b08,b05,b06,b07,b08a,b11,b12
        # ===================================================================================

        reorderExp = ''
        for idx in range(len(orderedSITS)):
            start10m = idx * 4 + 1
            start20m = idx * 6 + 1

            im1b = ['im1b' + str(i) for i in range(start10m, start10m + 4)]
            im2b = ['im2b' + str(i) for i in range(start20m, start20m + 6)]
            currentExp = ';'.join(str(e) for e in im1b) + \
                ';' + ';'.join(str(e) for e in im2b) + ';'

            reorderExp += currentExp
        reorderExp = str(reorderExp[:-1])
        appConcatenatePerDate = otbApplication.Registry.CreateApplication(
            "BandMathX")
        # first im inpput : temp SITS of the 4 10m bands for each date
        appConcatenatePerDate.AddImageToParameterInputImageList(
            'il', appTempSITS.GetParameterOutputImage("out"))
        # second im inpput : resample 10m SITS of the 6 20m bands for each
        # date
        appConcatenatePerDate.AddImageToParameterInputImageList(
            'il', appResampleCompute.GetParameterOutputImage("out"))
        # ordered as given in reorderExp
        appConcatenatePerDate.SetParameterString('exp', reorderExp)
        appConcatenatePerDate.Execute()

    # =============================================================================
    #     Execute process
    # =============================================================================

    print('Building SITS...')

    app = otbApplication.Registry.CreateApplication(
        "ImageTimeSeriesGapFilling")

    # We print the keys of all its parameter

    if resample_20mbands:
        app.SetParameterInputImage(
            "in", appConcatenatePerDate.GetParameterOutputImage("out"))
    else:
        app.SetParameterInputImage(
            "in", appTempSITS.GetParameterOutputImage("out"))

    if checkOutliers:
        app.SetParameterInputImage(
            "mask", appRemoveOutliers.GetParameterOutputImage("out"))
    else:
        app.SetParameterInputImage(
            "mask", appMask.GetParameterOutputImage("out"))
    app.SetParameterString("out", out_SITS)
    app.SetParameterOutputImagePixelType(
        "out", otbApplication.ImagePixelType_int16)  # int16 = 1
    app.SetParameterString("it", interpolation)
    app.SetParameterString("id", AcquisitionDatesCsv)
    app.SetParameterInt("comp", len(bands))
    app.SetParameterInt("ram", ram)
    if resample_CSV:
        app.SetParameterString("od", resample_CSV)
    else:
        app.SetParameterString("od", AcquisitionDatesCsv)

    if onlyROI is False:
        # writing raster
        app.ExecuteAndWriteOutput()
        appMask.ExecuteAndWriteOutput()

    else:
        print('Extracting values from SITS')
        app.Execute()

        SampleExtraction = otbApplication.Registry.CreateApplication(
            "SampleExtraction")
        # The following lines set all the application parameters:
        SampleExtraction.SetParameterInputImage(
            "in", app.GetParameterOutputImage("out"))
        SampleExtraction.SetParameterString("vec", onlyROI)
        SampleExtraction.SetParameterString("field", ROIfield)
        SampleExtraction.SetParameterString("outfield", "prefix")
        SampleExtraction.SetParameterString("outfield.prefix.name", "band_")

        if out_cloudMask is False:
            SampleExtraction.SetParameterString("out", out_cloudMask)
            SampleExtraction.ExecuteAndWriteOutput()

        else:
            SampleExtraction.Execute()
            CloudExtraction = otbApplication.Registry.CreateApplication(
                "SampleExtraction")
            CloudExtraction.SetParameterInputImage(
                "in", app.GetParameterOutputImage("out"))
            CloudExtraction.SetParameterString("vec", onlyROI)
            CloudExtraction.SetParameterString("field", ROIfield)
            CloudExtraction.SetParameterString("outfield", "prefix")
            CloudExtraction.SetParameterString(
                "outfield.prefix.name", "cloud_")
            CloudExtraction.SetParameterString("out", out_SITS)
            CloudExtraction.ExecuteAndWriteOutput()
# =============================================================================
# 
# 
# def main(argv=None, apply_config=True):
#     if len(sys.argv) == 1:
#         prog = os.path.basename(sys.argv[0])
#         print(sys.argv[0] + ' [options]')
#         print("Help : ", prog, " --help")
#         print("or : ", prog, " -h")
#         print(
#             2 *
#             ' ' +
#             "example 1 : ", prog, " -s2dir /tmp/S2downloads -out /tmp/SITS.tif")
#         print(
#             2 *
#             ' ' +
#             "example 2 : ", prog, " -s2dir /tmp/S2downloads -out /tmp/SITS.tif -interpolation 'spline' -resample20m True -unzip True -n_jobs 4 -ram 4000")
#         sys.exit(-1)
# 
#     else:
#         usage = "usage: %prog [options] "
#         parser = argparse.ArgumentParser(
#             description="Compute Satellite Image Time Series from Sentinel-2 A/B.",
#             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# 
#         parser.add_argument(
#             "-s2dir",
#             "--wd",
#             dest="s2dir",
#             action="store",
#             help="Sentinel-2 L2A Theia directory",
#             required=True)
# 
#         parser.add_argument(
#             "-outSITS",
#             "--out",
#             dest="outSITS",
#             action="store",
#             help="Output name of the Sentinel-2 Image Time Series",
#             required=True,
#             type=str)
# 
#         parser.add_argument(
#             "-resample20m",
#             "--rs",
#             dest="resample20mBands",
#             action="store",
#             help="Resample the 20m bands at 10m for computing 10 bands per date",
#             required=False,
#             type=bool,
#             default=False)
# 
#         parser.add_argument(
#             "-resampleCSV",
#             "--rsCSV",
#             dest="resampleCSV",
#             action="store",
#             help="CSV of output dates",
#             required=False,
#             default=False)
# 
#         parser.add_argument(
#             "-interpolation",
#             '--i',
#             dest='interpolation',
#             action="store",
#             help="Interpolation type : 'linear' or 'spline'",
#             default='linear',
#             required=False,
#             type=str)
# 
#         parser.add_argument(
#             "-unzip",
#             "--u",
#             dest="unzip",
#             action="store",
#             help="Do unzip of S2 images ?",
#             required=False,
#             default=False,
#             type=bool)
# 
#         parser.add_argument(
#             "-checkOutliers",
#             "--c",
#             dest="checkOutliers",
#             action="store",
#             help="If True, will look for outliers (values below 0)",
#             required=False,
#             type=bool,
#             default=False)
# 
#         parser.add_argument(
#             "-n_jobs",
#             "--n",
#             dest="n_jobs",
#             action="store",
#             help="Number of CPU / Threads to use for OTB applications (ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS)",
#             default="1",
#             required=False,
#             type=int)
# 
#         parser.add_argument("-ram", "--r", dest="ram", action="store",
#                             help="RAM for otb applications",
#                             default="2048", required=False, type=int)
# 
#         parser.add_argument(
#             "-cloudMask",
#             '--cm',
#             dest='cloudMask',
#             action="store",
#             help="Output name of the Clouds Mask from Time Series",
#             default=None,
#             required=False,
#             type=str)
# 
#         parser.add_argument(
#             "-flatreflectance",
#             '--fre',
#             dest='reflectance',
#             action="store",
#             help="If True, flat reflectance. If False, surface reflectance.",
#             default=True,
#             required=False,
#             type=str)
# 
#         args = parser.parse_args()
# 
#         computeSITS(
#             S2Dir=args.s2dir,
#             out_SITS=args.outSITS,
#             resample_20mbands=args.resample20mBands,
#             resampleCSV=args.resampleCSV,
#             interpolation=args.interpolation,
#             unzip=args.unzip,
#             out_cloudMask=args.cloudMask,
#             checkOutliers=args.checkOutliers,
#             use_flatreflectance=args.reflectance,
#             n_jobs=args.n_jobs,
#             ram=args.ram)
# 
# 
# if __name__ == "__main__":
#     sys.exit(main())
# 
# =============================================================================
