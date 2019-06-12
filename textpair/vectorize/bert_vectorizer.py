from .base_vectorizer import BaseVectorizer

import torch


class BertVectorizer(BaseVectorizer):
    def __init__(self, bert_tokenizer):
        """
        bert_tokenizer: 目前用的是pytorch_pretrained_bert中的BertTokenizer实例
        """
        self.bert_tokenizer = bert_tokenizer

    def tranform(self, ares1, ares2):
        tokens1, tokens2 = ares1, ares2 # 这里 ares中保存的是token列表
        token_ids1 = tokenizer.convert_tokens_to_ids(tokens1)
        token_ids2 = tokenizer.convert_tokens_to_ids(tokens2)
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
