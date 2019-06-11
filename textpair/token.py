class Token(object):
    def __init__(self, text,
                 pos_label = None,
                 ner = None
                ):
        self.text = text
        self.pos_label = pos_label
        self.ner_label = ner_label
