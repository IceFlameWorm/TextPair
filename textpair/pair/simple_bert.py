from .base import BasePreprocessor
from .base import BaseAnalyzer
from .base import BaseVectorizer
from .base import BaseModel
from .base import BaseSemantic

from pytorch_pretrained_bert import BertTokenizer, BertModel

import torch

from sklearn.metrics.pairwise import cosine_similarity

class BertPreprocessor(BasePreprocessor):
    def transform(self, text1, text2):
        return text1, text2


class BertAnalyzer(BaseAnalyzer):
    def __init__(self, bert_tokenizer):
        """
        bert_tokenizer: 目前用的是pytorch_pretrained_bert中的BertTokenizer实例
        """
        self.bert_tokenizer = bert_tokenizer

    def tranform(self, ptext1, ptext2):
        # 应该是以字符的模式进行tokenize
        # tokens1和tokens2都是list
        cls_token = ["[CLS]"]
        sep_token = ["[SEP]"]
        tokens1 = cls_token + self.bert_tokenizer.tokenize(ptext1) + sep_token
        tokens2 = cls_token + self.bert_tokenizer.tokenize(ptext2) + sep_token
        return tokens1, tokens2


class BertVectorizer(BaseVectorizer):
    def __init__(self, bert_tokenizer):
        """
        bert_tokenizer: 目前用的是pytorch_pretrained_bert中的BertTokenizer实例
        """
        self.bert_tokenizer = bert_tokenizer

    def tranform(self, ares1, ares2):
        tokens1, tokens2 = ares1, ares2 # 这里 ares中保存的是token列表
        token_ids1 = self.bert_tokenizer.convert_tokens_to_ids(tokens1)
        token_ids2 = self.bert_tokenizer.convert_tokens_to_ids(tokens2)
        segments1 = [0] * len(token_ids1)
        segments2 = [0] * len(token_ids2)

        TOKENS_TENSOR = "tokens_tensor"
        SEGMENTS_TENSOR = "segments_tensor"

        vec1 = {TOKENS_TENSOR: torch.tensor([token_ids1]),
                SEGMENTS_TENSOR: torch.tensor([segments1])
               }
        vec2 = {TOKENS_TENSOR: torch.tensor([token_ids2]),
                SEGMENTS_TENSOR: torch.tensor([segments2])
               }

        return vec1, vec2



class BertSimModel(BaseModel):
    def __init__(self, bert_model):
        """
        bert_model 目前用的是pytorch_pretrained_bert中的BertModel实例
        """
        self.bert_model = bert_model
        self.bert_model.eval()

    def tranform(self, vec1, vec2):
        # 这里的vec1 和 vec2 是字典保存了 tokens_tensor和segments_tensor
        TOKENS_TENSOR = "tokens_tensor"
        SEGMENTS_TENSOR = "segments_tensor"

        tokens_tensor1 = vec1[TOKENS_TENSOR]
        segments_tensor1 = vec1[SEGMENTS_TENSOR]

        tokens_tensor2 = vec2[TOKENS_TENSOR]
        segments_tensor2 = vec2[SEGMENTS_TENSOR]

        with torch.no_grad():
            encoded_layers1, _ = self.bert_model(tokens_tensor1, segments_tensor1)
            encoded_layers2, _ = self.bert_model(tokens_tensor2, segments_tensor2)

        # 取最后一层的[CLS]的向量作为句子的向量
        cls1 = encoded_layers1[-1].numpy()[:,0,:]
        cls2 = encoded_layers2[-1].numpy()[:,0,:]

        # 利用余弦相似度计算相似度
        score = cosine_similarity(cls1, cls2)[0, 0]
        return score


class BertSemantic(BaseSemantic):
    def __init__(self, bert_model_file,
                 bert_vocab_file
                ):
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_vocab_file)
        self.bert_model = BertModel.from_pretrained(bert_model_file)
        self.bert_preprocessor = BertPreprocessor()
        self.bert_analyzer = BertAnalyzer(self.bert_tokenizer)
        self.bert_vectorizer = BertVectorizer(self.bert_tokenizer)
        self.bert_sim_model = BertSimModel(self.bert_model)
        super(BertSemantic, self).__init__(preprocessor =
                                           self.bert_preprocessor,
                                           analyzer = self.bert_analyzer,
                                           vectorizer = self.bert_vectorizer,
                                           model = self.bert_sim_model
                                          )