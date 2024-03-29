"""
This is the main routine for the LArmstrong food analysis package. It serves as the main driver
for reading food databases and then creating the Neo4J database.
"""

#--------------------------------------------------------------------------------------------------
# Import Libraries

# Preliminary simple imports
import os
import sys

# The following constants must be created before we can import local modules since they live in
# the ./src subdirectory. The src subdirectory first needs to be added to the Python search path.
app_directory = os.getcwd()
src_directory = os.path.join(app_directory, 'src')
sys.path.append(src_directory)

# Remaining simple imports
import apputils
import datetime
import errno
import io
import logging
import py2neo
import scrapy
import sys
import yaml

# Aliased imports
# import epicurious_spider as ep
import traceback as tb
import epicurious_spider as es

# Selective imports
from neobolt.exceptions import ServiceUnavailable


#--------------------------------------------------------------------------------------------------
# Define global constants

# app_directory: Defined earlier
# src_directory: Defined earlier
config_filepath = os.path.join(src_directory, 'config.yaml')

#food_config = yaml.safe_load(config_stream)
food_config = apputils.read_configuration(config_filepath)
food_gr = py2neo.Graph()

#logging.getLogger('epicurious_log').handlers[0]
logger=logging.getLogger('epicurious_spider_log')


#--------------------------------------------------------------------------------------------------
# FoodGraph

def load_food_graph (authentication, host, port, protocol):
    """
    Loads the food graph database from Neo4J.
    Parameters:
      authentication: Two-par credentials tuple (username and password) used to authenticate to
        the Neo4J food database.
      host: Name of the host server where the Neo4J database is active.
      port: Communication port of the Neo4J database on the host server.
      protocol: Application-layer protocol used to communicate with the Neo4J database.
    """
    logger.debug('Loading food graph DB')
    gr = py2neo.Graph(auth=authentication, host=host, port=port, scheme=protocol)
    # Verify if the DB is active
    try:
        dbname = gr.database.name
    except ServiceUnavailable:
        # Log the error and show traceback.
        logger.error('Neo4J service not available. Is it running?')
        tb.print_last()

        # Exit the application with error code.
        sys.exit(errno.ECONNREFUSED)
    else:
        return gr


#--------------------------------------------------------------------------------------------------
# Main module

def main():
    # Assure we are using the global food_gr database
    global food_gr

    # Read configuration and export required Neo4J values.
    neo4j_config = food_config['neo4j-database']
    current_version = neo4j_config['dbversion']
    credentials = ( neo4j_config['user'], neo4j_config['pw'] )
    host = neo4j_config['host']
    port = neo4j_config['port']
    protocol = neo4j_config['scheme']

    # Connect to the food graph
    food_gr = load_food_graph(authentication=credentials, host=host, port=port, protocol=protocol)

    # Verify the DB name
    dbname = food_gr.database.name
    # The food graph DB is active. Let's start to process Epicurious
    logger.info(f'Neo4J {dbname} DB currently has {len(food_gr.nodes)} nodes.')

    # Call the Epicurious parsing routines
    spider_process = scrapy.crawler.CrawlerProcess()
    spider_process.crawl(es.EpicuriousSpider, gdb=food_gr)
    spider_process.start()

#--------------------------------------------------------------------------------------------------
# Module code external to any function.

if __name__ == '__main__':
    # Initialize logging.
    logcfg_path = os.path.join(src_directory, 'logging.config')
    logging.config.fileConfig(logcfg_path)
    logger.debug(f'***Start new run at {str(datetime.datetime.now())}***')
    # Invoke the main function.
    main()

help(es.EpicuriousSpider.start_requests)
