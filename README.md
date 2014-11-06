# Neubot API 2012.10.14

This is the networking API added to Neubot on 2012-10-14 when Neubot
0.4.15.5 was released. It is based on the `Poller` and `Pollable` APIs
as well as on the functionality provided by `utils_net`.

Since the 2012.10.14 API is only used by `mlabns` and by the `raw`
test, and since I'm currently working on Neubot plugins, I am
considering the possibility of factoring out the 2012.10.14 API from
Neubot, to include it in the `mlabns` and `raw` plugins only.

To this end, I need to create a subrepository. This one.

Below is the original text file describing this API. The description
is not up to date and needs some love:

## Neubot networking code

    Authors: Simone Basso <bassosimone@gmail.com>
    Version: 1.1
    Date: 2012/09/27
    X-Documents: cert.pem neubot/brigade.py neubot/connector.py
        neubot/handler.py neubot/listener.py neubot/net/poller.py
        neubot/net/stream.py neubot/pollable.py neubot/poller.py
        neubot/sslstream.py neubot/stream.py

The networking code is the core of Neubot.  It is based on a global POLLER
object (implemented in neubot/poller.py), which polls Pollable objects (defined
in neubot/pollable.py) for readability and writability.  The poller also takes
care of scheduling and dispatching future events, by using standard library's
event scheduler (Lib/sched.py).

At the moment of writing this note there are three different registered pollable
objects: connected stream sockets (neubot/stream.py), listening stream sockets
(neubot/listener.py), and connect-pending stream sockets (neubot/connector.py).
The complexity of listening and connect-pending stream sockets is partially
hidden by the handler (neubot/handler.py), which is an object that can handle
a set of connected stream sockets.

Extra support modules are: the SSL stream module (neubot/sslstream.py), which
extends the base stream module to add support for SSL (you typically don't
need to use this module directly, since neubot/stream.py imports and uses it
when SSL support is requested); the bucket brigade module (neubot/brigade.py),
loosely inspired by Apache brigades, which basically simplifies the task of
bufferising and reading incoming network data.  Worth mentioning is also the
127.0.0.1-only certificate file (cert.pem), created for the purpose of testing
the SSL code.

Finally, there are the backward-compatibility poller (neubot/net/poller.py) and
the backward compatibility stream (neubot/net/stream.py), which basically are
just the previous evolution of the networking code (the new code shares many
lines of code with the old one, the difference being mainly in how the new code
interfaces with protocol objects, e.g. HTTP).  Old files are kept in tree to
allow for a smooth migration from the old to the new networking code.
