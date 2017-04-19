#
# Module which implements a demuxer for the camera output.
# Several handlers may register to the different camera events
# and they will be called in succession for each event.
#

from multiprocessing import Process, Value, Event
import signal

from ..dvs128.controller import Controller
from ..dvs128.consts import *
from ..dvs128.packet_definitions import POLARITY_EVENT


# A process which collects the camera's events and passes
# them to registered handler functions
class Demux(Process):
    def __init__(self, handlers_queues):
        super(Demux, self).__init__()

        self._camera = Controller()
        self._stop_running = Event()

        # NOTE: Initially I tried to enable queue registration while
        # the demux process was actually running. It's problematic
        # since queues themselves cannot be passed between processes
        # unless they are used with a manager, which introduces considerable
        # overhead to the process. Currently my best solution is to allow
        # only initialization of queues upon initialization of the
        # demux process.
        # The events are then handled in the context of the handlers.
        # They may pull the events from the queue whenever they want
        # to do it.
        # Also note that this method does not allow chaining of events.
        # Currently unused, or at least, might be implemented by each
        # handler separately.

        # A list of queues held by the handlers. The camera's output
        # is sent to each of the queues.
        self._handlers_queues = handlers_queues
        
    def _init_signal_handling(self):
        # NOTE: Required in order to ignore KeyboardInterrupt
        # which may be sent to the parent process. The parent
        # process should always call the stop_running method
        # to cause a proper cleanup
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def _init_camera(self):
        self._camera.open_device()
        self._camera.send_default_configuration()
        self._camera.set_configuration(CAER_HOST_CONFIG_DATAEXCHANGE, \
                                       CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING, \
                                       True)
        # TODO: Added temporarily. Think about the interface to control
        # the camera configuration from outside this module. Notice that
        # we probably cannot create the camera object outside this class and pass it
        # to here since the object has to be created in the context of the processing
        # process
        #self._camera.set_configuration(DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFFOFF, 5)
        #self._camera.set_configuration(DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFFON, 4433455)
        #self._camera.set_configuration(DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_DIFF, 13125)
        self._camera.start_data()

    def _fini_camera(self):
        self._camera.stop_data()
        self._camera.close_device()

    def run(self):
        self._init_signal_handling()

        # NOTE: This has to happen in the context of the CHILD process
        # or else the data would be kept in the parent process
        self._init_camera()

        while not self._stop_running.is_set():
            event_packet = self._camera.get_data()
            if event_packet is None:
                continue

            [header, packet] = event_packet.get_event_packet(POLARITY_EVENT)
            if header is None:
                continue

            events = packet.get_all_events()

            # Send all events over the queue to all registered processes
            # NOTE: The processes which hold the queues should be
            # stopped *after* the demux process stops
            for queue in self._handlers_queues:
                queue.put_nowait(events)

        self._fini_camera()

    def stop(self):
        self._stop_running.set()


# Usage example
if __name__ == '__main__':
    import time
    from on_off_events_counter import OnOffEventsCounter

    h = OnOffEventsCounter()
    d = Demux([h.get_events_queue()])

    h.start()
    d.start()

    while True:
        try:
            print h.get_events_count()
            h.reset_events_count()
            time.sleep(0.01)
        except KeyboardInterrupt:
            break

    d.stop()
    h.stop()
