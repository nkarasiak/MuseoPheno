# MuseoPheno

MuseoPheno aims to be a phenology toolbox for Satellite Image Time Series.
The [documentation is hosted on readthedocs](https://museopheno.readthedocs.org/).

# What does MuseoPheno do today ?

MuseoPheno eases the way to compute Sentinel2 level 2A time series and spectral indices in time series.

Plus, you have a command line to produce a Sentinel2 raster time series :
`museopheno.computeS2SITS -S2dir /tmp/S2_2018/ -unzip True -out /mnt/SITS_2018.tif`

# Don't manage temporal information, MuseoPheno do it for you

Let's suppose you want to compute the NDVI, and you know how your bands are ordered in your raster.
Just define your band order (it supposes your bands are stacked in the following order : band1, band2... for date 1, then band1, band2 for date 2 and so on...)
then give MuseoPheno the expression "(B8-B4)/(B8+B4)", and the library will generate the NDVI for each date.

So it takes only a few lines to go from your time series to a temporal spectral indices. It is also as fast to produce the indice raster.

You can see the demo here with Leaf Chlorophyll Content.

*Your indice is not listed ?* It is very easy to add a new sensor or to add new indices for Sentinel2. Just follow the simple documentation.

# What is planning to do MuseoPheno ?

- Temporal signal smoothing (logistic, Savitzky-Golay, Whittaker...)
- Computation and mapping of phenology metrics (start of season, end of season)

# When ?
Nothing planned.
