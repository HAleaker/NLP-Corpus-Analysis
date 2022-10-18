import colander
import deform.widget
from colander import Schema

from eea.corpus.processing.phrases.widget import PhraseFinderWidget


class PhraseFinder(Schema):
    """ Schema for the phrases finder
    """

    widget = PhraseFinderWi