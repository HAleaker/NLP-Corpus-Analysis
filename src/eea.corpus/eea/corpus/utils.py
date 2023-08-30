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
        m.update(str(kv).encode('ascii'))

    return m.hexdigest()


def set_text(doc, text):
    """ Build a new doc based on doc's metadata and provided text
    """

    return {'text': text, 'metadata': doc['metadata']}


def is_locked(fpath):
    """ Check if a lock file exists for given path
    """
    path = fpath + '.lock'

    return os.path.exists(path)


def schema_defaults(schema):
    """ Returns a mapping of fielname:defaultvalue
    """
    res = {}

    for child in schema.children:
        if child.default is not None:
            res[child.name] = child.default
        else:
            res[child.name] = child.missing

    return res


def tokenize(phrase, delimiter='_'):
    """ Tokenizes a phrase (converts those words to a unique token)
    """

    words = phrase.split(' ')
    res = []

    # remove the 's in text

    for w in words:
        w = w.split("'")[0]
        res.append(w)

    ret