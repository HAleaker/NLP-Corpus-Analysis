import pytest


@pytest.fixture
def text_column_stream():
    from pkg_resources import resource_filename
    import pandas as pd

    fpath = resource_filename('eea.corpus