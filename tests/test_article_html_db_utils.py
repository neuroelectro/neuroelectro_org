# -*- coding: utf-8 -*-

__author__ = 'shreejoy'

import unittest
from article_text_mining.article_html_db_utils import add_article_full_text_from_file


class AddFullTextFromFileTest(unittest.TestCase):

    @property
    def load_article_full_text(self):
        # creates data table object 16055 with some dummy data
        with open('tests/test_article_full_texts/26490853.html', mode='rb') as f:
            article_full_text = f.read()
        return article_full_text


    def test_add_article_full_text_from_file(self):
        full_text_path = 'tests/test_article_full_texts/26490853.html'
        pmid = '26490853'
        html_table_list = []
        article_ob = add_article_full_text_from_file(full_text_path, pmid, html_table_list)

        expected_title = 'Rapid Feedforward Inhibition and Asynchronous Excitation Regulate Granule Cell Activity in the Mammalian Main Olfactory Bulb.'

        self.assertEqual(article_ob.title, expected_title)

