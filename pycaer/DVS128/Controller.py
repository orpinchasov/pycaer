#
# Module for controlling the DVS128 camera. Mainly a ctypes wrapper
# for the functions exported by the library libcaer.so.
# Function definitions are found in the files:
# - /usr/include/libcaer/devices/usb.h
#

from EventPacket import EventPacketContainer
from PacketDefinitions import caerEventPacketContainer

import ctypes

class Controller(object):
    DVS128_DEVICE_TYPE = 0 # DVS128 device (/usr/include/libcaer/devices/dvs128.h)

    def __init__(self, device_id=0):
        self._device_id = device_id

        self._libcaer = ctypes.CDLL('/home/bnapp/code/or_libcaer/src/libcaer.so')

        # NOTE: Some functions require configuration of their arguments and
        # return types to match the library's configuration.
        # Those functions which do not need explicit configuration are not
        # written here and some implicit casting might occur in their parameters
        # and return values
        self._libcaer_func_caerDeviceOpen = self._libcaer.caerDeviceOpen
        self._libcaer_func_caerDeviceOpen.restype = ctypes.c_void_p
        
        self._libcaer_func_caerDeviceClose = self._libcaer.caerDeviceClose
        self._libcaer_func_caerDeviceClose.restype = ctypes.c_bool

        self._libcaer_func_caerDeviceSendDefaultConfig = self._libcaer.caerDeviceSendDefaultConfig
        self._libcaer_func_caerDeviceSendDefaultConfig.restype = ctypes.c_bool

        self._libcaer_func_caerDeviceDataStart = self._libcaer.caerDeviceDataStart
        self._libcaer_func_caerDeviceDataStart.restype = ctypes.c_bool

        self._libcaer_func_caerDeviceDataStop = self._libcaer.caerDeviceDataStop
        self._libcaer_func_caerDeviceDataStop.restype = ctypes.c_bool

        self._libcaer_func_caerDeviceConfigSet = self._libcaer.caerDeviceConfigSet
        self._libcaer_func_caerDeviceConfigSet.restype = ctypes.c_bool

        self._libcaer_func_caerDeviceDataGet = self._libcaer.caerDeviceDataGet
        self._libcaer_func_caerDeviceDataGet.restype = ctypes.POINTER(caerEventPacketContainer)

    def open_device(self):
        # The parameters passed to the function are the most basic and
        # simply allow access to the events created by the device
        self._handle = self._libcaer_func_caerDeviceOpen(ctypes.c_uint16(self._device_id),
                                                         ctypes.c_uint16(self.DVS128_DEVICE_TYPE),
                                                         ctypes.c_uint8(0),
                                                         ctypes.c_uint8(0),
                                                         None)

        # NOTE: Checking for NULL pointers is done by checking
        # the boolean value (rather than None, for example)
        if not self._handle:
            return False
        else:
            return True

    def close_device(self):
        # Create a temporary variable to hold the ctypes variable and
        # not the Pythonic 'int'. This variable can be passed by reference
        c_handle = ctypes.c_void_p(self._handle)
        return self._libcaer_func_caerDeviceClose(ctypes.byref(c_handle))

    def send_default_configuration(self):
        return self._libcaer.caerDeviceSendDefaultConfig(self._handle)

    def start_data(self):
        # NOTE: The second argument and the ones after it are callback functions
        # which might be used in the future. Currently, the code supports only
        # getting data by polling
        return self._libcaer.caerDeviceDataStart(self._handle, None, None, None, None, None)

    def stop_data(self):
        return self._libcaer.caerDeviceDataStop(self._handle)

    def set_configuration(self, module, parameter, extra_param):
        return self._libcaer.caerDeviceConfigSet(self._handle,
                                                 ctypes.c_uint8(module),
                                                 ctypes.c_uint8(parameter),
                                                 ctypes.c_uint32(extra_param))

    def get_data(self):
        event_packet_container = self._libcaer_func_caerDeviceDataGet(self._handle)

        if not event_packet_container:
            return None
        else:
            return EventPacketContainer(self._libcaer, event_packet_container)
