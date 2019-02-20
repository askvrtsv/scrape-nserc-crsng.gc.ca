# -*- coding: utf-8 -*-

import json
from pprint import pprint
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.response import open_in_browser

from crawler.items import Award


URL = 'http://www.nserc-crsng.gc.ca/ase-oro/_incs/ajax.asp?lang=e'

FORMDATA = {
    'sEcho': '2',
    'iColumns': '5',
    'sColumns': '',
    'iDisplayStart': '0',
    'iDisplayLength': '10',
    'mDataProp_0': '0',
    'mDataProp_1': '1',
    'mDataProp_2': '2',
    'mDataProp_3': '3',
    'mDataProp_4': '4',
    'sSearch': '',
    'bRegex': 'false',
    'sSearch_0': '',
    'bRegex_0': 'false',
    'bSearchable_0': 'true',
    'sSearch_1': '',
    'bRegex_1': 'false',
    'bSearchable_1': 'true',
    'sSearch_2': '',
    'bRegex_2': 'false',
    'bSearchable_2': 'true',
    'sSearch_3': '',
    'bRegex_3': 'false',
    'bSearchable_3': 'true',
    'sSearch_4': '',
    'bRegex_4': 'false',
    'bSearchable_4': 'true',
    'iSortingCols': '2',
    'iSortCol_0': '0',
    'sSortDir_0': 'asc',
    'iSortCol_1': '3',
    'sSortDir_1': 'desc',
    'bSortable_0': 'true',
    'bSortable_1': 'true',
    'bSortable_2': 'true',
    'bSortable_3': 'true',
    'bSortable_4': 'true',
}

HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
}

FIELDS = {
    'Project Lead Name': 'lead_name',
    'Fiscal Year': 'fiscal_year',
}


class AwardsSpider(scrapy.Spider):
    name = 'awards'
    allowed_domains = ['www.nserc-crsng.gc.ca']

    start_urls = ['http://www.nserc-crsng.gc.ca/ase-oro/index_eng.asp?new']

    def parse(self, response):
        """Установка параметров поиска.

        ВАЖНО! Удалить .scrapy перед изменением параметров, потому что
        параметры поиска храятся в сессии на сервере.
        """
        yield scrapy.FormRequest.from_response(
            response,
            formid='contact-form',
            formdata={
                # Параметры поиска
                'fiscalyearfrom': '2015',
                'fiscalyearto': '2015',
            },
            callback=self.after_search
        )

    def after_search(self, response):
        yield scrapy.FormRequest(URL, callback=self.parse_num_of_records,
                                 formdata=FORMDATA)

    def parse_num_of_records(self, response):
        """Поиск количества записей."""
        try:
            data = json.loads(response.body)
            total_records = int(data['iTotalRecords'])
        except (json.decoder.JSONDecodeError, KeyError, ValueError):
            return

        num_on_page = 200
        for start in range(0, total_records, num_on_page):
            data = FORMDATA.copy()
            data['iDisplayStart'] = str(start)
            data['iDisplayLength'] = str(num_on_page)

            yield scrapy.FormRequest(URL, callback=self.parse_list,
                                     formdata=data, headers=HEADERS,
                                     dont_filter=False)

    def parse_list(self, response):
        """Парсинг списка записей.

        Из-за битого JSON-файла находим идентификаторы записей с помощью
        регулярок.
        """
        try:
            award_ids = re.findall('"(\w+)"\]', response.body.decode('utf8'))
            for id_ in award_ids:
                yield scrapy.Request(
                    f'http://www.nserc-crsng.gc.ca/ase-oro/Details-Detailles_eng.asp?id={id_}',
                    callback=self.parse_award
                )
        except (json.decoder.JSONDecodeError, KeyError):
            raise

    def parse_award(self, response):
        l = ItemLoader(item=Award(), response=response)

        l.add_value('url', response.url)
        l.add_css('project_title', '#main-container-1col > h2::text')

        for title, field in FIELDS.items():
            l.add_xpath(
                field,
                f'//strong[text()="{title}:"]/../following-sibling::td/text()'
            )

        return l.load_item()
