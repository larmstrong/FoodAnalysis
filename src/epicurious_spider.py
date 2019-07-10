#--------------------------------------------------------------------------------------------------
#% Import Libraries

import logging
import os
import scrapy

from scrapy.crawler import CrawlerProcess

#--------------------------------------------------------------------------------------------------
# Define Constants

# Directory and filename constants.
CURRENTDIR = os.path.dirname(os.path.realpath(os.curdir))     # Current working directory
LOGFILENAME = 'epicurious_spider.log'

#--------------------------------------------------------------------------------------------------
# Set up Logging

# Create a logger object
logger = logging.getLogger('epicurious_spider_log')
logger.setLevel(logging.INFO)

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
# Class definitions

class EpicuriousSpider (scrapy.Spider) :
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Class-specific constants
    name = "epicurious_spider"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # EpicuriousSpider.start_requests: Initiate the web-crawling process.
    # Parameters:
    #   self: Object instance
    def start_requests (self) :
        urls = ['https://www.epicurious.com/services/sitemap']
        for url in urls :
            logger.info('***\n{}'.format(url))
            yield scrapy.Request(url=url, callback=self.parse_sitemap)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # EpicuriousSpider.parse_sitemap: Process the basic web structure of the Epicurious.com
    #   sitemap. The primary flow is to obtain a list of year-organized URLs and then crawl each URL.
    # Parameters:
    #   self: Object instance
    #   response: Selector object provided by invoking parent method.
    def parse_sitemap (self, response) :
        css_str = ' div#sitemapItems'
        xpath_ul_str = './/div/h3[contains(text(), "Recipes")]/following-sibling::ul'
        xpath_recipelink_str = './/li/a/@href'

        # Obtain URLs from year-based sets of recipes from the Epicurious sitemap page.
        # (1) Since the HTML may not be well-formed, start with a CSS selector.
        # (2) Then select all <div>s following any <h3> tags that include the word 'recipe.'
        # (3) Then gather the URLs that are contained in individual list items.
        sitemapitems = response.css(css_str).xpath(xpath_ul_str).xpath(xpath_recipelink_str)
        logger.info(f'Sitemap items: {sitemapitems.getall()}')
        # Follow each URL for recipes.
        for link in sitemapitems:
            yield response.follow(url = link, callback = self.parse_yearpage)


    def parse_yearpage (self, response) :
        css_str = ' div#sitemapItems'
        xpath_ul_str = './/div/h1[contains(text(), "Recipes")]/following-sibling::ul'
        xpath_recipelink_str = './/li/a/@href'
        xpath_nextpage_str = './/div[@class = "paginate"]/a[@title="Next page"]/@href'

        # Obtain URLs for all recipes on a page
        recipeitems = response.css(css_str).xpath(xpath_ul_str).xpath(xpath_recipelink_str)
        logger.info(recipeitems.getall())
        for recipe_link in recipeitems:
            pass

        # Is there another page for this year?
        nextpageitems = response.css(css_str).xpath(xpath_nextpage_str)
        logger.info (f'Next Page: { nextpageitems.get() }')
        if len(nextpageitems) > 0 :
            nextpage_link = nextpageitems.get()
            yield response.follow(url = nextpage_link, callback = self.parse_yearpage)

    def parse_recipe (self, response) :
        pass

#--------------------------------------------------------------------------------------------------

spider_process = scrapy.crawler.CrawlerProcess()
spider_process.crawl(EpicuriousSpider)
spider_process.start()
