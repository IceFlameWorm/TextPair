from .base import BasePreprocessor
from .base import BaseAnalyzer

import re
import jieba
from snownlp import SnowNLP

class DummyPreprocessor(BasePreprocessor):
    def transform(self, text):
        return text


class TextNormalizer(BasePreprocessor):
    """
    主要功能：
        1. 去除特殊符号（标点、空格等），只保留中文、英文、数字等
        2. 中文繁体转换为简体
        3. 英文统一为小写
    """
    def __init__(self):
        pass

    def transform(self, text):
        ## 去除特殊符号
        pattern = r"[^\u4e00-\u9fa5^a-z^A-Z^0-9]" # 非常见中中英文数字字符
        ptext = re.sub(pattern, '', text)

        ## 中文繁体转简体
        snow = SnowNLP(ptext)
        ptext = snow.han

        ## 英文统一为小写
        ptext = ptext.lower()
        return ptext


class JiebaTokenizer(BaseAnalyzer):
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
