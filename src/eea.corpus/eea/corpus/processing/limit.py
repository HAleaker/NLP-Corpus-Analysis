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
        description='