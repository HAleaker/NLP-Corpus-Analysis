from __future__ import unicode_literals

import hashlib
import logging
import os
import random
import string

from cytoolz import compose
from eea.corpus.config import CORPUS_STORAGE

logger = logging.getLogger('eea.corpus')


def rand(n):
    re