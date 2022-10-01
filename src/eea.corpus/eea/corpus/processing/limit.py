""" Limit the content stream to a fixed number of "rows"
"""

from colander import Schema, Int, SchemaNode
from eea.corpus.processing import pipeline_component
from itertools import islice
import logging

logger = logging.getLogger('eea.cor