class BasePreprocessor(object):
    def __init__(self):
        pass

    def __call__(self, ann):
        text = ann.text
        ptext = self.transform(text)
        ann.ptext = ptext
        return ann

    def transform(self, text):
        raise NotImplementedError


class BaseAnalyzer(object):
    def __init__(self):
        pass

    def __call__(self, ann):
        ptext = ann.ptext
        ares = self.transform(ptext)
        ann.ares = ares
        return ann

    def transform(self, ptext):
        raise NotImplementedError


class BaseVectorizer(object):
    def __init__(self):
        pass

    def __call__(self, ann):
        ares = ann.ares
        vec = self.transform(ares)
        ann.vec = vec
        return ann

    def transform(self, ares):
        raise NotImplementedError


class BaseTextU(object):
    def __init__(self, preprocessor,
                 analyzer,
                 vectorizer
                ):
        self.preprocessor = preprocessor
        self.analyzer = analyzer
        self.vectorizer = vectorizer

    def __call__(self, ann):
        ann = self.preprocessor(ann)
        ann = self.analyzer(ann)
        ann = self.vectorizer(ann)
        return ann


class BasePair(object):
    def __init__(self, textu):
        self._textu = textu

    def __call__(self, ann1, ann2):
        ann1 = self._textu(ann1)
        ann2 = self._textu(ann2)
        vec1 = ann1.vec
        vec2 = ann2.vec
        score = self.transform(vec1, vec2)
        return score

    def transform(self, vec1, vec2):
        raise NotImplementedError
