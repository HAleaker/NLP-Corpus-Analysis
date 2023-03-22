from unittest.mock import Mock, patch


class TestHTML:
    texts = (
        "<strong>Hello</strong> world",
        "Just plain text",
    )

    def test_schema(self):
        from eea.corpus.processing.html import BeautifulSoupText
 