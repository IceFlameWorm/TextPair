class BaseModel(object):
    def __init__(self):
        pass

    def __call__(self, pair_ann):
        vec1, vec2 = pair_ann.get_vec()
        score = self.tranform(vec1, vec2)
        pair_ann.set_score(score)
        return pair_ann

    def tranform(self, vec1, vec2):
        """
        根据两段文本的特征向量作为输入，计算出两段文本比较结果。
        retur score
        """
        raise NotImplementedError`
