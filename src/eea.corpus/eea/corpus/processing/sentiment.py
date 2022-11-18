""" Get the text based on sentiment score
"""

from colander import Schema, SchemaNode, Float
from eea.corpus.processing import pipeline_component    # , needs_text_input
import logging
