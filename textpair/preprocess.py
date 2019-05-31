class BasePreprocessor(object):
    """
    对输入的文本进行预处理，处理的结果仍然是文本。
    """
    def __init__(self):
        pass

    def __call__(self, txt):
        """
        Args:
            txt: str

        Returns:
            str
        """
        raise NotImplementedError


class DummyPreprocessor(BasePreprocessor):
    def __call__(self, txt):
        return txt
