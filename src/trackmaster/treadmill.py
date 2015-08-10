from serial import Serial
from trackmaster import raw


class Treadmill:
    def __init__(self, device, timeout=0.5):
        self.port = Serial(device, baudrate=4800, timeout=timeout)
        self.speed = None
        self.elevation = None

    def start_belt(self):
        """Start the belt."""
        self._command('1')

    def stop_belt(self):
        """Stop the belt."""
        self._command('2')

    def set_speed(self, speed):
        """Set belt speed.

        Parameters
        ----------
        speed : float
            Desired speed, in miles per hour.
            Will be rounded to nearest tenth of a mph.

        """
        ascii_speed = '{:04d}'.format(round(10 * speed))
        self._command('3', data=ascii_speed)

    def set_elevation(self, elevation):
        """Set treadmill elevation.

        Parameters
        ----------
        elevation : float
            Desired elevation (as a percent, e.g. 2.5).
            Will be rounded to the nearest 0.5%.

        """
        ascii_elevation = '{:04d}'.format(5 * round(elevation/0.5))
        self._command('4', data=ascii_elevation)

    def increment_speed(self):
        """Increase speed by 0.1 mph."""
        self.set_speed(self.get_set_speed() + 0.1)

    def decrement_speed(self):
        """Decrease speed by 0.1 mph."""
        self.set_speed(self.get_set_speed() - 0.1)

    def increment_elevation(self):
        """Increase elevation by 0.5%."""
        self.set_elevation(self.get_set_elevation() + 0.5)

    def decrement_elevation(self):
        """Decrease elevation by 0.5%."""
        self.set_elevation(self.get_set_elevation() - 0.5)

    def freeze_speed(self):
        """Stop any ongoing speed changes, leaving the belt at its current speed."""
        self.set_speed(self.get_actual_speed())

    def freeze_elevation(self):
        """Stop any ongoing elevation changes, leaving the treadmill at its current elevation."""
        self.set_elevation(self.get_actual_elevation())

    def auto_stop(self):
        """Immediately set speed and elevation to 0."""
        self._command('A')

    def cool_down(self):
        """Gradually set speed and elevation to 0."""
        self._command('B')

    def get_belt_running(self):
        """Check if the belt is running.

        Returns
        -------
        bool

        """
        response = self._status_request('0', 1)
        return int(response) == 33

    def get_actual_speed(self):
        """Get the current belt speed.

        Returns
        -------
        float

        """
        response = self._status_request('1', 4)
        return int(response) / 10

    def get_actual_elevation(self):
        """Get the current elevation.

        Returns
        -------
        float

        """
        response = self._status_request('2', 4)
        return int(response) / 10

    def get_set_speed(self):
        """Get the speed that the belt is currently set to.

        Returns
        -------
        float

        """
        response = self._status_request('3', 4)
        return int(response) / 10

    def get_set_elevation(self):
        """Get the elevation that the treadmill is currently set to.

        Returns
        -------
        float

        """
        response = self._status_request('4', 4)
        return int(response) / 10

    def _command(self, code, data=''):
        raw.command(self.port, code, data=data)

    def _status_request(self, code, response_length):
        return raw.status_request(self.port, code, response_length)
