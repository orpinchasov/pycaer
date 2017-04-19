#
# Module for unpacking of events data. Handles bits
# in order to increase processing speed to maximum.
#

import struct

VALID_MARK_SHIFT = 0
VALID_MARK_MASK = 0x00000001
POLARITY_SHIFT = 1
POLARITY_MASK = 0x00000001
Y_ADDR_SHIFT = 2
Y_ADDR_MASK = 0x00007FFF
X_ADDR_SHIFT = 17
X_ADDR_MASK = 0x00007FFF

def _get_polarity_event_data(data, shift, mask):
    return (data >> shift) & mask

def unpack_polarity_event_data(data):
    return (_get_polarity_event_data(data, VALID_MARK_SHIFT, VALID_MARK_MASK), \
            _get_polarity_event_data(data, POLARITY_SHIFT, POLARITY_MASK), \
            _get_polarity_event_data(data, Y_ADDR_SHIFT, Y_ADDR_MASK), \
            _get_polarity_event_data(data, X_ADDR_SHIFT, X_ADDR_MASK))
