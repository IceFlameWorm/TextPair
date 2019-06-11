class PairAnn(object):
    def __init__(self, text1, text2):
        self.text1 = text1
        self.text2 = text2

    def get_rawtext(self):
        return self.text1, self.text2

    def set_ptext(self, ptext1, ptext2):
        self.ptext1 = ptext1
        self.ptext2 = ptext2

    def get_ptext(self):
        return self.ptext1, self.ptext2

    def set_ares(self, ares1, ares2):
        self.ares1 = ares1
        self.ares2 = ares2

    def get_ares(self):
        return self.ares1, self.ares2

    def set_vec(self, vec1, vec2):
        self.vec1 = vec1
        self.vec2 = vec2

    def get_vec(self):
        return self.vec1, self.vec2

    def set_score(self, score):
        self.score = score

    def get_score(self):
        return self.score
