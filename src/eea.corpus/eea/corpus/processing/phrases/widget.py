import logging
import os.path

from deform.widget import MappingWidget, default_resource_registry
from pyramid.threadlocal import get_current_request

from eea.corpus.async import get_assigned_job
from eea.corpus.corpus import corpus_base_path
from eea.corpus.processing.utils import (component_phash_id,
                                         get_pipeline_for_component)

logger = logging.getLogger('eea.corpus')


default_resource_registry.set_js_resources(
    'phrase-widget', None, 'eea.corpus:static/phrase-widget.js'
)


class PhraseFinderWidget(MappingWidget):
    """ Mapping widget with custom template

