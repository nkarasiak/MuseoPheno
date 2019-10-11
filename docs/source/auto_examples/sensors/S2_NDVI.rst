.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_sensors_S2_NDVI.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_sensors_S2_NDVI.py:


Compute a spectral indice from S2 Time Series
=============================================================================

This example shows how to compute an indice (here NDVI) from a S2 with 10 bands.
The raster is order date per date (blue,green,red...date 1 then blue,green,red... date 2...)

Import libraries
---------------------------


.. code-block:: default


    import numpy as np
    from museopheno import sensors,datasets
    from museotoolbox.raster_tools import rasterMath







Import dataset
---------------------------


.. code-block:: default

    raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)







Define an instance of sensors.Sentinel2()


.. code-block:: default


    S2 = sensors.Sentinel2(n_bands=10)

    # check default band_order
    print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')

    # List of available indice : 
    S2.available_indices.keys()





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Default band order for 10 bands is : 2, 3, 4, 8, 5, 6, 7, 8A, 11, 12.


Write metadata in each band (date + band name)
------------------------------------------------------


.. code-block:: default


    S2.setDescriptionMetadata(raster,dates)







Generate a raster with NDVI indice
---------------------------------------------


.. code-block:: default


    # show expression and condition of NDVI indice
    print(S2.getIndiceExpression('NDVI'))

    # generate raster
    S2.generateRaster(input_raster=raster,output_raster='/tmp/S2.tif',expression=S2.getIndiceExpression('NDVI'),dtype=np.float32)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    {'expression': '(B8-B4)/(B8+B4)', 'condition': '(B8+B4) != 0'}
    Total number of blocks : 246
    Detected 7 bands for function generateIndice.
    Computing indice [........................................]0%    Computing indice [........................................]1%    Computing indice [........................................]2%    Computing indice [#.......................................]3%    Computing indice [#.......................................]4%    Computing indice [##......................................]5%    Computing indice [##......................................]6%    Computing indice [##......................................]7%    Computing indice [###.....................................]8%    Computing indice [###.....................................]9%    Computing indice [####....................................]10%    Computing indice [####....................................]11%    Computing indice [####....................................]12%    Computing indice [#####...................................]13%    Computing indice [#####...................................]14%    Computing indice [######..................................]15%    Computing indice [######..................................]16%    Computing indice [######..................................]17%    Computing indice [#######.................................]18%    Computing indice [#######.................................]19%    Computing indice [########................................]20%    Computing indice [########................................]21%    Computing indice [########................................]22%    Computing indice [#########...............................]23%    Computing indice [#########...............................]24%    Computing indice [##########..............................]25%    Computing indice [##########..............................]26%    Computing indice [##########..............................]27%    Computing indice [###########.............................]28%    Computing indice [###########.............................]29%    Computing indice [############............................]30%    Computing indice [############............................]31%    Computing indice [############............................]32%    Computing indice [#############...........................]33%    Computing indice [#############...........................]34%    Computing indice [##############..........................]35%    Computing indice [##############..........................]36%    Computing indice [##############..........................]37%    Computing indice [###############.........................]38%    Computing indice [###############.........................]39%    Computing indice [################........................]40%    Computing indice [################........................]41%    Computing indice [################........................]42%    Computing indice [#################.......................]43%    Computing indice [#################.......................]44%    Computing indice [##################......................]45%    Computing indice [##################......................]46%    Computing indice [##################......................]47%    Computing indice [###################.....................]48%    Computing indice [###################.....................]49%    Computing indice [####################....................]50%    Computing indice [####################....................]51%    Computing indice [####################....................]52%    Computing indice [#####################...................]53%    Computing indice [#####################...................]54%    Computing indice [######################..................]55%    Computing indice [######################..................]56%    Computing indice [######################..................]57%    Computing indice [#######################.................]58%    Computing indice [#######################.................]59%    Computing indice [########################................]60%    Computing indice [########################................]61%    Computing indice [########################................]62%    Computing indice [#########################...............]63%    Computing indice [#########################...............]64%    Computing indice [##########################..............]65%    Computing indice [##########################..............]66%    Computing indice [##########################..............]67%    Computing indice [###########################.............]68%    Computing indice [###########################.............]69%    Computing indice [############################............]70%    Computing indice [############################............]71%    Computing indice [############################............]72%    Computing indice [#############################...........]73%    Computing indice [#############################...........]74%    Computing indice [##############################..........]75%    Computing indice [##############################..........]76%    Computing indice [##############################..........]77%    Computing indice [###############################.........]78%    Computing indice [###############################.........]79%    Computing indice [################################........]80%    Computing indice [################################........]81%    Computing indice [################################........]82%    Computing indice [#################################.......]83%    Computing indice [#################################.......]84%    Computing indice [##################################......]85%    Computing indice [##################################......]86%    Computing indice [##################################......]87%    Computing indice [###################################.....]88%    Computing indice [###################################.....]89%    Computing indice [####################################....]90%    Computing indice [####################################....]91%    Computing indice [####################################....]92%    Computing indice [#####################################...]93%    Computing indice [#####################################...]94%    Computing indice [######################################..]95%    Computing indice [######################################..]96%    Computing indice [######################################..]97%    Computing indice [#######################################.]98%    Computing indice [#######################################.]99%    Computing indice [########################################]100%
    Saved /tmp/S2.tif using function generateIndice


Plot image


.. code-block:: default


    rM = rasterMath(raster)
    X=rM.getRandomBlock()
    NDVI = S2.generateIndice(X,S2.getIndiceExpression('NDVI'),dtype=np.float32)

    from matplotlib import pyplot as plt
    from datetime import datetime
    dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
    plt.plot_date(dateToDatetime,NDVI[:10,:].T,'-o')
    plt.ylabel('Leaf Chlorophyll Content')


.. image:: /auto_examples/sensors/images/sphx_glr_S2_NDVI_001.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Total number of blocks : 246



.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  2.117 seconds)


.. _sphx_glr_download_auto_examples_sensors_S2_NDVI.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: S2_NDVI.py <S2_NDVI.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: S2_NDVI.ipynb <S2_NDVI.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
