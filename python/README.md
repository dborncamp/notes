# Network Tester

This is basically a chaos tester for our networks.
The version of Python that this is based on is 3.11 since [Hypatia](https://github.com/snkas/hypatia) depends on `imp` being in the standard library.
While we do not yet use Hypatia this doesn't really matter, but it is likely to be used in the future.

## Configuration

The defaults are configurable by either config file or environment variable in the following cascade of value precedence:

1. Environment variables
2. Values in specified configuration file
3. Defaults dictionary

The defaults are:

```json
{
    "LOG_LEVEL": "INFO",
    "LISTEN_HOST": "127.0.0.1",
    "LISTEN_PORT": 8080,
    "BROADCAST_HOST": "0.0.0.0",
    "BORADCAST_PORT": 8081,
    "PERCENT_DROPPED": 5,
    "LATENCY": 3,
    "LATENCY_SIGMA": 2,
    "PACKET_SIZE": 1024,
    "NUMBER_OF_CONCURRENT_TASKS": 20,
    "PROTOCOL": "udp"
}
```

**NOTE** It currently only echos back to the listen host and port, it does not re-broadcast so those variables are ignored.

While the main goal of this code is to test UDP connections, there are also functions to handle TCP here and add the same kind of response noise.

## Development

### Local

To develop locally, set up a local environment.
I chose to use Conda since it easily allows me to change between versions of python

```bash
conda create -n nettest python=3.11 pyyaml aioudp -y
conda activate nettest
python src/network_tester/main.py
```

In another terminal either...

Run netcat to interface with the server via UDP `nc -u 127.0.01 8080`.
I pasted the following to test it and this was the response (new line was recieved and re-sent):

```txt
hi
there
how
Are
you?

Are

there
how
hi
you?
```

Or for a TCP connection you can use curl.
Then in another terminal run `curl --header "Content-Type: application/json" --request POST --data '{"username":"xyz","password":"xyz"}'  http://localhost:8080 -vv --http0.9`.
It should echo back the json.
