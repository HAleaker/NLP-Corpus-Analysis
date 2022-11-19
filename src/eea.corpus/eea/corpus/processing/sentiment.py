""" Get the text based on sentiment score
"""

from colander import Schema, SchemaNode, Float
from eea.corpus.processing import pipeline_component    # , needs_text_input
import logging

logger = logging.getLogger('eea.corpus')


class Sentiment(Schema):
    """ Schema for Sentiment filter
    """
    description = "Filter documents based on their sentiment value"

    threshold = SchemaNode(
        Float(),
        default=0.5,
        missing=0