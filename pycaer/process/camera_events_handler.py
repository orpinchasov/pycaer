""" Module which implements a generic events handler from the camera.

The handler runs as a separate process with its own queue.
The queue should be passed to an events producer (for example,
the Demux module). The process is then run and reads the events
from the queue. Each event container packet triggers a call
to the handler function, which is implemented in each handler
locally.
"""

import signal
import ctypes
from multiprocessing import Process, Queue, Event
from Queue import Empty


class CameraEventsHandler(Process):
    def __init__(self):
        super(CameraEventsHandler, self).__init__()

        self._events_queue = Queue()
        self._stop_running = Event()

    def get_events_queue(self):
        """Get the events queue of the handler to be passed
        to the events producer.
        """

        return self._events_queue

    def remove_all_events(self):
        while not self._events_queue.empty():
            try:
                self._events_queue.get_nowait()
            except Empty:
                # NOTE: Apparently this is possible
                break

    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        while not self._stop_running.is_set():
            # Added a timeout to enable the process to check for stopping
            # signal even if the demuxer has stopped and the queue is empty.
            try:
                events = self._events_queue.get(timeout=0.1)
            except Empty:
                continue

            self._handle_events(events)

    def stop(self):
        self._stop_running.set()
