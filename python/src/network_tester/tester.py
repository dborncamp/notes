# -*- coding: utf-8 -*-
"""A class for making netowrking chaos
"""

import asyncio
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import QueueHandler, QueueListener
import queue
import random
import signal

import aioudp

from network_tester.config import set_log_level


class Tester:
    """Basically a chaos monkey for a network using Python"""
    def __init__(self, configs):
        # Log without blocking the event loop by creating a new QueueListener thread
        que = queue.Queue(-1)  # no limit on size
        queue_handler = QueueHandler(que)
        handler = StreamHandler()
        listener = QueueListener(que, handler)
        self.logger = getLogger("network_tester_tester")
        self.logger.addHandler(queue_handler)
        formatter = Formatter(
            "{asctime} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        listener.start()
        set_log_level(self.logger, configs['LOG_LEVEL'])

        self.listen_host = configs['LISTEN_HOST']
        self.listen_port = configs['LISTEN_PORT']

        self.latency = configs['LATENCY']
        self.latency_sig = configs['LATENCY_SIGMA']
        self.packetsize = configs['PACKET_SIZE']
        self.percent_dropped = configs['PERCENT_DROPPED']
        self.protocol = configs['PROTOCOL']
        self.concurrent = configs['NUMBER_OF_CONCURRENT_TASKS']

    async def handle_tcp_client(self, reader, writer):
        """Handle a TCP client and echo back the data that it gives"""
        try:
            data = await reader.read(self.packetsize)
            message = data.decode()
            addr = writer.get_extra_info('peername')
            self.logger.debug("Received %s from %s", message, addr)

            await asyncio.sleep(max(random.gauss(self.latency, self.latency_sig), 0))

            self.logger.debug("Send: %s", message)
            writer.write(data)
            await writer.drain()

            self.logger.info("Close the connection")
        except asyncio.CancelledError:
            pass
        finally:
            writer.close()
            self.logger.info("Closed")

    async def main_tcp(self):
        """Main function for the tester"""
        self.logger.info("Starting Async server at: %s:%s",
                         self.listen_host, self.listen_port)

        if self.protocol == 'tcp':
            self.logger.info("Starting TCP protocol")
            server = await asyncio.start_server(
                    self.handle_tcp_client,
                    self.listen_host,
                    self.listen_port
                )

            async with server:
                await server.serve_forever()

    async def sleeper(self, async_queue):
        """Sleep on the UDP connection"""
        while True:
            self.logger.debug("Sleeping")
            timer, message, connection = await async_queue.get()
            self.logger.debug("Sleeping a task with message: %s", message)
            await asyncio.sleep(timer)
            await connection.send(message)
            async_queue.task_done()

    async def main_udp(self):
        """Main Handler for the UDP connection"""
        self.logger.info("Starting UDP")
        async_queue = asyncio.Queue()

        # Serve the incomming connection by adding the packets to the queue so that we can sleep
        # on them
        async def handler(connection):
            while True:
                async for message in connection:
                    self.logger.info("Got a message %s", message)
                    await async_queue.put((max(random.gauss(self.latency, self.latency_sig), 0),
                               message, connection))

        # Create some taskers to concurrently handle the incomming packets
        taskers = [asyncio.create_task(self.sleeper(async_queue)) for _ in range(self.concurrent)]

        # Make sure that we properly handle SIGINT and SIGTERM
        loop = asyncio.get_running_loop()
        stop = loop.create_future()

        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
        async with aioudp.serve(self.listen_host, self.listen_port, handler):
            self.logger.info("Seving on %s:%s", self.listen_host, self.listen_port)
            await stop  # Serve forever

        self.logger.info("Done with Async server")
