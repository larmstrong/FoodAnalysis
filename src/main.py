
# This is the main routine for the LArmstrong food analysis package

#--------------------------------------------------------------------------------------------------
# Import Libraries

import io
import os
import yaml

from neobolt.exceptions import ServiceUnavailable
from py2neo import Graph



import sys

#--------------------------------------------------------------------------------------------------
# Define global constants

CONFIG_FILEPATH = os.path.join(os.getcwd(), 'src', 'config.yaml')
CONFIG_STREAM = io.open(CONFIG_FILEPATH, 'r')
FOOD_CONFIG = yaml.safe_load(CONFIG_STREAM)
food_gr = Graph()

#--------------------------------------------------------------------------------------------------
# FoodGraph

def FoodGraph (authentication, host, port, protocol):
    return(Graph(auth=authentication, host=host, port=port, scheme=protocol))

#--------------------------------------------------------------------------------------------------
# Main module

def main():
    global food_gr
    global food_db

    neo4j_config = FOOD_CONFIG['neo4j-database']
    current_version = neo4j_config['dbversion']
    auth_credentials = (
        neo4j_config['user'],
        neo4j_config['pw'])
    host = neo4j_config['host']
    port = neo4j_config['port']
    protocol = neo4j_config['scheme']

    # Connect to the food graph
    food_gr = FoodGraph(authentication=auth_credentials, host=host, port=port, protocol=protocol)
    # Verify if the DB is active
    try:
        dbname = food_gr.database.name
    except ServiceUnavailable:
        print('Neo4J service not available. Is it running?')


if __name__ == '__main__':
    main()
