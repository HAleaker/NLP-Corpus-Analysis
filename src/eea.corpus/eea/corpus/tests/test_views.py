from unittest.mock import sentinel as S
from unittest.mock import patch

from pyramid import testing


class TestHome:

    @patch('eea.corpus.views.available_documents')
    def test_it(self, available_documents):
        from eea.corpus.views import home

        available_documents.return_value = S.docs

        assert home(None) == {
            'project': 'EEA Corpus Server',
            'documents': S.docs
        }


class TestCreateCorpus:

    @classmethod
    def setup_class(cls):
        cls.config = testing.setUp()
        cls.config.scan('eea.corpus.processing')

    @classmethod
    def teardown_class(cls):
        testing.tearDown()

    def test_apply_schema_edits(self):
        from eea.corpus.processing import pipeline_registry as pr
        from eea.corpus.views import CreateCorpusView

        LimitSchema = pr['eea_corpus_processing_limit_process'].s