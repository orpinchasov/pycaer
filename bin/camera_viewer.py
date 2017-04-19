""" Module implementing a simple video renderer which presents
the camera output on screen.

TODO: Possible optimization methods:
1) Move event processing and video rendering to the same process since moving
   the data between processse takes a lot of time.
2) Accumulating data and less calls to pipe send (currently done per pixel)
3) Keep track of the events timestamps and drop those which are too much in the past
"""

import pygame
from time import time

from multiprocessing import Process, Pipe

from pycaer.dvs128.controller import Controller
from pycaer.dvs128.consts import *

# NOTE: Maximum frame rate depends on many more
# factors such as whether we are working over X or not...
MULTIPLIER = 2


def render(screen, events_pipe):
    black = (0, 0, 0)
    white = (255, 255, 255)

    clock = pygame.time.Clock()

    last_frame_time = 0

    while True:
        screen.fill(black)

        current_time = time()

        # Run at 30 fps
        while current_time - last_frame_time < 0.034:
            updates = events_pipe.recv()
            for update in updates:
                polarity, x, y = update 

                if polarity == 0:
                    color = (255, 0, 0)        
                else:
                    color = (0, 255, 0)

                screen.fill(color, \
                            ((127 - x) * MULTIPLIER, \
                             (127 - y) * MULTIPLIER, \
                             MULTIPLIER, \
                             MULTIPLIER))
            
            current_time = time()

        # Flush pipe to remove all events which were not draw in this frame
        while events_pipe.poll():
            events_pipe.recv()

        clock.tick()

        # Print framerate and playtime in titlebar.
        text = "FPS: {0:.2f}".format(clock.get_fps())
        pygame.display.set_caption(text)

        # A serious time-consuming function. The use of this function
        # seems to justify the removal of it to a different process.
        pygame.display.flip()

        last_frame_time = current_time

def handle_event_packet(event_packet, events_pipe):
    [header, packet] = event_packet.get_event_packet(1)
    number_of_events = header.get_number_of_events()

    updates = []
    for i in xrange(max(1, number_of_events)):
        event = packet.get_event(i)
        polarity = event.get_polarity()
        x = event.get_x()
        y = event.get_y()

        updates.append((polarity, x, y))

    events_pipe.send(updates)

def main():
    pygame.init()

    size = width, height = 128 * MULTIPLIER, 128 * MULTIPLIER
    FPS = 30

    screen = pygame.display.set_mode(size)

    parent_pipe, child_pipe = Pipe()
    rendering_process = Process(target=render, args=(screen, child_pipe))
    rendering_process.start()

    c = Controller()
    c.open_device()
    c.send_default_configuration()
    c.start_data()
    c.set_configuration(CAER_HOST_CONFIG_DATAEXCHANGE, CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING, True)

    while True:
        try:
            # NOTE: We are keeping the handling of the events as in real time as possible

            event_packet = c.get_data()
            handle_event_packet(event_packet, parent_pipe)
        except KeyboardInterrupt:
            break

    rendering_process.terminate()
    
    c.stop_data()
    c.close_device()

if __name__ == "__main__":
    main()
