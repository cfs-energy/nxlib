# Copyright 2026 Commonwealth Fusion Systems (CFS), all rights reserved.
# This entire source code file represents the sole intellectual property of CFS.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Internal utilities for nxlib logging."""

import logging
import os
import pickle
import socketserver
import struct
import threading
from contextlib import contextmanager
from logging.handlers import SocketHandler

import nxlib


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for logs from the NX subprocess."""

    def handle(self):
        while True:
            try:
                # Read the header to get the message length
                chunk = self.rfile.read(4)
                if not chunk:
                    break
                slen = struct.unpack(">L", chunk)[0]
                # Read and handle the remainder of the message
                record = logging.makeLogRecord(pickle.loads(self.rfile.read(slen)))
                logging.getLogger(record.name).handle(record)

            except ConnectionResetError:
                break


@contextmanager
def log_socket_listener():
    """Set up a socketserver to collect log messages from the NX subprocess"""
    server = socketserver.TCPServer(("127.0.0.1", 0), LogRecordStreamHandler)
    allocated_port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield allocated_port
    finally:
        server.shutdown()
        server.server_close()


class NxListingWindowHandler(logging.Handler):
    """Handler to emit log messages to the NX listing window."""

    def emit(self, record):
        try:
            nxlib.nxprint(self.format(record))
        except Exception:
            self.handleError(record)


def setup_subprocess_logging():
    """Set up logging for nxlib, with log messages from NX emitted to the main
    process.

    Any NX journal that uses ``import nxlib`` followed by
    ``logger = logging.getLogger()`` will have its log messages sent to the
    nxlib calling process in run_journal. Journals run graphically will
    have their log messages printed to the listing window.

    """
    port = os.getenv("NXLIB_LOG_SOCKET_PORT")
    level = os.getenv("NXLIB_LOG_LEVEL", logging.INFO)
    root_logger = logging.getLogger()

    try:
        # This will work if NXLIB_LOG_LEVEL is a string matching one of the logging
        # levels, e.g. "INFO", or if it was unset and defaults to logging.INFO
        root_logger.setLevel(level)
    except ValueError:
        # Try casting NXLIB_LOG_LEVEL to an integer. If the typecast fails,
        # the environment variable was set incorrectly and an exception will be raised
        root_logger.setLevel(int(level))

    if port and not any(
        isinstance(handler, SocketHandler) for handler in root_logger.handlers
    ):
        # If NXLIB_LOG_SOCKET_PORT is set, the subprocess (NX) will set up
        # a socket handler for its log messages that nxlib will listen to
        handler = SocketHandler("127.0.0.1", int(port))
        root_logger.addHandler(handler)


def add_listing_window_handler():
    """Add a special logging handler that works on the NX graphical listing window."""
    root_logger = logging.getLogger()
    listing_window_handler = NxListingWindowHandler()
    listing_window_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s")
    )
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(listing_window_handler)
