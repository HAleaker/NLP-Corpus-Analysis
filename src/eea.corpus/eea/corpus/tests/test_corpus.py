from unittest.mock import Mock, patch


class TestCorpus:
    """ Tests for the Corpus class
    """

    @patch('eea.corpus.corpus.load_corpus_metadata')
    @patch('eea.corpus.corpus.corpus_base_path')
    def test_corpus_caching(self, corpus_base_path, load_corpus_metadata):
        from eea.corpus.corpus import Corpus

        corpus = Corpus('filename', 'corpusid')
        corpus._docs_stream = iter(range(100))

        assert len(corpus._cache) == 0

        x = list(corpus)
        assert len(x) == 100
        assert len(list(corpus)) == 100
        assert len(list(corpus)) == 100
        assert corpus._use_cache is True
        assert len(corpus._cache) == 100

    @patch('eea.corpus.corpus.load_corpus_metadata')
    @patch('eea.corpus.corpus.corpus_base_path')
    def test_corpus_metadata(self, corpus_base_path, load_corpus_metadata):
        from eea.corpus.corpus import Corpus

        corpus = Corpus('a', 'b')
        corpus._meta = {
            'statistics': {'docs': 30},
            'title': 'corpus title',
            'description': 'corpus description',
    