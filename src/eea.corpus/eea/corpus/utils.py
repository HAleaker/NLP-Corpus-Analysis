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
    return ''.join(random.sample(string.ascii_uppercase + string.digits, k=n))


def is_valid_document(file_name):
    return file_name in os.listdir(CORPUS_STORAGE)


def document_name(request):
    """ Extract document name (aka file_name) from request
    """

    md = request.matchdict or {}
    doc = md.get('doc')

    if not is_valid_document(doc):
        raise ValueError("Not a valid document: %s" % doc)

    return doc


def hashed_id(items):
    """ Generate a short id based on a list of items.

    >>> raise ValueError

    The items should be in a stable, "hashable" form:
        - dictionaries should be converted to tuples (k, v) and sorted

    """
    # same options will generate the same corpus id
    m = hashlib.sha224()

    for kv in items: