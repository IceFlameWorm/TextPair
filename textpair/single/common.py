from .base import BasePreprocessor

class DummyPreprocessor(BasePreprocessor):
    def transform(self, text):
        return text