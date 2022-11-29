
import colander
import deform
from colander import Float, Int, Schema, SchemaNode, Set, String

import pandas as pd
from eea.corpus.config import upload_location
from eea.corpus.processing import pipeline_registry


class Store(dict):
    def preview_url(self, name):
        return ""


tmpstore = Store()


def csv_file_columns(request):
    md = request.matchdict or {}
    name = md.get('doc')

    if name:
        path = upload_location(name)        # TODO: move this to utils
        f = pd.read_csv(path)

    return [(k, k) for k in f.keys()]


@colander.deferred
def columns_widget(node, kw):
    """ A select widget that reads the csv file to show available columns
    """

    req = kw['request']
    choices = [('', '')] + csv_file_columns(req)

    return deform.widget.SelectWidget(
        values=choices,
        default=''
    )


@colander.deferred
def multi_columns_widget(node, kw):
    """ A multiselect widget that reads the csv file to show available columns
    """

    req = kw['request']
    choices = csv_file_columns(req)

    return deform.widget.SelectWidget(
        values=choices,
        multiple=True
    )


class UploadSchema(Schema):
    # title = SchemaNode(String())
    upload = SchemaNode(
        deform.FileData(),
        widget=deform.widget.FileUploadWidget(tmpstore)
    )


class TopicExtractionSchema(Schema):
    topics = SchemaNode(
        Int(),
        default=10,
        title="Number of topics to extract"
    )
    num_docs = SchemaNode(
        Int(),
        default=100,
        title="Max number of documents to process"
    )
    ngrams = SchemaNode(
        Int(),
        default=1,
        title="ngram level generation for tokens"
    )
    weighting = SchemaNode(
        String(),
        title="Term weighting normalization",
        description="Change the weight of terms based on frequency",
        widget=deform.widget.SelectWidget(
            values=[
                ('tf', 'TF'),
                ('tfidf', 'TFIDF'),
            ],
            default='tf'
        )
    )
    min_df = SchemaNode(
        Float(),
        title="min_df",
        description="""Ignore terms that have
        a document frequency strictly lower than the given threshold. This
        value is also called cut-off in the literature. The parameter
        represents a proportion of documents.""",
        default=0.1,
    )
    max_df = SchemaNode(
        Float(),
        title="max_df",
        description=""" Ignore terms that have
        a document frequency strictly higher than the given threshold
        (corpus-specific stop words). The parameter represents
        a proportion of documents. """,
        default=0.7,
    )
    mds = SchemaNode(
        String(),
        title="Distance scaling algorithm (not for termite plot)",
        description="Multidimensional Scaling algorithm. See "
        "https://en.wikipedia.org/wiki/Multidimensional_scaling",
        widget=deform.widget.SelectWidget(
            values=[
                ('pcoa', 'PCOA (Classic Multidimensional Scaling)'),
                ('mmds', 'MMDS (Metric Multidimensional Scaling)'),
                ('tsne',
                 't-SNE (t-distributed Stochastic Neighbor Embedding)'),
            ],
            default='pcoa'
        )
    )


@colander.deferred
def pipeline_components_widget(node, kw):
    values = [('', '-Select-')]
    values += [(p.name, p.title) for p in pipeline_registry.values()]

    return deform.widget.SelectWidget(
            template="pipeline_select",
            values=values,
        )


class CreateCorpusSchema(colander.MappingSchema):
    """ Process text schema
    """

    title = SchemaNode(
        String(),
        validator=colander.Length(min=1),
        title='Corpus title.',
        description='Letters, numbers and spaces',
    )

    description = SchemaNode(
        String(),
        widget=deform.widget.TextAreaWidget(),
        title='Description',
        missing='',
    )

    column = SchemaNode(
        String(),
        widget=columns_widget,
        validator=colander.Length(min=1),
        title='Text column in CSV file',
    )

    pipeline_components = SchemaNode(
        String(),
        missing='',
        widget=pipeline_components_widget,
        title="Add a new pipeline component"
    )


class ClassifficationModelSchema(colander.MappingSchema):
    """ Schema to build a text classification modle
    """

    columns = SchemaNode(
        Set(),
        widget=multi_columns_widget,
        title='Columns with class labels',
    )