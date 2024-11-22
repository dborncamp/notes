"""An asyncrynous network tester"""

import asyncio
import logging
import os

from network_tester import tester
from network_tester import config


logger = logging.getLogger("network_tester_main")
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter(
    "{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(formatter)


def main(config):
    """Lets get this thing started"""
    logger.debug("Configs: %s", config)
    t = tester.Tester(config)
    if config['PROTOCOL'] == 'tcp':
        asyncio.run(t.main_tcp())
    elif config['PROTOCOL'] == 'udp':
        asyncio.run(t.main_udp())
    else:
        raise ValueError("Please choose a protocol from 'tcp' or 'udp'.")
    logger.warning("Finished with the server")


if __name__ == "__main__":
    configfile = 'config.json'
    if os.path.exists(configfile):
        configs = config.cascade_config(config_file=configfile)
    else:
        configs = config.cascade_config()
    config.set_log_level(logger, configs['LOG_LEVEL'])
    main(configs)
