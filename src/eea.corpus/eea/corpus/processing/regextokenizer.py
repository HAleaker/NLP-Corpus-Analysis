import logging
import re

import colander

from eea.corpus.processing import pipeline_component
from eea.corpus.utils import set_text

logger = logging.getLogger('eea.corpus')


class RegexTokenizer(colander.Schema):
    """ Schem