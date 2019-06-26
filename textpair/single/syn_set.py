class SynSet(object):
    def __init__(self, words):
        self.father_dict = {}
        self.size_dict = {}
        self.count = len(words)

        for w in words:
            self.father_dict[w] = w
            self.size_dict[w] = 1

    def find_head(self, w):
        if w not in self.father_dict:
            return

        father = self.father_dict[w]
        if w != father:
            father = self.find_head(father)
        self.father_dict[w] = father
        return father

    def is_same_set(self, w1, w2):
        return self.find_head(w1) == self.find_head(w2)

    def union(self, w1, w2):
        if w1 not in self.father_dict or w2 not in self.father_dict:
            return

        w1_head = self.find_head(w1)
        w2_head = self.find_head(w2)

        if w1_head != w2_head:
            w1_set_size = self.size_dict[w1_head]
            w2_set_size = self.size_dict[w2_head]
            if w1_set_size >= w2_set_size:
                self.father_dict[w2_head] = w1_head
                self.size_dict[w1_head] = w1_set_size + w2_set_size
            else:
                self.father_dict[w1_head] = w2_head
                self.size_dict[w2_head] = w1_set_size + w2_set_size
            self.count -= 1