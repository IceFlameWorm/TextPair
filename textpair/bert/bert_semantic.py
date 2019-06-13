from ..base.base_semantic import BaseSemantic
from .bert_preprocessor import BertPreprocessor
from .bert_analyzer import BertAnalyzer
from .bert_vectorizer import BertVectorizer
from .bert_model import BertModel as BertSimModel # 为了与pytorch的bert模型区分
from pytorch_pretrained_bert import BertTokenizer, BertModel


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
