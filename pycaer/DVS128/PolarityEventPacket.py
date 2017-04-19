#
# Module for the specific polarity event packets.
#
# Definitions are taken from:
# - /usr/include/libcaer/events/polarity.h
#

from PacketDefinitions import caerPolarityEvent, caerPolarityEventPacket

import ctypes

class PolarityEvent(object):
    def __init__(self, event_address):
        self._event = event_address.contents

    def is_valid(self):
        return self._event.valid_mark

    def get_polarity(self):
        return self._event.polarity

    def get_y(self):
        return self._event.y_addr

    def get_x(self):
        return self._event.x_addr
    
    def get_timestamp(self):
        return self._event.timestamp 

class PolarityEventPacket(object):
    def __init__(self, libcaer, event_packet_address):
        self._libcaer = libcaer
        self._event_packet = ctypes.cast(event_packet_address, \
                                         ctypes.POINTER(caerPolarityEventPacket)).contents

    # NOTE: This function is now deprecated and should be replaced
    # by the function "get_all_events". The latter is faster and does
    # not instantiate a class per event. This improves the performance also
    # when data has to be sent through pipes between processes.
    def get_event(self, index):
        if index < 0 or index >= self._event_packet.packetHeader.eventCapacity:
            return None

        event_address = \
            ctypes.cast(ctypes.addressof(self._event_packet.events) + \
                            ctypes.sizeof(ctypes.POINTER(caerPolarityEvent)) * index, \
                        ctypes.POINTER(caerPolarityEvent))

        return PolarityEvent(event_address)

    def get_all_events(self):
        events_address = ctypes.addressof(self._event_packet.events)

        number_of_events = self._event_packet.packetHeader.eventNumber

        events_buffer = ctypes.cast(events_address, ctypes.POINTER(ctypes.c_int))

        events = []
        # TODO: This -1 should not be here. There's an off-by-1 here somewhere.
        # If I do read the data there I get garbage
        for i in xrange(number_of_events - 1):
            events.append((events_buffer[i * 2], events_buffer[i * 2 + 1]))

        return events
