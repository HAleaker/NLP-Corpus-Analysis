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

    Template customizations:

        * frame color based on phrase model status
        * the reload button is disabled/enabled based on live phrase model
          status
        * there is an AJAX js script that queries job status and updates the
          widget status indicators (frame color, reload preview button)
    """

    template = 'phrase_form'
    requirements = (('phrase-widget', None),)

    def get_template_values(self, field, cstruct, kw):
        """ Inserts the job status and preview status into template values
        """
        values = super(PhraseFinderWidget, self).\
            get_template_values(field, cstruct, kw)

        values['job_status'] = 'preview_not_available'

        req = get_current_request()

        # TODO: can we refactor this so that we compute the pi