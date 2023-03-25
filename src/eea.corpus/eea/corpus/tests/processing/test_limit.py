class TestLimit:

    def test_schema(self):
        from eea.corpus.processing.limit import LimitResults
        assert len(LimitResults().children) == 1

