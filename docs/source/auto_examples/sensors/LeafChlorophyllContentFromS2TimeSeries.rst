.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_sensors_LeafChlorophyllContentFromS2TimeSeries.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_sensors_LeafChlorophyllContentFromS2TimeSeries.py:


Compute Leaf Chlorophyll Content from S2 Time Series
=============================================================================

This example shows how to compute an indice (here LChloC) from a S2 with 10 bands.
The raster is order date per date (blue,green,red...date 1 then blue,green,red... date 2...)


Import libraries


.. code-block:: default


    import numpy as np
    from museopheno import sensors,datasets







Import raster dataset with list of dates


.. code-block:: default


    raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)







Create an instance of sensors.Sentinel2 with 10bands


.. code-block:: default


    S2 = sensors.Sentinel2(n_bands=10)

    print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')

    # List of available indice : 
    S2.available_indices.keys()






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Default band order for 10 bands is : 2, 3, 4, 8, 5, 6, 7, 8A, 11, 12.


Write metadata in each band (date + band name)
------------------------------------------------------

Write metadata in each band (date + band name) in order to use
raster timeseries manager plugin on QGIS or to have the date and the band in
the list of bands QGIS.


.. code-block:: default


    S2.setDescriptionMetadata(raster,dates)







Generate indice from array
---------------------------------


.. code-block:: default


    X = datasets.Sentinel2_3a_2018(get_only_sample=True)
    LChloC = S2.generateIndice(X,S2.getIndiceExpression('LChloC'),dtype=np.float32)
    print(LChloC)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Total number of blocks : 246
    [[3.6171224 4.7565336 6.339056  ... 4.8849206 4.6334014 2.5289633]
     [3.6171224 4.7565336 6.339056  ... 4.8849206 4.6334014 2.5289633]
     [3.816203  4.9623957 6.238683  ... 4.8507752 4.7189407 2.2846925]
     ...
     [3.496614  5.16485   5.8566036 ... 4.695811  4.6486487 2.7175226]
     [3.496614  5.16485   5.8566036 ... 4.695811  4.6486487 2.7175226]
     [3.6359339 5.6272726 6.242915  ... 5.0939336 5.041322  3.0707395]]


Generate indice from and to a raster
---------------------------------------


.. code-block:: default


    S2.generateRaster(input_raster=raster,output_raster='/tmp/LChloC.tif',expression=S2.getIndiceExpression('LChloC'),dtype=np.float32)






.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Total number of blocks : 246
    Detected 7 bands for function generateIndice.
    Computing indice [........................................]0%    Computing indice [........................................]1%    Computing indice [........................................]2%    Computing indice [#.......................................]3%    Computing indice [#.......................................]4%    Computing indice [##......................................]5%    Computing indice [##......................................]6%    Computing indice [##......................................]7%    Computing indice [###.....................................]8%    Computing indice [###.....................................]9%    Computing indice [####....................................]10%    Computing indice [####....................................]11%    Computing indice [####....................................]12%    Computing indice [#####...................................]13%    Computing indice [#####...................................]14%    Computing indice [######..................................]15%    Computing indice [######..................................]16%    Computing indice [######..................................]17%    Computing indice [#######.................................]18%    Computing indice [#######.................................]19%    Computing indice [########................................]20%    Computing indice [########................................]21%    Computing indice [########................................]22%    Computing indice [#########...............................]23%    Computing indice [#########...............................]24%    Computing indice [##########..............................]25%    Computing indice [##########..............................]26%    Computing indice [##########..............................]27%    Computing indice [###########.............................]28%    Computing indice [###########.............................]29%    Computing indice [############............................]30%    Computing indice [############............................]31%    Computing indice [############............................]32%    Computing indice [#############...........................]33%    Computing indice [#############...........................]34%    Computing indice [##############..........................]35%    Computing indice [##############..........................]36%    Computing indice [##############..........................]37%    Computing indice [###############.........................]38%    Computing indice [###############.........................]39%    Computing indice [################........................]40%    Computing indice [################........................]41%    Computing indice [################........................]42%    Computing indice [#################.......................]43%    Computing indice [#################.......................]44%    Computing indice [##################......................]45%    Computing indice [##################......................]46%    Computing indice [##################......................]47%    Computing indice [###################.....................]48%    Computing indice [###################.....................]49%    Computing indice [####################....................]50%    Computing indice [####################....................]51%    Computing indice [####################....................]52%    Computing indice [#####################...................]53%    Computing indice [#####################...................]54%    Computing indice [######################..................]55%    Computing indice [######################..................]56%    Computing indice [######################..................]57%    Computing indice [#######################.................]58%    Computing indice [#######################.................]59%    Computing indice [########################................]60%    Computing indice [########################................]61%    Computing indice [########################................]62%    Computing indice [#########################...............]63%    Computing indice [#########################...............]64%    Computing indice [##########################..............]65%    Computing indice [##########################..............]66%    Computing indice [##########################..............]67%    Computing indice [###########################.............]68%    Computing indice [###########################.............]69%    Computing indice [############################............]70%    Computing indice [############################............]71%    Computing indice [############################............]72%    Computing indice [#############################...........]73%    Computing indice [#############################...........]74%    Computing indice [##############################..........]75%    Computing indice [##############################..........]76%    Computing indice [##############################..........]77%    Computing indice [###############################.........]78%    Computing indice [###############################.........]79%    Computing indice [################################........]80%    Computing indice [################################........]81%    Computing indice [################################........]82%    Computing indice [#################################.......]83%    Computing indice [#################################.......]84%    Computing indice [##################################......]85%    Computing indice [##################################......]86%    Computing indice [##################################......]87%    Computing indice [###################################.....]88%    Computing indice [###################################.....]89%    Computing indice [####################################....]90%    Computing indice [####################################....]91%    Computing indice [####################################....]92%    Computing indice [#####################################...]93%    Computing indice [#####################################...]94%    Computing indice [######################################..]95%    Computing indice [######################################..]96%    Computing indice [######################################..]97%    Computing indice [#######################################.]98%    Computing indice [#######################################.]99%    Computing indice [########################################]100%
    Saved /tmp/LChloC.tif using function generateIndice


Plot example of LChloC


.. code-block:: default


    from matplotlib import pyplot as plt
    from datetime import datetime
    dateToDatetime = [datetime.strptime(str(date),'%Y%m%d') for date in dates]
    plt.plot_date(dateToDatetime,LChloC[:10,:].T,'-o')
    plt.ylabel('Leaf Chlorophyll Content')
    import os
    os.remove('/tmp/LChloC.tif')


.. image:: /auto_examples/sensors/images/sphx_glr_LeafChlorophyllContentFromS2TimeSeries_001.png
    :class: sphx-glr-single-img





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  2.026 seconds)


.. _sphx_glr_download_auto_examples_sensors_LeafChlorophyllContentFromS2TimeSeries.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: LeafChlorophyllContentFromS2TimeSeries.py <LeafChlorophyllContentFromS2TimeSeries.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: LeafChlorophyllContentFromS2TimeSeries.ipynb <LeafChlorophyllContentFromS2TimeSeries.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
