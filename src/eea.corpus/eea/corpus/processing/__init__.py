from collections import OrderedDict, namedtuple
from itertools import zip_longest

import colander
import deform
import venusian

from eea.corpus.config import upload_location
from eea.corpus.processing.utils import (component_phash_id,
                                         get_pipeline_for_component)
from pandas import read_csv

# con