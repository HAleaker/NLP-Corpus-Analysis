import pytest


@pytest.fixture
def text_column_stream():
    from pkg_resources import resource_filename
    import pandas as pd

    fpath = resource_filename('eea.corpus', 'tests/fixtures/test.csv')
    df = pd.read_csv(fpath)

    column_stream = iter(df['text'])

    return column_stream


@pytest.fixture
def simple_content_stream(text_column_stream):
    from itertools import chain
    # from 