class BaseSemantic(object):
    def __init__(self, preprocessor,
                 analyzer,
                 vectorizer,
                 model
                ):
        self.preprocessor = preprocessor
        self.analyzer = analyzer
        self.vectorizer = vectorizer
        self.model = model

    def __call__(self, pair_ann):
        pair_ann = self.preprocessor(pair_ann)
        pair_ann = self.analyzer(pair_ann)
        pair_ann = self.vectorizer(pair_ann)
        pair_ann = self.model(pair_ann)
        return pair_ann
