""" Module to define packet structs as used by the camera itself.

These structs match their C definitions as found in the files:
- /usr/include/libcaer/events/common.h
- /usr/include/libcaer/events/polarity.h
"""

from ctypes import Structure, POINTER, c_uint16, c_uint32, c_int32

SPECIAL_EVENT = 0
POLARITY_EVENT = 1


class caerEventPacketHeader(Structure):
    # NOTE: The packing of the struct is essential for compatibility
    # with the C struct packing
    _pack_ = 1
    _fields_ = [("eventType", c_uint16),
                ("eventSource", c_uint16),
                ("eventSize", c_uint32),
                ("eventTSOffset", c_uint32),
                ("eventTSOverFlow", c_uint32),
                ("eventCapacity", c_uint32),
                ("eventNumber", c_uint32),
                ("eventValid", c_uint32)]


# NOTE: This definition is currently not in use because
# of the large overhead it ensues on the processing. A
# single event container contains a large number of events
# (up to 4096). Instantiating a class for each results
# in long processing times and delays
class caerPolarityEvent(Structure):
    _pack_ = 1
    # The third element of the tuple is the size
    # of the field in bits
    _fields_ = [("valid_mark", c_uint32, 1),
                ("polarity", c_uint32, 1),
                ("y_addr", c_uint32, 15),
                ("x_addr", c_uint32, 15),
                ("timestamp", c_int32)]


class caerPolarityEventPacket(Structure):
    _pack_ = 1
    _fields_ = [("packetHeader", caerEventPacketHeader),
                # NOTE: The following is a field of variable length. The number
                # of elements is kept in the field "eventNumber" of "packetHeader"
                # We need to explicitly write it in order to facilitate different 
                # calculations regarding the struct's size and more
                ("events", caerPolarityEvent)]


class caerEventPacketContainer(Structure):
    _pack_ = 1
    _fields_ = [("eventPacketNumber", c_uint32),
                # NOTE: The following field is of variable length. The number of
                # pointers to eventPackets is as the value of the previous variable
                ("eventPackets", POINTER(caerEventPacketHeader))]
