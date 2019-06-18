from ..base.base_preprocessor import BasePreprocessor

class BertPreprocessor(BasePreprocessor):
    def transform(self, text1, text2):
        return text1, text2
