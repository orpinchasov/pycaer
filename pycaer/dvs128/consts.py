#
# Module containing necessary DVS128 configuration constants.
# They are used when configuration camera usage, etc.
#
# The consts are taken from the C headers. Specifically from:
# - /usr/include/libcaer/devices/usb.h
# - /usr/include/devices/dvs128.h
#
# Further documentation of the consts themselves is found in the
# header files.
#

CAER_HOST_CONFIG_USB = -1
CAER_HOST_CONFIG_DATAEXCHANGE = -2
CAER_HOST_CONFIG_PACKETS = -3

CAER_HOST_CONFIG_DATAEXCHANGE_BUFFER_SIZE = 0
CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING = 1
CAER_HOST_CONFIG_DATAEXCHANGE_START_PRODUCERS = 2
CAER_HOST_CONFIG_DATAEXCHANGE_STOP_PRODUCERS = 3

DVS128_CONFIG_BIAS = 1
DVS128_CONFIG_BIAS_DIFFOFF = 4
DVS128_CONFIG_BIAS_DIFFON = 8
DVS128_CONFIG_BIAS_DIFF = 9
