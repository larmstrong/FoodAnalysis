"""
Epicurious spider processes and addition webscraping code.
"""

# -------------------------------------------------------------------------------------------------
# Import Libraries

# Simple imports
import logging
import py2neo
import os
import scrapy

# Selective imports
from collections import Counter
from scrapy.crawler import CrawlerProcess


#--------------------------------------------------------------------------------------------------
# Define Constants

MAX_DIRECTORY_PAGES = 100
MAX_RECIPES = 100

#--------------------------------------------------------------------------------------------------
# Global variable and object definitions

# Directory and filename constants.
current_directory = os.path.realpath(os.curdir)     # Current working directory
src_directory = os.path.join(current_directory, "src")

n_recipes = 0

logger = logging.getLogger('epicurious_spider_log')

# Spider class

class EpicuriousSpider (scrapy.Spider) :

    # Class-specific constants
    name = "epicurious_spider"

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, gdb) :
        """
        EpicuriousSpider.__init__: Create a new spider object for the Epicurious website.
        Parameters:
          self: Object instance
          gdb: Graph database to read/write.
        """
        logger.info(f'Creating new EpicuriousSpider for {gdb.database.name}')
        # Assign the passed-in graph database.
        self.gdb = gdb
        self.n_directory_pages = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def start_requests (self) :
        """
        EpicuriousSpider.start_requests: Initiate the web-crawling process.

        Parameters:
            self: Object instance
        """
        logger.info('Starting Epicurious crawler process.')
        urls = ['https://www.epicurious.com/services/sitemap']
        for url in urls :
            logger.info(f'***{url}')
            yield scrapy.Request(url=url, callback=self.parse_sitemap)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse_sitemap (self, response) :
        """
        Process the basic web structure of the Epicurious.com sitemap.
        The flow obtains a list of year-organized URLs and then crawls each URL.

        Parameters:
            self: Object instance
            response: Selector object provided by invoking parent method.
        """
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
            if self.n_directory_pages <= MAX_DIRECTORY_PAGES :
                yield response.follow(url = link, callback = self.parse_yearpage)
            else:
                return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def parse_yearpage (self, response) :
        """
        Process a single year-based recipe directory page.
        The flow obtains a list of year-recipe URLs and then crawls each URL.

        Parameters:
            self: Object instance
            response: Selector object provided by invoking parent method.
        """
        # Log iteration
        logger.info(f'parse_yearpage for {response.request.url}')

        # Increment number of directory pages traveled.
        self.n_directory_pages = self.n_directory_pages + 1
        # Do not process further if the max counts have been passed.
        if self.n_directory_pages > MAX_DIRECTORY_PAGES :
            logger.info(f'Passed threshold of directory pages. ({self.n_directory_pages})')
            return

        # Create a recipe directory node
        logger.info(f'Creating new recipe page node in {self.gdb.database.name}')
        tx = py2neo.begin()
        rdir = py2neo.Node("RecipeDirectory", url=response.request.url)
        tx.py2neo.create(rdir)
        tx.commit()
        if not food_db.exists(rdir) :
            logger.error(f'Recipe directory {response.request.url} was not created. :()')

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


if __name__ == '__main__':
    # Initialize logging.
    logcfg_path = os.path.join(src_directory, 'logging.config')
    print(logcfg_path)
    logging.config.fileConfig(logcfg_path)
    logger.info(f'***Start from epicurious_spider.py***')
    # Invoke the main function.
    spider_process = scrapy.crawler.CrawlerProcess()
    spider_process.crawl(EpicuriousSpider)
    spider_process.start()
