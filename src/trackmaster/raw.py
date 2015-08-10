def check_for_errors(response, expected):
    if response == b'be':
        raise ValueError('Input Command Data Out of Range')
    if response == b'bf':
        raise ValueError('Illegal command or command not recognized')

    if response != expected:
        raise RuntimeError('Expected acknowledgment code {}, received {}'.format(
            response.decode('ascii').upper(), expected.decode('ascii').upper()
        ))


def command(port, code, data=''):
    """Send a command to the Trackmaster and wait for acknowledgment.

    Parameters
    ----------
    code : str
        A hexadecimal string (0-9, A-F) defining the command.
        This is the second digit listed in the documentation under "HEX"
        under both "A - INPUT COMMANDS" and "B - INPUT COMMAND ACKNOWLEDGMENT".
        For example, the command "Stop Belt" is listed as "A2" with acknowledgment code "B2".
        The `code` for "Stop Belt" is therefore ``'2'``.
    port : serial.Serial
        A |Serial| instance corresponding to the port connected to the Trackmaster.
    data : str, optional
        Additional data sent to the Trackmaster, required for some commands.

    """
    input_code = bytes('A' + code)
    acknowledgment_code = bytes('B' + code)

    port.write(input_code + bytes(data))
    response = port.read(2)
    check_for_errors(response, acknowledgment_code)


def status_request(port, code, response_length):
    """Send a status request to the Trackmaster and return the response.

    Parameters
    ----------
    code : str
        A hexadecimal string (0-9, A-F) defining the status request.
        This is the second digit listed in the documentation under "HEX"
        under both "C - STATUS REQUEST" and "D - STATUS RESPONSE".
        For example, the request "Xmit Belt Status" is listed as "C0" with response code "D0".
        The `code` for "Xmit Belt Status" is therefore ``'0'``.
    port : serial.Serial
        A |Serial| instance corresponding to the port connected to the Trackmaster.
    response_length : The number of bytes expected to be returned (not including the response code).

    Returns
    -------
    bytes

    """
    input_code = bytes('C' + code)
    response_code = bytes('D' + code)

    port.write(input_code)
    response = port.read(2)
    check_for_errors(response, response_code)

    return port.read(response_length)
