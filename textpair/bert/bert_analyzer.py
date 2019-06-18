from ..base.base_analyzer import BaseAnalyzer

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
