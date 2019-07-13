
# This is the main routine for the LArmstrong food analysis package

#--------------------------------------------------------------------------------------------------
# Import Libraries

import io
import os
import sys
import yaml

from neobolt.exceptions import ServiceUnavailable
import py2neo

# The following constants must be created before we can import local modules since they live in a
# ./src subdirectory.
app_directory = os.getcwd()
src_directory = os.path.join(app_directory, 'src')

# Append the src directory to the Python path.
sys.path.append(src_directory)

import apputils

#--------------------------------------------------------------------------------------------------
# Define global constants

# app_directory: Defined earlier
# src_directory: Defined earlier
config_filepath = os.path.join(src_directory, 'config.yaml')

#food_config = yaml.safe_load(config_stream)
food_config = apputils.read_configuration(config_filepath)
food_gr = py2neo.Graph()

#--------------------------------------------------------------------------------------------------
# FoodGraph

def load_food_graph (authentication, host, port, protocol):
    """
    load_food_graph: Loads the food graph database from Neo4J.
    Parameters:
      authentication: Two-par credentials tuple (username and password) used to authenticate to
        the Neo4J food database.
      host: Name of the host server where the Neo4J database is active.
      port: Communication port of the Neo4J database on the host server.
      protocol: Application-layer protocol used to communicate with the Neo4J database.
    """
    return(py2neo.Graph(auth=authentication, host=host, port=port, scheme=protocol))

#--------------------------------------------------------------------------------------------------
# Main module

def main():
    # Assure we are using the global food_gr database
    global food_gr

    # Read configuration and export required Neo4J values.
    neo4j_config = food_config['neo4j-database']
    current_version = neo4j_config['dbversion']
    auth_credentials = ( neo4j_config['user'], neo4j_config['pw'] )
    host = neo4j_config['host']
    port = neo4j_config['port']
    protocol = neo4j_config['scheme']

    logger = apputils.create_logger()
    logger.info('Logging enabled.')

    # Connect to the food graph
    food_gr = load_food_graph(
        authentication=auth_credentials, host=host, port=port, protocol=protocol)
    # Verify if the DB is active
    try:
        dbname = food_gr.database.name
    except ServiceUnavailable:
        print('Neo4J service not available. Is it running?')
        # 3 (ESRCH) is the value found in errno.h for "No such process."
        sys.exit(3)

    # The food graph DB is active. Let's start to process Epicurious


if __name__ == '__main__':
    main()
