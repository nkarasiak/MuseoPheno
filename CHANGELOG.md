# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2020-07-06 : 0.1]

### Fixed
- Fix bug with pip installation

### Removed
- Remove some useless requirements

## [2020-07-06 : 0.1-rc2]

### Added 
- Added the choice to compute metrics thresold with the min from season or from the year
- Documentation enhancements

### Fixed
- Various improvements

## [2020-06-14 : 0.1-rc1]

### Added

modules are : 
- datasets
- expression_manager
- sensor
- time_series

Pre-defined sensors are : 
- Sentinel-2
- Formosat-2

time_series interpolation are :
- double_logistic (thanks to @mfauvel)
- linear and cubic interpolation
- savitzky golay
