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
        raise NotImplementedError


class BaseSemantic(object):
    def __init__(self, preprocessor,
                 analyzer,
                 vectorizer,
                 model
                ):
        self.preprocessor = preprocessor
        self.analyzer = analyzer
        self.vectorizer = vectorizer
        self.model = model

    def __call__(self, pair_ann):
        pair_ann = self.preprocessor(pair_ann)
        pair_ann = self.analyzer(pair_ann)
        pair_ann = self.vectorizer(pair_ann)
        pair_ann = self.model(pair_ann)
        return pair_ann