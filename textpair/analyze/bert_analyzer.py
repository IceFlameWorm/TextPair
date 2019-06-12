from .base_analyzer import BaseAnalyzer

class BertAnalyzer(BaseAnalyzer):
    def __init__(self, bert_tokenizer):
        """
        bert_tokenizer: 目前用的是pytorch_pretrained_bert中的BertTokenizer实例
        """
        self.bert_tokenizer = bert_tokenizer

    def tranform(self, ptext1, ptext2):
        # 应该是以字符的模式进行tokenize
        # tokens1和tokens2都是list
        tokens1 = self.bert_tokenizer.tokenize(ptext1)
        tokens2 = self.bert_tokenizer.tokenize(ptext2)
        return tokens1, tokens1
