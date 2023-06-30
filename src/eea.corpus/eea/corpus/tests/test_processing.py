from unittest.mock import patch
from pyramid import testing


class TestProcessing:
    @classmethod
    def setup_class(cls):
        cls.config = testing.setUp()
        cls.config.scan('eea.corpus.processing')

    @classmethod
    def teardown_class(cls):
        testing.tearDown()

    @patch('eea.corpus.processing.upload_location')
    def test_build_pipeline_for_preview(self, upload_location):
        from eea.corpus.proce