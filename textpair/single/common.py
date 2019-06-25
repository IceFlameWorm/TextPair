from .base import BasePreprocessor
from .base import BaseAnlyzer

import re
import jieba

class DummyPreprocessor(BasePreprocessor):
    def transform(self, text):
        return text


class PuncCleaner(BasePreprocessor):
    def __init__(self, puncs):
        self.puncs = puncs
        pass

    def transform(self, text):
        pass


class JiebaTokenizer(BaseAnlyzer):
    def __init__(self, user_vocab = None,
                 stop_words = None,
                 syn_words = None,
                 char_mode = False
                ):
        self.user_vocab = user_vocab
        self.stop_words = stop_words
        self.syn_words = syn_words
        self.char_mode = char_mode

        # 加载自定义词表

    def transform(self, text):
        # 分词
        words = jieba.cut(text)
        return words
        # 移除停用词，包括一些标点符号等

        # 同义词转换
        pass
