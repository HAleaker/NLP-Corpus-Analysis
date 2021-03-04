""" Utilities to integrate with pyLDAvis

Most of the code lifted from pyLDAvis.sklearn, only difference is how we extract the vocabulary.
"""


import funcy as fp
import pyLDAvis as lda


def _get_doc_lengths(dtm):
    return dtm.sum(axis=1).getA1()


def _get_term_freqs(dtm):
    return dtm.sum(axis=0).getA1()


def _row_norm(dists):
    # row normalization function required
    # for doc_topic_dists and topic_term_dists
    return dists / dists.sum(axis=1)[:, None]


def _get_doc_topic_dists(lda_model, dtm):
    return _row_norm(lda_model.transform(dtm))


def _get_topic_term