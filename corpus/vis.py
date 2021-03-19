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


def _get_topic_term_dists(lda_model):
    return _row_norm(lda_model.components_)


def _get_vocab(id2term):
    res = []
    for i in sorted(id2term.keys()):
        res.append(id2term[i])
    return res


def _extract_data(lda_model, dtm, id2term):
    vocab = _get_vocab(id2term)
    doc_lengths = _get_doc_lengths(dtm)
    term_freqs = _get_term_freqs(dtm)
    topic_term_dists = _get_topic_term_dists(lda_model)

    assert term_freqs.shape[0] == len(vocab), \
        ('Term frequencies and vocabulary are of different sizes, {} != {}.'
         .format(term_freqs.shape[0], len(vocab)))

    assert topic_term_dists.shape[1] == dtm.shape[1], \
        ('Topic-term distributions and document-term matrix have different '
         'number of columns, {} != {}.'
         .format(topic_term_dists.shape[1], len(vocab)))

    # column dimensions of document-term matrix and topic-term distributions
    # must match first before transforming to document-topic distributions
    doc_topic_dists = _get_doc_topic_dists(lda_model, dtm)

    return {'vocab': vocab,
            'doc_lengths': doc_lengths.tolist(),
            'term_frequency': term_freqs.tolist(),
            'doc_topic_dists': doc_topic_dists.tolist(),
            'topic_term_dists': topic_term_dists.tolist()}


def prepare(lda_model, dtm, id2term, **kwargs):
    """Create Prepared Data from sklearn's LatentDirichletAllocation and
    CountVectorizer.

    Parameters
    ----------
    lda_model : sklearn.decomposition.LatentDirichletAllocation.
        Latent Dirichlet Alloc