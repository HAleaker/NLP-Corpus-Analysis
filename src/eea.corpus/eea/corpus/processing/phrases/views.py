import logging
import os.path
from glob import iglob

from eea.corpus.async import get_assigned_job
from eea.corpus.config import CORPUS_STORAGE

logger = logging.getLogger('eea.corpus')


def phrase_model_status(request):
    """ A view for information about the async status of a phrase model

    It looks up any existing running or queued async job that would process
    the phrases and returns JSON info about that.

    # TODO: this view + template + script implementation still needs work
    """

    phash_id = request.matchdict['phash_id']

    # TODO: when looking for phrase model files, look for lock files as well

    # look for a filename in corpus v