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
            'document