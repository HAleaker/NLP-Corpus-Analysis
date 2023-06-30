from unittest.mock import patch
from pyramid import testing


class TestProcessing:
    @classmethod
    def setup_class(cls):
        cls.config = testing.setUp()
        cls.config.scan('