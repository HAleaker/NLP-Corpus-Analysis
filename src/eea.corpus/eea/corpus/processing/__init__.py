from collections import OrderedDict, namedtuple
from itertools import zip_longest

import colander
import deform
import venusian

from eea.corpus.config import upload_location
from eea.corpus.processing.utils import (component_phash_id,
                                         get_pipeline_for_component)
from pandas import read_csv

# container for registered pipeline components
pipeline_registry = OrderedDict()

Processor = namedtuple('Processor',
                       ['name', 'schema', 'process', 'title', 'actions'])


def pipeline_component(schema, title, actions=None):
    """ Register a processing function as a pipeline component, with a schema

    A pipeline component is two pieces:

    * a ``process(content, **kwargs)`` function that performs any needed
    transformation on the input content.
    * a schema that will provide the necessary parameters values for the
    ``register`` function call

    Additionally, an ``actions`` mapping can be passed, where the keys are
    button names and the values are functions that will handle requests. They
    can be used to handle special cases that can't be foreseen by the main form
    views.

    Use such as:

        class SomeSettingsSchema(colander.Schema):
            count = colander.SchemaNode(colander.Int)

        @pipeline_component(schema=SomeSettingsSchema, title='Generic Pipe',
                            actions={'handle_': handle})
        def process(content, **settings):
            for doc in content:
                # do something
     