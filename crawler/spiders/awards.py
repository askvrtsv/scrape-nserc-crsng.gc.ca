# -*- coding: utf-8 -*-

import sqlite3

import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.response import open_in_browser
from selenium import webdriver

from crawler.items import Award


class AwardsSpider(scrapy.Spider):
    name = 'awards'
    allowed_domains = ['www.nserc-crsng.gc.ca']

    start_urls = ['http://www.nserc-crsng.gc.ca/ase-oro/index_eng.asp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = sqlite3.connect('db.sqlite')
        cur = self.db.cursor()

        try:
            cur.executescript('''
                create table awards (
                    url text,
                    project_title text,
                    lead_name text
                );
            ''')
        except sqlite3.OperationalError:
            pass

    def close(self, reason):
        self.db.close()

    def parse(self, response):
        pass
