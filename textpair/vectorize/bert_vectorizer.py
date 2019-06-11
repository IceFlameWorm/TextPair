from .base_vectorizer import BaseVectorizer


class BertVectorizer(BaseVectorizer):
    def __init__(self, token2index):
        self.token2index = self.token2index

    def tranform(self, ares1, ares2):
        vec1 = []
        vec2 = []
        for tk in ares1:
            vec1.append(self.token2index[tk.text]) # 要处理未登录符号

        for tk in ares2:
            vec2.append(self.token2index[tk.text]) # 要处理未登录符号
        return vec1, vec2
