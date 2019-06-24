import torch
from .base import *
from .ann import Ann
from pytorch_pretrained_bert import BertTokenizer, BertModel
from .common import DummyPreprocessor as BertPreprocessor

class BertAnalyzer(BaseAnlyzer):
    def __init__(self, bert_tokenizer):
        self.bert_tokenizer = bert_tokenizer

    def transform(self, ptext):
        cls_token = ["[CLS]"]
        sep_token = ["[SEP]"]
        tokens = self.bert_tokenizer.tokenize(ptext)
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
    def __init__(self, bert_model_file,
                 bert_vocab_file
                ):
        self.bert_model = BertModel.from_pretrained(bert_model_file)
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_vocab_file)
        bert_preprocessor = BertPreprocessor()
        bert_analyzer = BertAnalyzer(self.bert_tokenizer)
        bert_vectorizer = BertVectorizer(self.bert_model, self.bert_tokenizer)
        super(BertTextU, self).__init__(preprocessor = bert_preprocessor,
                                        analyzer = bert_analyzer,
                                        vectorizer = bert_vectorizer
                                       )


if __name__ == "__main__":
    import os
    fpath = os.path.dirname(__file__)
    BERT_MODEL_FILE = os.path.join(fpath, '../data/bert/pytorch/bert-base-chinese.tar.gz')
    BERT_VOCAB_FILE = os.path.join(fpath, '../data/bert/pytorch/bert-base-chinese-vocab.txt')
    textu = BertTextU(BERT_MODEL_FILE, BERT_VOCAB_FILE)
    ann = Ann("今天天气怎么样")
    ann = textu(ann)
    print(ann.vec)

