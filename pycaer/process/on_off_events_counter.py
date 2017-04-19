#
# Module implementing an ON/OFF events counter.
#

from multiprocessing import Value

from .camera_events_handler import CameraEventsHandler
from ..dvs128.process_packets import unpack_polarity_event_data


class OnOffEventsCounter(CameraEventsHandler):
    def __init__(self):
        super(OnOffEventsCounter, self).__init__()

        self._on_events_count = Value('i', 0)
        self._off_events_count = Value('i', 0)

    def _handle_events(self, events):
        #for event in events:
        for data, timestamp in events:
            valid_mark, polarity, _, _ = unpack_polarity_event_data(data)

            if valid_mark == 0:
                continue

            if polarity == 1:
                # ON
                self._on_events_count.value += 1 
            else:
                # OFF
                self._off_events_count.value += 1 

    def get_events_count(self):
        return (self._on_events_count.value, self._off_events_count.value)

    def reset_events_count(self):
        self._on_events_count.value = 0
        self._off_events_count.value = 0
