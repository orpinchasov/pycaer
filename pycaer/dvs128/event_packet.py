#
# Module of generic event packets and their contents.
# All relevant classes are held in a single file according
# to their type.
#
# Classes here follow the API described in:
# - /usr/include/libcaer/events/packetContainer.h
#

import ctypes

from packet_definitions import caerEventPacketHeader
from packet_definitions import POLARITY_EVENT
from polarity_event_packet import PolarityEventPacket


class EventPacketHeader(object):
    def __init__(self, libcaer, event_packet_header_address):
        self._libcaer = libcaer
        self._event_packet_header = ctypes.cast(event_packet_header_address,
                                                ctypes.POINTER(caerEventPacketHeader)).contents

    def get_number_of_events(self):
        return self._event_packet_header.eventNumber

    def get_number_of_valid_events(self):
        # NOTE: Notice the confusing naming convention...
        # This is the *number* of events rather than whether they
        # are valid as it might be possible to consider
        return self._event_packet_header.eventValid


class EventPacketContainer(object):
    def __init__(self, libcaer, container_address):
        self._libcaer = libcaer
        # The address is saved for the free method. I could not
        # find a proper way to use ctypes.addressof which seems
        # convenient
        self._container_address = container_address
        self._container = container_address.contents

    def __del__(self):
        self._free()
    
    def _free(self):
        self._libcaer.caerEventPacketContainerFree(self._container_address)

    def get_number_of_event_packets(self):
        return self._container.eventPacketNumber

    def get_event_packet(self, index):
        # NOTE: The following is an array of pointers to event packets.
        # The access is quiet complicated. We get to the desired index
        # using simple array indexing 
        event_packet_header_address = \
            ctypes.cast(ctypes.addressof(self._container.eventPackets) +
                            ctypes.sizeof(ctypes.POINTER(caerEventPacketHeader)) * index,
                        ctypes.POINTER(ctypes.POINTER(caerEventPacketHeader))).contents

        if not event_packet_header_address:
            return (None, None)

        # Parse the packet according to its type and return the
        # appropriate object
        if index == POLARITY_EVENT:
            return (EventPacketHeader(self._libcaer, event_packet_header_address),
                    PolarityEventPacket(self._libcaer, event_packet_header_address))

        return (None, None)
