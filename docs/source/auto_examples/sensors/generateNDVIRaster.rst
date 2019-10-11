.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_sensors_generateNDVIRaster.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_sensors_generateNDVIRaster.py:


Generate a NDVI time series
=============================================================================

This example shows how to produce a NDVI time series from a Sentinel-2 time series.

Import libraries
---------------------------


.. code-block:: default

    from museopheno import sensors,datasets
    import numpy as np







Import dataset
---------------------------


.. code-block:: default

    raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)







Create an instance of sensors.Sentinel2()


.. code-block:: default


    S2 = sensors.Sentinel2(n_bands=10)

    print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Default band order for 10 bands is : 2, 3, 4, 8, 5, 6, 7, 8A, 11, 12.


List of available indice : 


.. code-block:: default


    print(S2.available_indices.keys())





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    dict_keys(['ACORVI', 'ACORVInarrow', 'SAVI', 'EVI', 'EVI2', 'PSRI', 'ARI', 'ARI2', 'MARI', 'CHLRE', 'MCARI', 'MSI', 'MSIB12', 'NDrededgeSWIR', 'SIPI2', 'NDWI', 'LCaroC', 'LChloC', 'LAnthoC', 'Chlogreen', 'NDVI', 'NDVInarrow', 'NDVIre', 'RededgePeakArea', 'Rratio', 'MTCI', 'S2REP', 'IRECI', 'NBR'])


Write metadata in each band (date + band name)
------------------------------------------------------

This is useful to show date in band number in Qgis


.. code-block:: default


    S2.setDescriptionMetadata(raster,dates)







Produce NDVI time series from and to a raster
----------------------------------------------


.. code-block:: default

    S2.generateRaster(input_raster=raster,output_raster='/tmp/indice.tif',expression=S2.getIndiceExpression('NDVI'),dtype=np.float32)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Total number of blocks : 246
    Detected 7 bands for function generateIndice.
    Computing indice [........................................]0%    Computing indice [........................................]1%    Computing indice [........................................]2%    Computing indice [#.......................................]3%    Computing indice [#.......................................]4%    Computing indice [##......................................]5%    Computing indice [##......................................]6%    Computing indice [##......................................]7%    Computing indice [###.....................................]8%    Computing indice [###.....................................]9%    Computing indice [####....................................]10%    Computing indice [####....................................]11%    Computing indice [####....................................]12%    Computing indice [#####...................................]13%    Computing indice [#####...................................]14%    Computing indice [######..................................]15%    Computing indice [######..................................]16%    Computing indice [######..................................]17%    Computing indice [#######.................................]18%    Computing indice [#######.................................]19%    Computing indice [########................................]20%    Computing indice [########................................]21%    Computing indice [########................................]22%    Computing indice [#########...............................]23%    Computing indice [#########...............................]24%    Computing indice [##########..............................]25%    Computing indice [##########..............................]26%    Computing indice [##########..............................]27%    Computing indice [###########.............................]28%    Computing indice [###########.............................]29%    Computing indice [############............................]30%    Computing indice [############............................]31%    Computing indice [############............................]32%    Computing indice [#############...........................]33%    Computing indice [#############...........................]34%    Computing indice [##############..........................]35%    Computing indice [##############..........................]36%    Computing indice [##############..........................]37%    Computing indice [###############.........................]38%    Computing indice [###############.........................]39%    Computing indice [################........................]40%    Computing indice [################........................]41%    Computing indice [################........................]42%    Computing indice [#################.......................]43%    Computing indice [#################.......................]44%    Computing indice [##################......................]45%    Computing indice [##################......................]46%    Computing indice [##################......................]47%    Computing indice [###################.....................]48%    Computing indice [###################.....................]49%    Computing indice [####################....................]50%    Computing indice [####################....................]51%    Computing indice [####################....................]52%    Computing indice [#####################...................]53%    Computing indice [#####################...................]54%    Computing indice [######################..................]55%    Computing indice [######################..................]56%    Computing indice [######################..................]57%    Computing indice [#######################.................]58%    Computing indice [#######################.................]59%    Computing indice [########################................]60%    Computing indice [########################................]61%    Computing indice [########################................]62%    Computing indice [#########################...............]63%    Computing indice [#########################...............]64%    Computing indice [##########################..............]65%    Computing indice [##########################..............]66%    Computing indice [##########################..............]67%    Computing indice [###########################.............]68%    Computing indice [###########################.............]69%    Computing indice [############################............]70%    Computing indice [############################............]71%    Computing indice [############################............]72%    Computing indice [#############################...........]73%    Computing indice [#############################...........]74%    Computing indice [##############################..........]75%    Computing indice [##############################..........]76%    Computing indice [##############################..........]77%    Computing indice [###############################.........]78%    Computing indice [###############################.........]79%    Computing indice [################################........]80%    Computing indice [################################........]81%    Computing indice [################################........]82%    Computing indice [#################################.......]83%    Computing indice [#################################.......]84%    Computing indice [##################################......]85%    Computing indice [##################################......]86%    Computing indice [##################################......]87%    Computing indice [###################################.....]88%    Computing indice [###################################.....]89%    Computing indice [####################################....]90%    Computing indice [####################################....]91%    Computing indice [####################################....]92%    Computing indice [#####################################...]93%    Computing indice [#####################################...]94%    Computing indice [######################################..]95%    Computing indice [######################################..]96%    Computing indice [######################################..]97%    Computing indice [#######################################.]98%    Computing indice [#######################################.]99%    Computing indice [########################################]100%
    Saved /tmp/indice.tif using function generateIndice


Plot NDVI indice


.. code-block:: default

    from museotoolbox.raster_tools import rasterMath
    from matplotlib import pyplot as plt

    rM = rasterMath('/tmp/indice.tif')
    NDVI=rM.getRandomBlock() #randomly select a block
    from datetime import datetime
    dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
    plt.plot_date(dateToDatetime,NDVI[:10,:].T,'-o')
    plt.ylabel('NDVI')


.. image:: /auto_examples/sensors/images/sphx_glr_generateNDVIRaster_001.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Total number of blocks : 246



.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  1.997 seconds)


.. _sphx_glr_download_auto_examples_sensors_generateNDVIRaster.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: generateNDVIRaster.py <generateNDVIRaster.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: generateNDVIRaster.ipynb <generateNDVIRaster.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
