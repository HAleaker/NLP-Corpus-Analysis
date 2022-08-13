
import json
import logging
import os.path
from collections import defaultdict

from eea.corpus.async import queue
from eea.corpus.config import CORPUS_STORAGE
from eea.corpus.processing import build_pipeline
from eea.corpus.utils import is_valid_document
from rq.decorators import job
from textacy import io

logger = logging.getLogger('eea.corpus')


def corpus_base_path(file_name):
    """ Returns the /corpus/var/<filename> folder for an uploaded file
    """

    varpath = os.path.join(CORPUS_STORAGE, 'var')
    base = os.path.join(varpath, file_name)

    if not os.path.exists(base):
        os.makedirs(base)

    return base


def delete_corpus(file_name, corpus_id):
    assert len(corpus_id) > 10
    cp = corpus_base_path(file_name)

    for f in os.listdir(cp):
        if f.startswith(corpus_id):
            fp = os.path.join(cp, f)
            os.unlink(fp)


def available_corpus(file_name):
    """ Returns available, already-created, corpuses for a filename

    The corpuses corespond to a column in the file.
    """

    base = corpus_base_path(file_name)

    if not os.path.exists(base):
        return []

    res = []
    files = defaultdict(list)

    for fn in os.listdir(base):
        if '_' not in fn:
            continue
        base, spec = fn.split('_', 1)
        files[base].append(spec)

        for corpus, cfs in files.items():
            if len(cfs) != len(('docs', 'info')):
                logger.warning("Not a valid corpus: %s (%s)",
                               file_name, corpus)

                continue
            res.append(corpus)

    return res


def corpus_info_path(file_name, corpus_id):
    """ Returns the <corpusid>_info.json file path for a given doc/corpus
    """
    cpath = corpus_base_path(file_name)      # corpus_id
    meta_name = "{0}_info.json".format(corpus_id)
    meta_path = os.path.join(cpath, meta_name)

    return meta_path


def load_corpus_metadata(file_name, corpus_id):
    """ Returns the EEA specific metadata saved for a doc/corpus
    """

    meta_path = corpus_info_path(file_name, corpus_id)

    res = None

    with open(meta_path) as f:
        res = json.load(f)

    return res


def extract_corpus_id(request):
    """ Extract document name (aka file_name) from request
    """

    md = request.matchdict or {}
    doc = md.get('doc')
    corpus = md.get('corpus')

    if not (is_valid_document(doc) and (corpus in available_corpus(doc))):
        return (None, None)

    return (doc, corpus)


def save_corpus_metadata(stats, file_name, corpus_id, text_column, **kw):
    cpath = corpus_base_path(file_name)      # corpus_id
    meta_name = "{0}_info.json".format(corpus_id)
    meta_path = os.path.join(cpath, meta_name)

    title = kw.pop('title')
    description = kw.pop('description', '')

    info = {
        'title': title,
        'description': description,
        'statistics': stats,
        'text_column': text_column,