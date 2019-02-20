# -*- coding: utf-8 -*-

from w3lib.html import remove_tags

import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def absolute_url(url, loader_context):
    return loader_context['response'].urljoin(url)


class Award(scrapy.Item):
    url = scrapy.Field(
        output_processor=TakeFirst(),
    )
    project_title = scrapy.Field(
        output_processor=TakeFirst(),
    )
    lead_name = scrapy.Field(
        output_processor=TakeFirst(),
    )
    fiscal_year = scrapy.Field(
        output_processor=TakeFirst(),
    )
