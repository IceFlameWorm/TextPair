from .base_preprocessor import BasePreprocessor

class BertPreprocessor(BasePreprocessor):
    def tranform(self, text1, text2):
        cls_token = "[CLS]"
        sep_token = "[SEP]"
        ptext1 = cls_token + text1 + sep_token
        ptext2 = cls_token + text2 + sep_token
        return ptext1, ptext2
