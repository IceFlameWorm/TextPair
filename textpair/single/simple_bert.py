import torch
from .base import *
from .ann import Ann
from pytorch_pretrained_bert import BertTokenizer, BertModel
from .common import TextNormalizer
from .common import JiebaTokenizerE, JiebaTokenizer

from sklearn.metrics.pairwise import cosine_similarity

class BertAnalyzer(BaseAnalyzer):
    def __init__(self, bert_tokenizer):
        self.bert_tokenizer = bert_tokenizer

    def transform(self, ptext):
        cls_token = ["[CLS]"]
        sep_token = ["[SEP]"]
        tokens = self.bert_tokenizer.tokenize(ptext)
        if len(tokens) == 0:
            raise Exception('{}: there are no input tokens.'.format(self.__class__.__name__))
        return cls_token + tokens + sep_token


class BertVectorizer(BaseVectorizer):
    def __init__(self, bert_model, bert_tokenizer):
        self.bert_model = bert_model
        self.bert_tokenizer = bert_tokenizer

    def transform(self, ares):
        tokens = ares
        token_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        segments = [0] * len(token_ids)

        tokens_tensor = torch.tensor([token_ids])
        segments_tensor = torch.tensor([segments])

        self.bert_model.eval()
        with torch.no_grad():
            encoded_layers, _ = self.bert_model(tokens_tensor, segments_tensor)

        cls = encoded_layers[-1].numpy()[:,0,:]
        return cls


class BertTextU(BaseTextU):
    def __init__(self, bert_model_path,
                 bert_vocab_path
                ):
        self.bert_model = BertModel.from_pretrained(bert_model_path)
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_vocab_path)
        bert_preprocessor = TextNormalizer()
        bert_analyzer = BertAnalyzer(self.bert_tokenizer)
        bert_vectorizer = BertVectorizer(self.bert_model, self.bert_tokenizer)
        super(BertTextU, self).__init__(preprocessor = bert_preprocessor,
                                        analyzer = bert_analyzer,
                                        vectorizer = bert_vectorizer
                                       )


class BertSim(BasePair):
    def __init__(self, bert_model_path,
                 bert_vocab_path
                ):
        textu = BertTextU(bert_model_path, bert_vocab_path)
        super(BertSim, self).__init__(textu = textu)

    def transform(self, vec1, vec2):
        score = (cosine_similarity(vec1, vec2)[0, 0] + 1.0) / 2.0
        res = {'score': score}
        return res


class BertPreprocessor(BasePreprocessor):
    def __init__(self, user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        self.preprocessor = TextNormalizer()
        self.analyzer = self._instantiate_tokenizer(user_dict_path= user_dict_path,
                                                     stop_words_path= stop_words_path,
                                                     syn_words_path= syn_words_path
                                                    )

    def _instantiate_tokenizer(self, user_dict_path,
                               stop_words_path,
                               syn_words_path
                              ):
        analyzer = JiebaTokenizer(user_dict_path= user_dict_path,
                                  stop_words_path= stop_words_path,
                                  syn_words_path= syn_words_path
                                 )
        return analyzer

    def transform(self, text):
        _ptext = self.preprocessor.transform(text)
        words = self.analyzer.transform(_ptext)
        ptext = "".join(words)
        return ptext


class BertTextU2(BaseTextU):
    def __init__(self, bert_model_path,
                 bert_vocab_path,
                 user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        self.bert_model = BertModel.from_pretrained(bert_model_path)
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_vocab_path)
        self.bert_preprocessor = bert_preprocessor = self._instantiate_preprocessor(user_dict_path= user_dict_path,
                                             stop_words_path= stop_words_path,
                                             syn_words_path= syn_words_path
                                            )
        bert_analyzer = BertAnalyzer(self.bert_tokenizer)
        bert_vectorizer = BertVectorizer(self.bert_model, self.bert_tokenizer)
        super(BertTextU2, self).__init__(preprocessor = bert_preprocessor,
                                        analyzer = bert_analyzer,
                                        vectorizer = bert_vectorizer
                                       )

    def _instantiate_preprocessor(self, user_dict_path,
                                  stop_words_path,
                                  syn_words_path
                                 ):
        bert_preprocessor = BertPreprocessor(user_dict_path= user_dict_path,
                                             stop_words_path= stop_words_path,
                                             syn_words_path= syn_words_path
                                            )
        return bert_preprocessor



class BertSim2(BasePair):
    def __init__(self, bert_model_path,
                 bert_vocab_path
                ):
        textu = self._instantiate_textu(bert_model_path, bert_vocab_path)
        super(BertSim2, self).__init__(textu = textu)

    def _instantiate_textu(self, bert_model_path, bert_vocab_path):
        textu = BertTextU2(bert_model_path, bert_vocab_path)
        return textu

    def transform(self, vec1, vec2):
        score = (cosine_similarity(vec1, vec2)[0, 0] + 1.0) / 2.0
        res = {'score': score}
        return res


class BertPreprocessorE(BertPreprocessor):
    def __init__(self, user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        super(BertPreprocessorE, self).__init__(user_dict_path,
                                                stop_words_path,
                                                syn_words_path
                                               )


    def _instantiate_tokenizer(self, user_dict_path,
                               stop_words_path,
                               syn_words_path
                              ):
        analyzer = JiebaTokenizerE(user_dict_path= user_dict_path,
                                  stop_words_path= stop_words_path,
                                  syn_words_path= syn_words_path
                                 )
        return analyzer


class BertTextU2E(BertTextU2, BaseTextUE):
    def __init__(self, bert_model_path,
                 bert_vocab_path,
                 user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        BertTextU2.__init__(self, bert_model_path,
                            bert_vocab_path,
                            user_dict_path,
                            stop_words_path,
                            syn_words_path
                           )


    def _instantiate_preprocessor(self, user_dict_path,
                                  stop_words_path,
                                  syn_words_path
                                 ):
        bert_preprocessor = BertPreprocessorE(user_dict_path= user_dict_path,
                                             stop_words_path= stop_words_path,
                                             syn_words_path= syn_words_path
                                            )
        return bert_preprocessor


    def _get_analyzer(self):
        return self.bert_preprocessor.analyzer


class BertSim2E(BertSim2, BasePairE):
    def __init__(self, bert_model_path,
                 bert_vocab_path
                ):
        BertSim2.__init__(self, bert_model_path, bert_vocab_path)

    def _instantiate_textu(self, bert_model_path, bert_vocab_path):
        textu = BertTextU2E(bert_model_path, bert_vocab_path)
        return textu


if __name__ == "__main__":
    import os
    fpath = os.path.dirname(__file__)
    BERT_MODEL_FILE = os.path.join(fpath, '../data/bert/pytorch/bert-base-chinese.tar.gz')
    BERT_VOCAB_FILE = os.path.join(fpath, '../data/bert/pytorch/bert-base-chinese-vocab.txt')
    textu = BertTextU(BERT_MODEL_FILE, BERT_VOCAB_FILE)
    ann = Ann("今天天气怎么样")
    ann = textu(ann)
    print(ann.vec)

