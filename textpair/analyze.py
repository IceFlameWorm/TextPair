import jieba

"""
目前实现的对文本的NLP处理只有分词，输入是一段文本，返回是分词结果列表。
"""
class BaseTokenizer(BaseAnalyzer):
    def __init__(self, char_grain = False):
        self.char_grain = char_grain


    def __call__(self, txt):
        raise NotImplementedError


class BertTokenizer(BaseTokenizer):
    def __call__(self, txt):
        if self.char_grain:
            pass
        else:
            pass
