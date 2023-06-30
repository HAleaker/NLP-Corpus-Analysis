from unittest.mock import sentinel as S
from unittest.mock import patch

from pyramid import testing


class TestHome:

    @patch('eea.corpus.views.available_