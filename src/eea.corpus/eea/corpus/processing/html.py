""" Get the text from potential html strings using bs4
"""

import logging

from bs4 import BeautifulSoup
from colander import Schema

from eea.corpus.processing import pipeline_component  # , needs_text_input
from eea.corpus.utils import set_text

logger = logging.getLogger('eea.corpus')


class BeautifulSoupText(Schema):
    """ Schema for BeautifulSoup based parser
    """
    description = "Uses BeautifulSoup t