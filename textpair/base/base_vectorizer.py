class BaseVectorizer(object):
    def __init__(self):
        pass

    def __call__(self, pair_ann):
        ares1, ares2 = pair_ann.get_ares()
        vec1, vec2 = self.tranform(ares1, ares2)
        pair_ann.set_vec(vec1, vec2)
        return pair_ann

    def tranform(self, ares1, ares2):
        """
        把词法，语法分析的结果向量化，比如转化成index
        return vec1, vec2
        """
        raise NotImplementedError

