
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

    def _get_sorted_component_names(self, request):
        """ Returns a list of (component names, params) from request
        """

        data = parse(request.POST.items())
        schemas = []        # establish position of widgets

        for k, v in self.request.POST.items():
            if (k == '__start__') and (':mapping' in v):
                sk = v.split(':')[0]
                parms = data[sk]

                if isinstance(parms, dict) and parms.get('schema_type', None):
                    schemas.append((sk, data[sk]))

        return schemas

    def get_pipeline_components(self, appstruct):
        """ Returns a pipeline, a list of (process, schema name, arguments)

        It uses the request to understand the structure of the pipeline. The
        significant elements of that structure are the pipeline component name,
        its position in the schema and its settings.

        It's only used in ``generate_corpus_success`` in this form.
        """

        pipeline = []

        for name, _ in self._get_sorted_component_names(self.request):
            kwargs = appstruct[name]
            schema_type = kwargs.pop('schema_type')
            s = (schema_type, name, kwargs)
            pipeline.append(s)

        return pipeline

    def pipeline_from_schema(self, schema, appstruct):

        # the difference to _get_sorted_component_names is that here
        # we loop over schema children and need to have default params when
        # schema is newly added
        pipeline = []

        for c in schema.children:
            _type = c.get('schema_type')

            if _type:
                # assume mapping schema
                kw = appstruct.get(c.name, schema_defaults(c)).copy()

                # remove auxiliary fields that are not expected as args
                kw.pop('schema_type', None)

                # TODO: is the pipeline_registry here needed?
                p = pipeline_registry[_type.default]
                pipeline.append((p.name, c.name, kw))

        return pipeline

    def _schemas(self):
        """ Returns a list of schema instances, for ``Form`` instantiation.
        """

        schemas = []

        for name, params in self._get_sorted_component_names(self.request):
            _type = params['schema_type']
            p = pipeline_registry[_type]
            s = p.schema(name=name, title=p.title)
            schemas.append(s)

        return schemas

    def preview_success(self, appstruct):
        # preview is done by show()
        pass

    def generate_corpus_success(self, appstruct):
        pipeline = self.get_pipeline_components(appstruct)

        s = appstruct.copy()
        s['doc'] = self.document
        corpus_id = hashed_id(sorted(s.items()))

        job = queue.enqueue(build_corpus,
                            timeout='1h',
                            args=(
                                pipeline,
                                corpus_id,
                                self.document,
                                appstruct['column'],
                            ),
                            kwargs=appstruct)

        raise exc.HTTPFound('/job-view/%s/%s/job/%s' %
                            (self.document, corpus_id, job.id))

    def form_class(self, schema, **kwargs):
        data = parse(self.request.POST.items())

        schemas = self._schemas()
        schemas = self._apply_schema_edits(schemas, data)

        for s in schemas:
            schema.add(s)

        # move the pipeline components select widget to the bottom
        w = schema.__delitem__('pipeline_components')
        schema.add(w)

        kwargs.update(dict(self.form_options))

        self.form = Form(schema, renderer=deform_renderer, **kwargs)

        return self.form

    def _apply_schema_edits(self, schemas, data):
        # assume the schemas have a contigous range of schema_position values
        # assume schemas are properly ordered

        for i, s in enumerate(schemas):

            if "remove_%s_success" % s.name in data:
                del schemas[i]

                return schemas

            if "move_up_%s_success" % s.name in data:
                if i == 0:
                    return schemas      # can't move a schema that's first
                # switch position between list members
                this, other = schemas[i], schemas[i-1]
                schemas[i-1] = this
                schemas[i] = other

                return schemas

            if "move_down_%s_success" % s.name in data:
                if i == len(schemas) - 1:
                    return schemas      # can't move a schema that's last
                # switch position between list members
                this, other = schemas[i], schemas[i+1]
                schemas[i+1] = this
                schemas[i] = other

                return schemas

        return schemas

    def show(self, form):
        # re-validate form, it is possible to be changed
        appstruct = {}
        controls = list(self.request.POST.items())

        if controls:
            try:
                appstruct = form.validate(controls)
            except deform.exception.ValidationFailure as e:
                return self.failure(e)

        schema = form.schema
        # now add new schemas, at the end of all others
        add_component = appstruct.pop('pipeline_components', None)

        if add_component:
            p = pipeline_registry[add_component]
            s = p.schema(name=rand(10), title=p.title,)
            schema.add(s)
            # move pipeline_components to the bottom
            w = schema.__delitem__('pipeline_components')
            schema.add(w)

        # try to build a preview, if possible

        if appstruct.get('column'):
            pipeline = self.pipeline_from_schema(schema, appstruct)
            pstruct = self.request.create_corpus_pipeline_struct = {
                'file_name': self.document,
                'text_column': appstruct['column'],
                'pipeline': pipeline,
                'preview_mode': True
            }
            content_stream = build_pipeline(**pstruct)

            self.preview = islice(content_stream, 0, self.preview_size)

        form = Form(schema, buttons=self.buttons, renderer=deform_renderer,
                    **dict(self.form_options))
        reqts = form.get_widget_resources()

        return {
            'form': form.render(appstruct),
            'css_links': reqts['css'],
            'js_links': reqts['js'],
        }


@view_config(route_name='view_job', renderer='templates/job.pt')
def view_job(request):
    jobid = request.matchdict.get('job')
    job = queue.fetch_job(jobid)

    return {'job': job}


@view_config(route_name='delete_corpus')
def delete_corpus_view(request):
    doc, corpus = extract_corpus_id(request)
    delete_corpus(doc, corpus)
    request.session.flash("Corpus deleted")
    raise exc.HTTPFound('/')


@view_config(context=Exception, renderer='templates/error.pt')
def handle_exc(context, request):
    _type, value, tr = sys.exc_info()
    error = " ".join(tb.format_exception(_type, value, tr))
    logger.error(error)

    return {
        'error': error
    }


@view_config(route_name="corpus_view", renderer='templates/view_corpus.pt')
def view_corpus(request):
    page = int(request.matchdict['page'])
    corpus = get_corpus(request)

    if corpus is None or page > (corpus.n_docs - 1):
        raise exc.HTTPNotFound()

    nextp = page + 1

    if nextp >= corpus.n_docs:
        nextp = None

    prevp = page - 1

    if prevp < 0:
        prevp = None

    return {
        'corpus': corpus,
        'doc': next(islice(corpus, page, None)),
        'nextp': nextp,
        'prevp': prevp,
        'page': page
    }