class BaseAnalyzer(object):
    def __init__(self):
        pass

    def __call__(self, pair_ann):
        ptext1, ptext2 = pair_ann.get_ptext()
        ares1, ares2 = self.tranform(ptext1, ptext2)
        pair_ann.set_ares(ares1, ares2)
        return pair_ann

    def tranform(self, text1, text2):
        """
        对两段文本分别进行词法和语法等相关分析，
        分别返回各自的分析结果
        return ares1, ares2
        ares1和ares2是两个包含token对象的列表
        """
        raise NotImplementedError
