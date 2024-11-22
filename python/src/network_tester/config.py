# -*- coding: utf-8 -*-
"""Config parsing utilities
"""

from __future__ import absolute_import, print_function

import json
import logging
import os

import yaml


logger = logging.getLogger("network_tester_config")
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)
console_handler.setFormatter(formatter)


DEFAULTS = {"LOG_LEVEL": "DEBUG",
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


def parse_config_file(filename):
    """ Load configuration values from input file

    YAML and JSON are currently supported.

    Parameters:
    -----------
    filename: str
        Full path to the file containing the configuration.

    Returns:
    --------
    values: dict
        Loaded configuration values to use in the service.
    """

    ext = os.path.splitext(filename)[-1].lower()

    if ext in ['.yml', '.yaml']:
        with open(filename, 'r', encoding="utf8") as fil:
            values = yaml.load(fil.read(), Loader=yaml.FullLoader)
    elif ext == '.json':
        with open(filename, 'r', encoding="utf8") as fil:
            values = json.loads(fil.read())
    else:
        raise ValueError(f"Cannot parse config extension type {ext}")

    if not set(values.keys()).issubset(DEFAULTS.keys()):
        raise ValueError("Provided config is not a subset of needed values.")

    logger.debug("Vales from %s", filename)
    logger.debug(values)

    return values


def cascade_config(config_file=None):
    """ Build complete config file considering ENV vars, files, and DEFAULTS

    Value precedence:
        1. Environment variables
        2. Values in specified configuration file
        3. Defaults dictionary

    Parameters:
    -----------
    config_file: str,opt
        Full path to any desired configuration files.

    Returns:
    --------
    values: dict
        Configuration dictionary to be used in the service.
    """
    if 'LOG_LEVEL' in os.environ:
        set_log_level(logger, os.environ['LOG_LEVEL'])
    logger.debug("Cascading Config")
    # start with default values
    values = DEFAULTS.copy()

    # update with config file values, if present
    if config_file:
        config_file = os.path.expanduser(config_file)

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not"
                                    " found")
        file_values = parse_config_file(config_file)
        values.update(file_values)

    # Environment variables take highest precedence
    for envvar in values:
        if envvar in os.environ:
            new_val = os.environ[envvar]

            # integer
            if new_val.isdigit():
                new_val = int(new_val)
            # boolean
            if new_val in ['True', 'False']:
                new_val = bool(new_val)

            values[envvar] = new_val
            logger.debug("Evn variable %s is %s", envvar, new_val)

    return values


def set_log_level(log, level):
    """Set the log level for the logger
    """
    if isinstance(level, int):
        log.setLevel(level)
        return

    if level.lower() == "info":
        log.setLevel(logging.getLevelName("INFO"))
    elif level.lower() == "debug":
        log.setLevel(logging.getLevelName("DEBUG"))
    elif level.lower() == "warning":
        log.setLevel(logging.getLevelName("WARNING"))
    elif level.lower() == "error":
        log.setLevel(logging.getLevelName("ERROR"))
    log.debug("Log level has been set to: %s", level.lower())
