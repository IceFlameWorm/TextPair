class BasePreprocessor(object):
    def __init__(self):
        pass

    def __call__(self, pair_ann):
        text1, text2 = pair_ann.get_rawtext()
        ptext1, ptext2 = self.transform(text1, text2)
        pair_ann.set_ptext(ptext1, ptext2)
        return pair_ann

    def transform(self, text1, text2):
        """
        对两段文本进行预处理，比如繁体转简体等。
        将两段处理后的文本返回
        return ptext1, ptext2
        """
        raise NotImplementedError
