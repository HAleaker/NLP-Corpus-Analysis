import logging
import os.path
from glob import iglob

from eea.corpus.async import get_assigned_job
from eea.corpus.config import CORPUS_STORAGE

logger = logging.ge