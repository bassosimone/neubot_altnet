# __main__.py

#
# Copyright (c) 2011-2012, 2014
#     Nexa Center for Internet & Society, Politecnico di Torino (DAUIN)
#     and Simone Basso <bassosimone@gmail.com>.
#
# This file is part of Neubot <http://www.neubot.org/>.
#
# Neubot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Neubot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Neubot.  If not, see <http://www.gnu.org/licenses/>.
#

# Adapted from http_clnt.py's main()

import collections
import getopt
import logging
import sys

try:
    from neubot.poller import POLLER
    from neubot import utils_version
except ImportError:
    sys.exit("Neubot not found; please set PYTHONPATH accordingly")

from .http_clnt import HttpClient
from . import six

HTTP10 = six.b("HTTP/1.0")
CLOSE = six.b("close")
CONNECTION = six.b("connection")

class HttpClientSmpl(HttpClient):
    ''' Simple HTTP client '''

    def handle_connect(self, connector, sock, rtt, sslconfig, extra):
        self.create_stream(sock, self.connection_made, None,
          sslconfig, None, extra)

    def connection_made(self, stream):
        ''' Invoked when the connection is established '''
        context = stream.opaque
        address, port, paths, cntvec = context.extra
        if not paths:
            stream.close()
            return
        self.append_request(stream, 'GET', paths.popleft(), 'HTTP/1.1')
        self.append_header(stream, 'Host', '%s:%s' % (address, port))
        self.append_header(stream, 'User-Agent', utils_version.HTTP_HEADER)
        self.append_header(stream, 'Cache-Control', 'no-cache')
        self.append_header(stream, 'Pragma', 'no-cache')
        self.append_end_of_headers(stream)
        self.send_message(stream)
        context.body = self  # Want to print the body
        cntvec[0] += 1

    def handle_end_of_body(self, stream):
        HttpClient.handle_end_of_body(self, stream)
        context = stream.opaque
        cntvec = context.extra[3]
        if cntvec[0] <= 0:  # No unexpected responses
            raise RuntimeError('http_dload: unexpected response')
        cntvec[0] -= 1
        sys.stdout.flush()
        # XXX ignoring the "Connection" header for HTTP/1.0
        if (context.protocol == HTTP10 or
          context.headers.get(CONNECTION) == CLOSE):
            stream.close()
            return
        self.connection_made(stream)

    def write(self, data):
        ''' Write data on standard output '''
        # Remember that with Python 3 we need to decode data
        sys.stdout.write(six.bytes_to_string(data, 'utf-8'))

USAGE = 'usage: neubot http_clnt [-6Sv] [-A address] [-p port] path...'

def main(args):
    ''' Main function '''

    try:
        options, arguments = getopt.getopt(args[1:], '6A:p:Sv')
    except getopt.error:
        sys.exit(USAGE)
    if not arguments:
        sys.exit(USAGE)

    prefer_ipv6 = 0
    address = '127.0.0.1'
    sslconfig = 0
    port = 80
    level = logging.INFO
    for name, value in options:
        if name == '-6':
            prefer_ipv6 = 1
        elif name == '-A':
            address = value
        elif name == '-p':
            port = int(value)
        elif name == '-S':
            sslconfig = 1
        elif name == '-v':
            level = logging.DEBUG

    logging.getLogger().setLevel(level)

    handler = HttpClientSmpl(POLLER)
    handler.connect((address, port), prefer_ipv6, sslconfig,
      (address, port, collections.deque(arguments), [0]))
    POLLER.loop()

if __name__ == '__main__':
    main(sys.argv)
