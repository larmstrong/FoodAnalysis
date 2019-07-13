"""
Provides a set of generic utilites that should be applicable to this of a variety of other projects.
"""

# Define the intended exported entities.
__all__ = [ 'read_configuration', 'set_configuration', 'get_configuration', 'create_logger' ]

#--------------------------------------------------------------------------------------------------
# Module and library imports

import io
import logging
import os
import yaml

#--------------------------------------------------------------------------------------------------
# Define module constants

_app_directory = os.getcwd()
#src_directory = os.path.join(app_directory, 'src')

_configuration = {}

#--------------------------------------------------------------------------------------------------
# Define exported configuration functions

def read_configuration (path = None) :
    """
    read_configuration: Reads configuration data from a YAML configuration file.
    Parameters:
      path: Path to the configuration file. If no parameter is passed then the configuration file
        is assumed to be named `config.yaml` and to reside in the current working directory.
    Returns: The configuration file that was read.
    """
    global _configuration

    # Use path if one is provided. Otherwise assume config.yaml in current working directory.
    cfg_path = path if path is not None else os.path.join(_app_directory, 'config.yaml')
    cfg_stream = io.open(cfg_path, 'r')

    # Load and return the configuration.
    _configuration = yaml.safe_load(cfg_stream)
    return _configuration

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def set_configuration (cfg) :
    global _configuration
    _configuration = cfg
    return _configuration

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_configuration () :
    global _configuration
    return _configuration

#--------------------------------------------------------------------------------------------------
# Define exported configuration functions

def create_logger () :
    """
    create_logger: Creates an application-specific logger with output to the console and to a file.
    """
    # Get the application logger name from the configuration.
    food_config = get_configuration()
    logger_config = food_config['logging']
    logname = logger_config['log-name']

    # Create a logger object
    logger = logging.getLogger(logname)
    logger.setLevel(logging.INFO)

    # Define the logging handlers.
    # Only do the handler work if none already exists.
    #if len(logger.handlers) == 0 :
    # Get the default console handler.
    ch = logging.StreamHandler()

    # Create a file handler as well
    logpath = os.path.join(_app_directory, logname + '.txt')
    fh = logging.FileHandler(logpath)
    fh.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

def get_logger () :
    cfg = get_configuration()
    logcfg = cfg['logging']
    loggername = logcfg['log-name']
    logger = logging.getLogger(name=loggername)
    return logger
