from .base_preprocessor import BasePreprocessor

class DummyPreprocessor(BasePreprocessor):
    def tranform(self, text1, text2):
        return text1, text2
