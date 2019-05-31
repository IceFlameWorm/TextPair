class BaseModel(object):
    def __init__(self, model_file):
        self.model = self.load(model_file)

    def load(self, model_file):
        raise NotImplementedError

    def __call__(self, inp1, inp2):
        res = self.model(inp1, inp2)
        return res


class BertCharModel(BaseModel):
    def __init__(self):
        pass

    def load(self, model_file):
        pass
