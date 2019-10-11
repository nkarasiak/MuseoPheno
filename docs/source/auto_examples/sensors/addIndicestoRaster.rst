.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_sensors_addIndicestoRaster.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_sensors_addIndicestoRaster.py:


Produce a new raster with indices stacked in new bands
=============================================================================

This example shows how to add to a raster spectral indices.
Here we add LChloC and ACORVI (a modified NDVI).


Import libraries
----------------------------


.. code-block:: default


    import numpy as np
    from museopheno import sensors,datasets

    # to add custom  creation of new raster, import rasterMath
    from museotoolbox.raster_tools import rasterMath 







Import dataset
----------------------


.. code-block:: default


    raster,dates = datasets.Sentinel2_3a_2018(return_dates=True)
    S2 = sensors.Sentinel2(n_bands=10)

    print('Default band order for 10 bands is : '+', '.join(S2.band_order)+'.')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Default band order for 10 bands is : 2, 3, 4, 8, 5, 6, 7, 8A, 11, 12.


List of available indice : 


.. code-block:: default


    S2.available_indices.keys()







Define a custom function
---------------------------------------


.. code-block:: default


    def createSITSplusIndices(X):
        X1 = S2.generateIndice(X,S2.getIndiceExpression('LChloC'),multiply_by=100,dtype=np.int16)
        X2 = S2.generateIndice(X,S2.getIndiceExpression('ACORVI'),multiply_by=100,dtype=np.int16)
    
        return np.hstack((X,X1,X2)).astype(np.int16)







Use rasterMath to read and write block per block the raster according to a function


.. code-block:: default


    rM = rasterMath(raster)

    X = rM.getRandomBlock()
    print('Block has {} pixels and {} bands'.format(X.shape[0],X.shape[1]))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Total number of blocks : 246
    Block has 227 pixels and 70 bands


Now we can try our function


.. code-block:: default


    XwithIndices = createSITSplusIndices(X)
    print('Raster+indice produced has {} pixels and {} bands'.format(XwithIndices.shape[0],XwithIndices.shape[1]))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Raster+indice produced has 227 pixels and 84 bands


Now we add our function as the test was a success


.. code-block:: default

    rM.addFunction(createSITSplusIndices,'/tmp/SITSwithIndices.tif')





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Using datatype from numpy table : int16.
    Detected 84 bands for function createSITSplusIndices.


Produce raster


.. code-block:: default


    rM.run()

    ##################
    # Plot image
    from matplotlib import pyplot as plt
    rM = rasterMath('/tmp/SITSwithIndices.tif')
    X=rM.getRandomBlock() #randomly select a block
    plt.plot(X[:20,:].T)



.. image:: /auto_examples/sensors/images/sphx_glr_addIndicestoRaster_001.png
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    rasterMath... [........................................]0%    rasterMath... [........................................]1%    rasterMath... [........................................]2%    rasterMath... [#.......................................]3%    rasterMath... [#.......................................]4%    rasterMath... [##......................................]5%    rasterMath... [##......................................]6%    rasterMath... [##......................................]7%    rasterMath... [###.....................................]8%    rasterMath... [###.....................................]9%    rasterMath... [####....................................]10%    rasterMath... [####....................................]11%    rasterMath... [####....................................]12%    rasterMath... [#####...................................]13%    rasterMath... [#####...................................]14%    rasterMath... [######..................................]15%    rasterMath... [######..................................]16%    rasterMath... [######..................................]17%    rasterMath... [#######.................................]18%    rasterMath... [#######.................................]19%    rasterMath... [########................................]20%    rasterMath... [########................................]21%    rasterMath... [########................................]22%    rasterMath... [#########...............................]23%    rasterMath... [#########...............................]24%    rasterMath... [##########..............................]25%    rasterMath... [##########..............................]26%    rasterMath... [##########..............................]27%    rasterMath... [###########.............................]28%    rasterMath... [###########.............................]29%    rasterMath... [############............................]30%    rasterMath... [############............................]31%    rasterMath... [############............................]32%    rasterMath... [#############...........................]33%    rasterMath... [#############...........................]34%    rasterMath... [##############..........................]35%    rasterMath... [##############..........................]36%    rasterMath... [##############..........................]37%    rasterMath... [###############.........................]38%    rasterMath... [###############.........................]39%    rasterMath... [################........................]40%    rasterMath... [################........................]41%    rasterMath... [################........................]42%    rasterMath... [#################.......................]43%    rasterMath... [#################.......................]44%    rasterMath... [##################......................]45%    rasterMath... [##################......................]46%    rasterMath... [##################......................]47%    rasterMath... [###################.....................]48%    rasterMath... [###################.....................]49%    rasterMath... [####################....................]50%    rasterMath... [####################....................]51%    rasterMath... [####################....................]52%    rasterMath... [#####################...................]53%    rasterMath... [#####################...................]54%    rasterMath... [######################..................]55%    rasterMath... [######################..................]56%    rasterMath... [######################..................]57%    rasterMath... [#######################.................]58%    rasterMath... [#######################.................]59%    rasterMath... [########################................]60%    rasterMath... [########################................]61%    rasterMath... [########################................]62%    rasterMath... [#########################...............]63%    rasterMath... [#########################...............]64%    rasterMath... [##########################..............]65%    rasterMath... [##########################..............]66%    rasterMath... [##########################..............]67%    rasterMath... [###########################.............]68%    rasterMath... [###########################.............]69%    rasterMath... [############################............]70%    rasterMath... [############################............]71%    rasterMath... [############################............]72%    rasterMath... [#############################...........]73%    rasterMath... [#############################...........]74%    rasterMath... [##############################..........]75%    rasterMath... [##############################..........]76%    rasterMath... [##############################..........]77%    rasterMath... [###############################.........]78%    rasterMath... [###############################.........]79%    rasterMath... [################################........]80%    rasterMath... [################################........]81%    rasterMath... [################################........]82%    rasterMath... [#################################.......]83%    rasterMath... [#################################.......]84%    rasterMath... [##################################......]85%    rasterMath... [##################################......]86%    rasterMath... [##################################......]87%    rasterMath... [###################################.....]88%    rasterMath... [###################################.....]89%    rasterMath... [####################################....]90%    rasterMath... [####################################....]91%    rasterMath... [####################################....]92%    rasterMath... [#####################################...]93%    rasterMath... [#####################################...]94%    rasterMath... [######################################..]95%    rasterMath... [######################################..]96%    rasterMath... [######################################..]97%    rasterMath... [#######################################.]98%    rasterMath... [#######################################.]99%    rasterMath... [########################################]100%
    Saved /tmp/SITSwithIndices.tif using function createSITSplusIndices
    Total number of blocks : 246



.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  3.352 seconds)


.. _sphx_glr_download_auto_examples_sensors_addIndicestoRaster.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: addIndicestoRaster.py <addIndicestoRaster.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: addIndicestoRaster.ipynb <addIndicestoRaster.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
