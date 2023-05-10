from unittest.mock import Mock, patch


class TestCorpus:
    """ Tests for the Corpus class
    """

    @patch('eea.corpus.corpus.load_corpus_metadata')
    @patch('eea.corpus.corpus.corpus_base_path')
    def test_corpus_caching(self, corpus_base_path, load_corpus_metadata):
        from eea.corpus.corpus import Corpus

        cor