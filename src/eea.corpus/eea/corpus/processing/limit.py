""" Limit the content stream to a fixed number of "rows"
"""

from colander import Schema, Int, SchemaNode
from eea.corpus.processing import pipeline_component
from itertools import islice
import logging

logger = logging.getLogger('eea.corpus')


class LimitResults(Schema):

    # description = "Limit the number of processed documents"

    max_count = SchemaNode(
        Int(),
        default=10,
        missing=10,
        title='Results limit',
        description='Set to 0 if you want unlimited results',
    )


@pipeline_component(schema=LimitResults,
                    title="Limit number of results")
def process(content, env, **settings):
    count = int(settings.get('max_count', 10))
    if not count:
        yield from content
    else:
        content = islice(content, 0, count)
        yield from content
