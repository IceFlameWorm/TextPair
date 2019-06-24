class Ann(object):
    def __init__(self, text):
        self._text = text

    @property
    def text(self):
        return self._text

    @property
    def ptext(self):
        return self._ptext

    @ptext.setter
    def ptext(self, ptext):
        self._ptext = ptext

    @property
    def ares(self):
        return self._ares

    @ares.setter
    def ares(self, ares):
        self._ares = ares

    @property
    def vec(self):
        return self._vec

    @vec.setter
    def vec(self, vec):
        self._vec = vec

