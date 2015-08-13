from __future__ import print_function, division
from binascii import a2b_hex


def communicate(dev, data, acknowledgment_code):
    dev.write(data)
    response = dev.read(1)

    if response == a2b_hex('BE'):
        raise ValueError('Input Command Data Out of Range')
    if response == a2b_hex('BF'):
        raise ValueError('Illegal command or command not recognized')

    if response != acknowledgment_code:
        raise RuntimeError('Expected acknowledgment code {}, received {}'.format(
            acknowledgment_code, response
        ))


def command(dev, code, data=''):
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

    """
    communicate(dev, a2b_hex('A' + code) + data.encode('ascii'), a2b_hex('B' + code))


def status_request(dev, code, response_length):
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
    response_length : The number of bytes expected to be returned (not including the response code).

    Returns
    -------
    bytes

    """
    communicate(dev, a2b_hex('C' + code), a2b_hex('D' + code))
    return dev.read(response_length)
