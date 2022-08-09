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

    docs = (doc for doc in corpu