#
# Module implementing a type of a focus filter on the camera input.
# The filter gives priority to events at the focal point and forwards
# them as a result. Other events are ignored in a probabilistic fashion.
#
# TODO: Future features of this module:
# - Let the user choose the type of filter it requires. Whether 
#   a uniform circle or a gaussian, a circle or a square, etc.
# - Update the focal point during run without requiring to recreate
#   the entire probability matrix
# - Consider setting the std also during run. Currently it's not supported
#

import numpy as np
from scipy.stats import norm
from multiprocessing import Value, Event

from .camera_events_handler import CameraEventsHandler
from ..dvs128.process_packets import unpack_polarity_event_data


class FocusFilter(CameraEventsHandler):
    def __init__(self, output_queue, focal_point, focus_std=10, resolution=128):
        super(FocusFilter, self).__init__()

        self._output_queue = output_queue

        # NOTE: The focal point is currently using the same coordinate
        # system as the camera itself ((0,0) is lower left)
        self._focal_point_x = Value('i', focal_point[0])
        self._focal_point_y = Value('i', focal_point[1])
        self._update_focal_point = Event()

        self._focus_std = focus_std # Standard deviation of normal distribution used to create the filter
        self._resolution = resolution # A single number representing the square resolution (e.g. 128 for a 128x128 resolution)

        self._build_probability_matrix()
        self._create_random_number_list()

    def _build_probability_matrix(self):
        """Builds a matrix which states the probability of each
           pixel to pass the filter.
        """

        self._probability_matrix = np.zeros([self._resolution, self._resolution])

        norm_pdfs = list()

        # Create the distribution of the filter in a single axis
        for i in xrange(self._resolution * 2):
            # We use a mean of 0
            norm_i = norm(0, self._focus_std).pdf(i - self._resolution)
            norm_pdfs.append(norm_i)

        norm_pdfs /= max(norm_pdfs) # Normalize probability so all events at the focal point are handled

        # Combine both axes to create a single 2D filter matrix
        for i in xrange(self._resolution):
            for j in xrange(self._resolution):
                norm_i_index = i - self._focal_point_x.value + self._resolution
                norm_j_index = j - self._focal_point_y.value + self._resolution

                # TODO: This is the original line. Currently the filter is a uniform circle
                # self._probability_matrix[i, j] = norm_pdfs[norm_i_index] * norm_pdfs[norm_j_index]
                self._probability_matrix[i, j] = norm_pdfs[norm_i_index] * norm_pdfs[norm_j_index]
                if self._probability_matrix[i, j] > 0.30:
                    self._probability_matrix[i, j] = 1
                else:
                    self._probability_matrix[i, j] = 0

    def _create_random_number_list(self):
        # NOTE: The following is used instead of actually choosing a random value
        # for each pixel in real-time, which would be time-consuming
        self._random_numbers = list(np.random.random(10000))
        self._random_numbers_index = 0

    def _get_random_number(self):
        number = self._random_numbers[self._random_numbers_index]
        self._random_numbers_index = (self._random_numbers_index + 1) % 10000

        return number

    def _should_forward_event(self, data):
        valid_mark, polarity, y, x = unpack_polarity_event_data(data)

        if valid_mark == 0:
            return False

        random_number = self._get_random_number() 
        if random_number > self._probability_matrix[x, y]:
            # We want to drop this event
            return False
        else:
            return True

    def _handle_events(self, events):
        if self._update_focal_point.is_set():
            self._build_probability_matrix()
            self._update_focal_point.clear()

        forwarded_events = []

        for data, timestamp in events:
            if self._should_forward_event(data):
                forwarded_events.append((data, timestamp))

        self._output_queue.put_nowait(forwarded_events)

    def get_focal_point(self):
        return (self._focal_point_x.value, self._focal_point_y.value)
    
    def set_focal_point(self, x, y):
        # Handle cases of choosing values outside the screen.
        # NOTE: Sicne the values are altered here, in order
        # to get the actual value of the focal point one
        # should use the get method.
        x = max(0, int(x))
        y = max(0, int(y))

        self._focal_point_x.value = x
        self._focal_point_y.value = y

        self._update_focal_point.set()

    def set_focus_std(self, focus_std):
        self._focus_std = focus_std

        self._build_probability_matrix()


if __name__ == '__main__':
    from pycaer.process.demux import Demux
    from pycaer.graphics.render import Renderer

    render = Renderer(multiplier=2)
    focus_filter = FocusFilter(render.get_events_queue(), (10, 100))
    demux = Demux([focus_filter.get_events_queue()])

    render.start()
    focus_filter.start()
    demux.start()

    raw_input('Press any key to quit...')

    demux.stop()
    focus_filter.stop()
    render.stop()
