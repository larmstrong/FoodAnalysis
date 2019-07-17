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
# Define classes

# Counter class
class IncrementDecrementCounter :

    def __init__(self) :
        # Class-specific attributes
        self.counter = 0

    def increment (self, by = 1):
        self.counter = self.counter + by
        return self.counter

    def decrement (self, by = 1):
        self.counter = self.counter - by
        return self.counter

    def get_value (self) :
        return self.counter


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
