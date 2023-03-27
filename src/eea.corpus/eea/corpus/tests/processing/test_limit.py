class TestLimit:

    def test_schema(self):
        from eea.corpus.processing.limit import LimitResults
        assert len(LimitResults().children) == 1

    def test_it(self):
        from eea.corpus.processing.limit import process

        text = "Hello world".split() * 20       # 40 words

        content = process(iter(text), {}, max_count=10)
        assert len(list(content)) == 10

        