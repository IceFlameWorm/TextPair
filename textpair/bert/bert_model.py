from ..base.base_model import BaseModel

import torch
from sklearn.metrics.pairwise import cosine_similarity

class BertModel(BaseModel):
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
