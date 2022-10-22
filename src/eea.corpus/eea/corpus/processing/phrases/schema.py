import colander
import deform.widget
from colander import Schema

from eea.corpus.processing.phrases.widget import PhraseFinderWidget


class PhraseFinder(Schema):
    """ Schema for the phrases finder
    """

    widget = PhraseFinderWidget()       # overrides the default template
    description = "Find and process phrases in text."

    MODES = (
        ('tokenize', 'Tokenize phrases in text'),
        ('append', 'Append phrases to text'),
        ('replace', 'Replace all text with found phrases')
    )

    SCORING = (
        ('default', 'Default'),
        ('npmi', 'NPMI: Slower, better with common words'),
    )

    LEVELS = (
        (2, 'Bigrams'),
        (3, 'Trigrams'),
        (4, 'Quadgrams'),
    )

    mode = colander.SchemaNode(
        coland