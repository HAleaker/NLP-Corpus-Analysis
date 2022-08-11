class ClassVocab:
    def __init__(self):
        self.vocab = {}

    def __getitem__(self, k):
        if isinstance(k, float):
            k = 'empty'
        k = [x for x in k.split('/') if x][0]

        if k not in self.vocab:
            x = len(self.vocab)
            self.vocab[k] = x

            return x

        return self.vocab[k]


def train_model(corpus):
    # conventions: X are features, y are labels
    # X_train is array of training feature values,
    # X_test is array with test values
    # y_train are labels for X_train, y_test are labels for X_test

    from sklearn import metrics
    from sklearn.model_selection import train_test_split
    from itertools import tee

    docs = (doc for doc in corpus
            if not isinstance(doc.metadata['Category Path'], float))
    docs_stream, meta_stream = tee(docs, 2)

    print("Transforming docs")
    docs = [doc.text for doc in docs_stream]

    from sklearn.feature_extraction.text import CountVectorizer
    vect = CountVectorizer(input='content', strip_accents='unicode',
                           tokenizer=tokenizer,  # stop_words='english',
                           max_features=5000)

    X = vect.fit_transform(docs)

    from sklearn.feature_extraction.text import TfidfTransformer
    transf = TfidfTransformer()
    X = transf.fit_transform(X)
    # X = X.toarray()   # only needed for GDC

    # from sklearn.feature_extraction.text import TfidfVectorizer
    # vect = TfidfV