

.. image:: https://readthedocs.org/projects/museopheno/badge/?version=latest
   :target: https://museopheno.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation status


.. image:: https://badge.fury.io/py/museopheno.svg
   :target: https://badge.fury.io/py/museopheno
   :alt: PyPI version


.. image:: https://api.travis-ci.com/nkarasiak/MuseoPheno.svg?branch=master
   :target: https://travis-ci.com/nkarasiak/MuseoPheno
   :alt: Build status


.. image:: https://pepy.tech/badge/museopheno
   :target: https://pepy.tech/project/museopheno
   :alt: Downloads



.. image:: https://github.com/nkarasiak/MuseoPheno/raw/master/metadata/MuseoPheno_logo_128.png
   :target: https://github.com/nkarasiak/MuseoPheno/raw/master/metadata/MuseoPheno_logo_128.png
   :alt: MuseoPheno logo


MuseoPheno
==========

MuseoPheno aims to be a phenology toolbox for Satellite Image Time Series.
The `documentation is hosted on readthedocs <https://museopheno.readthedocs.org/>`_.

What does MuseoPheno do today ?
===============================

MuseoPheno globally eases the way to smooth or compute spectral indices for time series.

Don't manage temporal information, MuseoPheno does it for you
=============================================================

Spectral indices
----------------

Let's suppose you want to compute the NDVI, and you know how your bands are ordered in your raster.
Just define your band order (it supposes your bands are stacked in the following order : band1, band2... for date 1, then band1, band2 for date 2 and so on...)
then give MuseoPheno the expression "(B8-B4)/(B8+B4)", and the library will generate the NDVI for each date.

So it takes only a few lines to go from your time series to a temporal spectral index. It is also as fast to produce the indice raster.

You can see the `demo here with Leaf Chlorophyll Content <https://museopheno.readthedocs.io/en/latest/auto_examples/sensors/LeafChlorophyllContentFromS2TimeSeries.html>`_.

*Your index is not listed ?* It is very easy to add a new sensor or to add new index. Just follow the simple documentation.

Temporal resampling and smoothing
---------------------------------

It has never been so easy to temporaly resample a time series given an array. Just define the beginning date, the end date, and the delta between acquistion, then MuseoPheno will deal it for you.
You need to smooth your new time series ? No problem, just use the SmoothSignal class.

Phenological metrics
--------------------

You can easilly compute phenological metrics (start of season, end of season) using the PhenologyMetrics class from the time_series module.

How do I install it ?
=====================

A package is available on pip :
``python3 -m pip install museopheno --user``

Alternatively, you can install **museopheno** directly from the git :
``python3 -m pip install git+https://github.com/nkarasiak/MuseoPheno.git --user``

Feel free to remove the ``--user`` if you like to install the library for every user on the machine.

What is planning to do MuseoPheno ?
===================================


* More temporal signal smoothing (Whittaker...)
* Lot of examples... so feel free to add !
* Add tests to check consistency and reliability.
