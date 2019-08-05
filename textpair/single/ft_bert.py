
import torch

from .simple_bert import BertPreprocessor, BertPreprocessorE
from .simple_bert import BertAnalyzer

from .base import *

from pytorch_pretrained_bert import BertForPointWiseClassification
from pytorch_pretrained_bert import BertTokenizer


class FtBertVectorizer(BaseVectorizer):
    def __init__(self, bert_tokenizer):
        self.bert_tokenizer = bert_tokenizer

    def transform(self, ares):
        tokens = ares
        token_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        segments = [0] * len(token_ids)

        tokens_tensor = torch.tensor([token_ids])
        segments_tensor = torch.tensor([segments])
        
        vec = {'tokens_tensor': tokens_tensor,
               'segments_tensor': segments_tensor
              }
        return vec


class FtBertTextU(BaseTextU):
    def __init__(self, bert_vocab_path,
                 user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_vocab_path)
        self.bert_preprocessor = bert_preprocessor = self._instantiate_preprocessor(user_dict_path= user_dict_path,
                                             stop_words_path= stop_words_path,
                                             syn_words_path= syn_words_path
                                            )
        bert_analyzer = BertAnalyzer(self.bert_tokenizer)
        bert_vectorizer = FtBertVectorizer(self.bert_tokenizer)
        super(FtBertTextU, self).__init__(preprocessor = bert_preprocessor,
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


class FtBertSim(BasePair):
    def __init__(self, bert_model_path,
                 bert_vocab_path
                ):
        self.bert_model = BertForPointWiseClassification.from_pretrained(bert_model_path)
        textu = self._instantiate_textu(bert_vocab_path)
        super(FtBertSim, self).__init__(textu = textu)

    def _instantiate_textu(self, bert_vocab_path):
        textu = FtBertTextU(bert_vocab_path)
        return textu

    def transform(self, vec1, vec2):
        tokens_tensor1 = vec1['tokens_tensor']
        segments_tensor1 = vec1['segments_tensor']
        tokens_tensor2 = vec2['tokens_tensor']
        segments_tensor2 = vec2['segments_tensor']

        self.bert_model.eval()
        with torch.no_grad():
            logits, left_vec, right_vec = self.bert_model(tokens_tensor1,
                                                          tokens_tensor2,
                                                          segments_tensor1,
                                                          segments_tensor2
                                                         )
            probs = torch.softmax(logits, dim = -1)
        res = {'score': probs[0, 1].item(),
               'left_vec': left_vec.cpu().numpy()
              }
        return res


class FtBertTextUE(FtBertTextU, BaseTextUE):
    def __init__(self, bert_vocab_path,
                 user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        FtBertTextU.__init__(self, bert_vocab_path,
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


class FtBertSimE(FtBertSim, BasePairE):
    def __init__(self, bert_model_path,
                 bert_vocab_path
                ):
        FtBertSim.__init__(self, bert_model_path, bert_vocab_path)

    def _instantiate_textu(self, bert_vocab_path):
        textu = FtBertTextUE(bert_vocab_path)
        return textu