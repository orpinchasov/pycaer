# General
'pycaer' is a Python package wrapping libcaer by iniLabs. 'libcaer' is described as a "Minimal C library to access,
configure and get data out of AER sensors, such as the Dynamic Vision Sensor (DVS) or DAVIS cameras."

## Requirements
libcaer <= 1.0.3 (code doesn't run on 2.0.1)

## Installation
Compile and install libcaer as instructed:
https://github.com/inilabs/libcaer

## Usage
See bin/camera_viewer.py for a complete example.

Also look at the various examples included in the various modules.

Run them according to the following example:

cd \<repository main\>

python -m pycaer.graphics.render
