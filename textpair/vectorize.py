class BaseVectorizer(object):
    def __init__(self):
        pass

    def __call__(self, ar):
        raise NotImplementedError


class BertCharIndexer(BaseVectorizer):
    def __init__(self, token2index):
        self.token2index = token2index

    def __call__(self, ar):
        pass
