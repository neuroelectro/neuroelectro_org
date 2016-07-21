# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 16:10:16 2013

@author: Shreejoy
"""
import os
#import django_startup
import re
from random import shuffle

from django.conf import settings

# from lxml import etree
import glob

from article_text_mining.article_html_db_utils import add_single_full_text
from scripts.dbrestore import prog


def add_full_texts_from_mult_dirs(curr_path, matching_journ_str):
    """Expected Usage:
        add_full_texts_from_mult_dirs(PATH_TO_JOURNAL_DIRECTORIES, FRONTIERS)
    """

    dir_list = os.listdir(curr_path)
    for d in dir_list:
        print d
        if matching_journ_str in d:
            abs_path = curr_path + d + '/'
            add_full_texts_from_directory(abs_path)


def add_full_texts_from_directory(dir_path):
    base_dir = dir_path
    os.chdir(base_dir)
    file_name_list = [f for f in glob.glob("*.html")]

    #shuffle(file_name_list)
    file_name_list.sort(reverse= True)

    os.chdir(settings.PROJECT_BASE_DIRECTORY)

    print len(file_name_list)
    for i, fn in enumerate(file_name_list):
        prog(i, len(file_name_list))
        file_name = base_dir + fn

        pmid_str = re.search('\d+', file_name).group()

        add_single_full_text(file_name, pmid_str)



