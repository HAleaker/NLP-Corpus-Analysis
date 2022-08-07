class ClassVocab:
    def __init__(self):
        self.vocab = {}

    def __getitem__(self, k):
        if isinstance(k, float):
            k = 'empty'
        k = [x for x in k.split('/') if x][0]

     