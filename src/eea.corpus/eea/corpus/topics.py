
from __future__ import print_function
from io import StringIO
from pyLDAvis import save_html
from pyLDAvis.sklearn import prepare
import matplotlib.pyplot as plt
import pkg_resources
import textacy
import wordcloud


class Vectorizer(textacy.vsm.Vectorizer):
    def get_feature_names(self):
        return self.feature_names


def build_model(corpus, topics, num_docs=None, ngrams=1, weighting='tf',
                min_df=0.1, max_df=0.7):
    ngrams = int(ngrams)
    docs = [
        list(
            doc.to_terms_list(
                ngrams=ngrams, named_entities=True, as_strings=True,
                filter_nums=True,
            )
        )
        for doc in corpus[:num_docs]
    ]

    vectorizer = Vectorizer(
        weighting=weighting,      # TODO: is this weighting correct?
        normalize=False, smooth_idf=False, min_df=min_df, max_df=max_df,
        max_n_terms=100000
    )
    doc_term_matrix = vectorizer.fit_transform(docs)

    # TODO: support other gensim models
    model = textacy.tm.TopicModel('lda', n_topics=topics)
    model.fit(doc_term_matrix)

    return model, doc_term_matrix, vectorizer


def pyldavis_visualization(corpus, topics, num_docs=None, ngrams=1,
                           weighting='tf', min_df=0.1, max_df=0.7, mds='pcoa',
                           *args, **kwargs):
    model, doc_term_matrix, vectorizer = build_model(
        corpus, topics, num_docs, ngrams, weighting, min_df, max_df
    )
    prep_data = prepare(model.model, doc_term_matrix, vectorizer, mds=mds)
    out = StringIO()
    save_html(prep_data, out)
    out.seek(0)
    return (doc_term_matrix, out.read())


def termite_visualization(corpus, topics, num_docs=None, min_df=0.1, ngrams=1,
                          weighting='tf', max_df=0.7, *args, **kwargs):
    model, doc_term_matrix, vectorizer = build_model(
        corpus, topics, ngrams, num_docs, weighting, min_df, max_df
    )
    out = StringIO()
    id2term = vectorizer.id_to_term
    model.termite_plot(doc_term_matrix, id2term, save=out)
    out.seek(0)
    return (doc_term_matrix, out.read())


def wordcloud_visualization(corpus, topics, num_docs=None, min_df=0.1,
                            ngrams=1, weighting='tf', max_df=0.7, mds='pcoa',
                            *args, **kwargs):
    font = pkg_resources.resource_filename(__name__,
                                           "fonts/ZillaSlab-Medium.ttf")
    print(font)
    model, doc_term_matrix, vectorizer = build_model(
        corpus, topics, num_docs, ngrams, weighting, min_df, max_df
    )
    prep_data = prepare(model.model, doc_term_matrix, vectorizer, mds=mds)
    ti = prep_data.topic_info
    topic_labels = ti.groupby(['Category']).groups.keys()

    plt.clf()
    topics = []
    for label in topic_labels:
        out = StringIO()
        df = ti[ti.Category == label].sort_values(by='Total',
                                                     ascending=False)[:20]
        tf = dict(df[['Term', 'Total']].to_dict('split')['data'])

        wc = wordcloud.WordCloud(font_path=font, width=600, height=300,
                                 background_color='white')
        wc.fit_words(tf)
        plt.imshow(wc)
        plt.axis('off')
        plt.savefig(out)
        out.seek(0)
        topics.append((label, out.read()))

    return topics
    """
     Category         Freq            Term        Total  loglift  logprob
term
478   Default   738.000000          specie   738.000000   1.0000   1.0000
...       ...          ...             ...          ...      ...      ...
191   Topic10    25.344278           space   145.983738   1.8935  -5.0376
190   Topic10    32.076070           green   193.201661   1.8488  -4.8020
319   Topic10    12.129367          aspect    73.063725   1.8488  -5.7745

"""