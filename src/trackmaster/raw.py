from __future__ import print_function, division
from binascii import a2b_hex


class TreadmillError(RuntimeError):
    """An error arising from the treadmill itself."""


def communicate(dev, data, acknowledgment_code, verbose=False):
    if verbose:
        print('->', repr(data))
    dev.write(data)

    response = dev.read(1)
    if verbose:
        print('<-', repr(response))

    if response == a2b_hex('BE'):
        raise TreadmillError('Input Command Data Out of Range')
    if response == a2b_hex('BF'):
        raise TreadmillError('Illegal command or command not recognized')

    if response != acknowledgment_code:
        raise ValueError('Expected acknowledgment code {}, received {}'.format(
            acknowledgment_code, response
        ))


def command(dev, code, data='', verbose=False):
    """Send a command to the Trackmaster and wait for acknowledgment.

    Parameters
    ----------
    dev : serial.Serial
        A |Serial| instance corresponding to the device connected to the Trackmaster.
    code : str
        A hexadecimal string (0-9, A-F) defining the command.
        This is the second digit listed in the documentation under "HEX"
        under both "A - INPUT COMMANDS" and "B - INPUT COMMAND ACKNOWLEDGMENT".
        For example, the command "Stop Belt" is listed as "A2" with acknowledgment code "B2".
        The `code` for "Stop Belt" is therefore ``'2'``.
    data : str, optional
        Additional data sent to the Trackmaster, required for some commands.
    verbose : bool, optional
        If `True`, print input and output.

    """
    communicate(dev, a2b_hex('A' + code) + data.encode('ascii'), a2b_hex('B' + code), verbose=verbose)


def status_request(dev, code, response_length, verbose=False):
    """Send a status request to the Trackmaster and return the response.

    Parameters
    ----------
    dev : serial.Serial
        A |Serial| instance corresponding to the device connected to the Trackmaster.
    code : str
        A hexadecimal string (0-9, A-F) defining the status request.
        This is the second digit listed in the documentation under "HEX"
        under both "C - STATUS REQUEST" and "D - STATUS RESPONSE".
        For example, the request "Xmit Belt Status" is listed as "C0" with response code "D0".
        The `code` for "Xmit Belt Status" is therefore ``'0'``.
    response_length : int
        The number of bytes expected to be returned (not including the response code).
    verbose : bool, optional
        If `True`, print input and output.

    Returns
    -------
    bytes

    """
    communicate(dev, a2b_hex('C' + code), a2b_hex('D' + code), verbose=verbose)
    response = dev.read(response_length)
    if verbose:
        print('<-', repr(response))
    return response
