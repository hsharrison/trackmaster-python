Python interface to Trackmaster treadmill
=========================================

Control a Trackmaster treadmill from Python, over a serial interface.
Tested with Python 2.7 and 3.4.

To install::

    pip install trackmaster

Example::

    from time import sleep
    from trackmaster import Treadmill

    t = Treadmill('/dev/ttyUSB0')

    t.speed = 6
    sleep(60)
    t.incline = 5
    sleep(60)
    t.incline = 10
    sleep(60)
    t.incline = 15
    sleep(5 * 60)
    t.auto_stop()
