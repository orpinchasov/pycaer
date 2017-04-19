""" Module for rendering camera events on screen.

Uses the simple PyGame engine.
Visual processing is processor-time consuming. Currently it seems as if
it's best to perform it in its own process.

TODO:
- The option to remove user pixels
"""

import time
import signal
import pygame

from multiprocessing import Process, Event, Queue
from Queue import Empty

from ..dvs128.process_packets import unpack_polarity_event_data


class Renderer(Process):
    # NOTE: This is currently relevant only to DVS128
    FOV_WIDTH = 128
    FOV_HEIGHT = 128

    def __init__(self, fps=30, multiplier=1):
        super(Renderer, self).__init__()

        self._multiplier = multiplier
        self._fps = fps

        # A list of pixels to be drawn in each frame
        self._static_pixels = []

        self._events_queue = Queue()
        self._user_queue = Queue()
        self._stop_running = Event()

    def _init_signal_handling(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def _init_rendering(self):
        pygame.init()

        self._clock = pygame.time.Clock()

        self._screen_width = self.FOV_WIDTH * self._multiplier 
        self._screen_height = self.FOV_HEIGHT * self._multiplier

        self._surface = pygame.Surface((self.FOV_WIDTH, self.FOV_HEIGHT))
        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))

    def _update_user_events(self):
        try:
            events = self._user_queue.get_nowait()
        except Empty:
            return

        # NOTE: "position" is a tuple of the type (x,y).
        # "color" is a tuple of the type (r,g,b).
        # "is_static" is True for static pixels (which always stay)
        # or False for pixels which are updated only for a single frame.
        for position, color, is_static in events:
            if is_static:
                self._static_pixels.append((position, color))

            x, y = position
            self._surface.set_at((x, 127 - y), color)

    def _update_camera_events(self):
        try:
            events = self._events_queue.get_nowait()
        except Empty:
            return

        for data, timestamp in events:
            valid_mark, polarity, y, x = unpack_polarity_event_data(data)

            if valid_mark == 0:
                continue

            if polarity == 0:
                color = (255, 0, 0)        
            elif polarity == 1:
                color = (0, 255, 0)

            # NOTE: The (0,0) coordinate of the DVS128 camera is at the
            # *lower* left corner (like in OpenGL)
            self._surface.set_at((x, 127 - y), color)

    def _render(self):
        last_frame_time = 0

        while not self._stop_running.is_set():
            self._surface.fill((0, 0, 0))

            for position, color in self._static_pixels:
                x, y = position
                self._surface.set_at((x, 127 - y), color)

            current_time = time.time()
            while current_time - last_frame_time < 1.0 / self._fps:
                self._update_user_events()
                self._update_camera_events()
                
                current_time = time.time()

            self._clock.tick()

            # Print framerate and playtime in titlebar.
            text = "FPS: {0:.2f}".format(self._clock.get_fps())
            pygame.display.set_caption(text)

            pygame.transform.scale(self._surface, \
                                   (self._screen_width, self._screen_height), \
                                   self._screen)

            # NOTE: The following is a serious time-consuming function
            pygame.display.flip()

            # Flush pipe to remove all events which were not drawn in this frame
            while not self._events_queue.empty():
                self._events_queue.get_nowait()

            last_frame_time = current_time

    def get_events_queue(self):
        return self._events_queue

    def get_user_queue(self):
        return self._user_queue

    def run(self):
        self._init_signal_handling()
        self._init_rendering()

        self._render()

    def stop(self):
        self._stop_running.set()


if __name__ == "__main__":
    from pycaer.process.demux import Demux

    renderer = Renderer(multiplier=3)
    demux = Demux([renderer.get_events_queue()])

    renderer.start()

    demux.start()

    raw_input('Press any key to quit...')

    demux.stop()

    renderer.stop()
