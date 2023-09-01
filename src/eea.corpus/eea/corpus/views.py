
""" Pyramid views. Main UI for the eea.corpus
"""

import logging
import sys
import traceback as tb
from itertools import islice

import deform
import pyramid.httpexceptions as exc
from deform import Button, Form, ZPTRendererFactory
from peppercorn import parse
from pkg_resources import resource_filename
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.view import view_config
from pyramid_deform import FormView

from eea.corpus.async import queue
from eea.corpus.config import upload_location
from eea.corpus.corpus import (available_documents, build_corpus,
                               delete_corpus, extract_corpus_id, get_corpus)
from eea.corpus.processing import build_pipeline, pipeline_registry
from eea.corpus.schema import (CreateCorpusSchema, TopicExtractionSchema,
                               UploadSchema)
from eea.corpus.topics import (pyldavis_visualization, termite_visualization,
                               wordcloud_visualization)
from eea.corpus.utils import document_name, hashed_id, rand, schema_defaults

logger = logging.getLogger('eea.corpus')

# Configure alternative Deform templates renderer. Includes overrides for
# default deform templates
deform_templates = resource_filename('deform', 'templates')
eeacorpus_templates = resource_filename('eea.corpus', 'templates/deform')
search_path = (eeacorpus_templates, deform_templates)
deform_renderer = ZPTRendererFactory(search_path)


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):
    documents = available_documents(request)

    return {
        'project': 'EEA Corpus Server',
        'documents': documents
    }


@view_config(
    route_name="upload_csv",
    renderer="templates/simpleform.pt"
)
class UploadView(FormView):
    schema = UploadSchema()
    buttons = ('save',)

    def save_success(self, appstruct):
        upload = appstruct.get('upload')

        if upload:
            fname = upload['filename']
            path = upload_location(fname)
            with open(path, 'wb') as f:
                for line in upload['fp']:
                    f.write(line)

        self.request.session.flash(u"Your changes have been saved.")

        return HTTPFound(location='/')


@view_config(
    route_name="corpus_topics",
    renderer="templates/topics.pt"
)
class TopicsView(FormView):
    schema = TopicExtractionSchema()
    buttons = ('view', 'termite', 'wordcloud')

    vis = None
    dtm = None

    def corpus(self):
        """ Return a corpus based on environment.

        It will try to return it from cache, otherwise load it from disk.
        """

        corpus = get_corpus(self.request)

        if corpus is None:
            raise exc.HTTPNotFound()

        return corpus

    def metadata(self):
        """ Show metadata about context document
        """
        # TODO: show info about processing and column
        corpus = self.corpus()

        return {
            'docs': corpus.n_docs,
            'sentences': corpus.n_sents,
            'tokens': corpus.n_tokens,
            'lang': corpus.lang,
        }

    def visualise(self, appstruct, method):
        max_df = appstruct['max_df']
        min_df = appstruct['min_df']
        mds = appstruct['mds']
        num_docs = appstruct['num_docs']
        ngrams = appstruct['ngrams']
        topics = appstruct['topics']
        weighting = appstruct['weighting']

        corpus = self.corpus()
        MAP = {
            'pyLDAvis': pyldavis_visualization,
            'termite': termite_visualization,
            'wordcloud': wordcloud_visualization,
        }

        visualizer = MAP[method]
        vis = visualizer(corpus, topics, num_docs, ngrams, weighting, min_df,
                         max_df, mds)

        return vis

    def view_success(self, appstruct):
        self.dtm, self.vis = self.visualise(appstruct, method='pyLDAvis')
        self.dtm = self.dtm.shape

    def termite_success(self, appstruct):
        self.dtm, self.vis = self.visualise(appstruct, method='termite')

    def wordcloud_success(self, appstruct):
        topics = self.visualise(appstruct, method='wordcloud')
        out = render('templates/wordcloud_fragments.pt',
                     {'topics': topics})

        self.vis = out


@view_config(
    route_name="process_csv",
    renderer="templates/create_corpus.pt"
)
class CreateCorpusView(FormView):
    schema = CreateCorpusSchema()

    preview = ()        # will hold preview results
    preview_size = 5    # number of documents (csv rows) to preview

    buttons = (
        Button('preview', 'Preview'),
        Button('generate_corpus', 'Generate Corpus'),
        Button('save_pipeline', 'Save pipeline as template'),
    )

    @property
    def document(self):
        return document_name(self.request)
