class BasePair(object):
    def __init__(self, preprocessor,
                 analyzer,
                 vectorizer,
                 model,
                ):
        self.preprocessor = preprocessor
        self.analyzer = analyzer
        self.vectorizer = vectorizer
        self.model = model

    def __call__(self, txt1, txt2):
        inp1 = self.preprocessor(txt1)
        inp2 = self.preprocessor(txt2)

        inp1 = self.analyzer(inp1)
        inp2 = self.analyzer(inp2)

        inp1 = self.vectorizer(inp1)
        inp2 = self.vectorizer(inp2)

        score = self.model(inp1, inp2)
        return score
