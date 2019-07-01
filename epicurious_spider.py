#--------------------------------------------------------------------------------------------------
#% Import Libraries

import logging
import os
import scrapy

from scrapy.crawler import CrawlerProcess

#--------------------------------------------------------------------------------------------------
#% Define Constants

# Directory and filename constants.
CURRENTDIR = os.path.dirname(os.path.realpath(os.curdir))     # Current working directory
LOGFILENAME = 'epicurious_spider.log'

#--------------------------------------------------------------------------------------------------
#% Set up Logging

# Create a logger object
logger = logging.getLogger('epicurious_spider_log')
logger.setLevel(logging.DEBUG)

# Only do the handler work if none already exists.
if len(logger.handlers) == 0 :
    # Get the default console handler.
    ch = logging.StreamHandler()

    # Create a file handler as well
    logpath = os.path.join(CURRENTDIR, LOGFILENAME)
    fh = logging.FileHandler(logpath)
    fh.setLevel(logging.INFO)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

#--------------------------------------------------------------------------------------------------
#% Class definitions

class EpicuriousSpider (scrapy.Spider) :
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Class-specific constants
    name = "epicurious_spider"
    css_str = ' div#sitemapItems'
    xpath_ul_str = './/div/h3[contains(text(), "Recipes")]/following-sibling::ul'
    xpath_recipelink_str = './/li/a'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Class-specific methods
    def start_requests (self) :
        urls = ['https://www.epicurious.com/services/sitemap']
        for url in urls :
            logger.debug('***\n{}'.format(url))
            yield scrapy.Request(url=url, callback=self.parse_sitemap)

    def parse_sitemap (self, response) :
        # Obtain the sitemap items <div>.
        # Since the HTML may not be well-formed we start with a CSS selector.
        sitemapitems = response.css(self.css_str)
        logger.debug('Sitemapitems: {}'.format(sitemapitems.getall()))
        for sm_item in sitemapitems:
            # Within the sitemap div we want to select all <div>s following any <h3> tags that
            # include the word 'recipe.'
            ulitems = sitemapitems.xpath(self.xpath_ul_str)
            logger.debug('UL Items: {}'.format(ulitems))
            for ul_item in ulitems :
                # Process each UL separately in case we want to treat stock recipes differently
                # than member-submitted recipes.
                listitems = ul_item.xpath()
                for li_link in ul_item :


#--------------------------------------------------------------------------------------------------

spider_process = scrapy.crawler.CrawlerProcess()
spider_process.crawl(EpicuriousSpider)
spider_process.start()
