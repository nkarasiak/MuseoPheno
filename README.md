[![Documentation status](https://readthedocs.org/projects/museopheno/badge/?version=latest)](https://museopheno.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/museopheno.svg)](https://badge.fury.io/py/museopheno)
[![Build status](https://api.travis-ci.org/nkarasiak/MuseoPheno.svg?branch=master)](https://travis-ci.org/nkarasiak/MuseoPheno)
[![Downloads](https://pepy.tech/badge/museopheno)](https://pepy.tech/project/museopheno)
[comment]: <> [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3404729.svg)](https://doi.org/10.5281/zenodo.3404728)

![MuseoPheno logo](https://github.com/nkarasiak/MuseoPheno/raw/master/metadata/MuseoPheno_logo_128.png)

# MuseoPheno

MuseoPheno aims to be a phenology toolbox for Satellite Image Time Series.
The [documentation is hosted on readthedocs](https://museopheno.readthedocs.org/).

# What does MuseoPheno do today ?

MuseoPheno eases the way to compute Sentinel2 level 2A time series and spectral indices in time series.

Plus, you have a command line to produce a Sentinel2 raster time series :
`museopheno.computeS2SITS -S2dir /tmp/S2_2018/ -unzip True -out /mnt/SITS_2018.tif`

# Don't manage temporal information, MuseoPheno do it for you

## Spectral indices

Let's suppose you want to compute the NDVI, and you know how your bands are ordered in your raster.
Just define your band order (it supposes your bands are stacked in the following order : band1, band2... for date 1, then band1, band2 for date 2 and so on...)
then give MuseoPheno the expression "(B8-B4)/(B8+B4)", and the library will generate the NDVI for each date.

So it takes only a few lines to go from your time series to a temporal spectral indices. It is also as fast to produce the indice raster.

You can see the demo here with Leaf Chlorophyll Content.

*Your indice is not listed ?* It is very easy to add a new sensor or to add new indices for Sentinel2. Just follow the simple documentation.

## Temporal resampling and smoothing



## How do I install it ?
A package is available on pip :
`python3 -m pip install museopheno --user`

Alternatively, you can install **museopheno** directly from the git :
`python3 -m pip install git+https://github.com/nkarasiak/MuseoPheno.git --user`

Feel free to remove the `--user` if you like to install the library for every user on the machine.

# What is planning to do MuseoPheno ?

- More temporal signal smoothing (double logistic, Whittaker...)
- Computation and mapping of phenology metrics (start of season, end of season)