import logging
import os.path
from glob import iglob

from eea.corpus.async import get_assigned_job
from eea.corpus.config import CORPUS_STORAGE

logger = logging.getLogger('eea.corpus')


def phrase_model_status(request):
    """ A view for information about the async status of a phrase model

    It looks up any existing running or queued async job that would process
    the phrases and returns 