from __future__ import print_function, division
import sys
from serial import Serial
from trackmaster import raw

MIN_SPEED = 0.2
MAX_SPEED = 15
MAX_INCLINE = 25


class Treadmill(object):
    def __init__(self, port, verbose=False):
        """Interface to Trackmaster treadmill.

        Parameters
        ----------
        port : str
            The port at which with treadmill is connected.
            On Linux, likely to be ``/dev/ttyUSB0``.
        verbose : bool, optional
            If `True`, print input and output to treadmill.

        Attributes
        ----------
        device : |Serial|
            The |Serial| device representing the connection to the treadmill.
        speed : float
            The belt speed, in mph. Min is 0.2, max is 15.
            Changes will be reflected on the treadmill.
        incline : float
            The treadmill incline, in %. Min is 0, max is 25.
            Changes will be reflected on the treadmill.
        belt_running : bool
            Whether the belt is running.
            Not writable.
        verbose : bool

        """
        self.device = Serial(port, baudrate=4800, timeout=0.5)
        self.verbose = verbose
        self._speed = self.get_set_speed()
        self._incline = self.get_set_incline()

    @property
    def speed(self):
        return self._speed

    @property
    def incline(self):
        return self._incline

    @speed.setter
    def speed(self, value):
        rounded_speed = round(value, 1)

        if rounded_speed > MAX_SPEED:
            warn('Too fast! Setting speed to {} mph instead.'.format(MAX_SPEED))
            rounded_speed = MAX_SPEED

        if rounded_speed < MIN_SPEED:
            warn('Too slow! Stopping belt instead. It will have to be restarted.')
            stop_after = True
            rounded_speed = MIN_SPEED
        else:
            stop_after = False

        ascii_speed = '{:04d}'.format(int(round(10 * rounded_speed)))
        self._command('3', data=ascii_speed)
        self._speed = rounded_speed

        if not self.belt_running:
            self.start_belt()

        if stop_after:
            self.stop_belt()

    @incline.setter
    def incline(self, value):
        rounded_incline = round(2 * value) / 2

        if rounded_incline > MAX_INCLINE:
            warn('Too steep! Setting incline to {}% instead.'.format(MAX_INCLINE))
            rounded_incline = MAX_INCLINE

        if rounded_incline < 0:
            warn('Incline cannot be negative. Setting incline to 0% instead.')
            rounded_incline = 0

        ascii_incline = '{:04d}'.format(int(round(10 * rounded_incline)))
        self._command('4', data=ascii_incline)
        self._incline = rounded_incline

    @property
    def belt_running(self):
        return self._status_request('0', 1) == 3

    def start_belt(self):
        """Start the belt."""
        self._command('1')

    def stop_belt(self):
        """Stop the belt."""
        self._command('2')

    def increment_speed(self, by=0.1):
        """Increase speed by 0.1 mph (or more).

        Parameters
        ----------
        by : float, optional
            Amount to increase speed by, in mph.
            Default and minimum is 0.1.

        """
        self.speed += by

    def decrement_speed(self, by=0.1):
        """Decrease speed by 0.1 mph (or more).

        Parameters
        ----------
        by : float, optional
            Amount to decrease speed by, in mph.
            Default and minimum is 0.1.

        """
        self.speed -= by

    def increment_incline(self, by=0.5):
        """Increase incline by 0.5% (or more).

        Parameters
        ----------
        by : float, optional
            Amount to increase incline by, in %.
            Default and minimum is 0.5.

        """
        self.incline += by

    def decrement_elevation(self, by=0.5):
        """Decrease incline by 0.5% (or more).

        Parameters
        ----------
        by : float, optional
            Amount to decrease incline by, in %.
            Default and minimum is 0.5.

        """
        self.incline -= by

    def auto_stop(self):
        """Immediately set speed and incline to 0."""
        self._command('A')

    def get_actual_speed(self):
        """Get the current belt speed.

        Returns
        -------
        float

        Note
        ----
        Does not seem to be very accurate/responsive.

        """
        response = self._status_request('1', 4)
        return response / 10

    def get_actual_elevation(self):
        """Get the current incline.

        Returns
        -------
        float

        Note
        ----
        Does not seem to be very accurate/responsive.

        """
        response = self._status_request('2', 4)
        return response / 10

    def get_set_speed(self):
        """Get the speed that the belt is currently set to.

        Returns
        -------
        float

        Notes
        -----
        Should only be necessary for troubleshooting.
        ``Treadmill.speed` should work for most use cases.

        """
        response = self._status_request('3', 4)
        self._speed = response / 10
        return self.speed

    def get_set_incline(self):
        """Get the incline that the treadmill is currently set to.

        Returns
        -------
        float

        Notes
        -----
        Should only be necessary for troubleshooting.
        ``Treadmill.incline`` should work for most use cases.

        """
        response = self._status_request('4', 4)
        self._incline = response / 10
        return self.incline

    def _command(self, code, data=''):
        raw.command(self.device, code, data=data, verbose=self.verbose)

    def _status_request(self, code, response_length):
        return int(raw.status_request(self.device, code, response_length, verbose=self.verbose))


def warn(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
