from unittest.mock import Mock, patch


class TestHTML:
    texts = (
        "<strong>Hello</strong> world",
        "Just plain text",
    )

    def test_schema(self):
        from eea.corpus.processing.html import BeautifulSoupText
        assert len(BeautifulSoupText().children) == 0

    def test_clean_docs(self):
        from eea.corpus.processing.html import process

        content = ({'text': s, 'metadata': None} for s in self.texts)
        content = process(content, {})

      