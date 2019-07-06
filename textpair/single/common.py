from .base import BasePreprocessor
from .base import BaseAnalyzer
from .syn_set import SynSet

import os
import re
import jieba
from snownlp import SnowNLP
from collections import defaultdict
# from copy import deepcopy
from io import StringIO

from jieba import text_type
from jieba import re_userdict

class DummyPreprocessor(BasePreprocessor):
    def transform(self, text):
        return text


class TextNormalizer(BasePreprocessor):
    """
    主要功能：
        1. 去除特殊符号（标点等），只保留中文、英文、数字等
        2. 中文繁体转换为简体
        3. 英文统一为小写
    """
    def __init__(self):
        pass

    def transform(self, text):
        ## 去除特殊符号
        pattern = r"([^\u4e00-\u9fa5^a-z^A-Z^0-9^\s]|\^)" # 非常见中中英文数字字符, 保留空白字符, 防止相邻的英文单词合并到一起
        ptext = re.sub(pattern, '', text)
        # ptext = re.sub(r'\^', '', ptext)

        ## 中文繁体转简体
        if len(ptext) > 0: # 空字符串会报错
            snow = SnowNLP(ptext)
            ptext = snow.han

        ## 英文统一为小写
        ptext = ptext.lower()
        return ptext


class JiebaTokenizer(BaseAnalyzer):
    def __init__(self, user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None,
                 char_mode = False
                ):
        self.user_dict_path = user_dict_path
        self.stop_words_path = stop_words_path
        self.syn_words_path = syn_words_path
        self.char_mode = char_mode

        # 加载自定义词表
        self.tokenizer = self._load_user_dict(user_dict_path)
        self._tokenizer_bak = self.tokenizer

        # 加载停用词
        self.stop_words_set = self._load_stop_words(stop_words_path)
        self._stop_words_set_bak = self.stop_words_set

        # 加载同义词表
        self.syn_set = self._load_syn_words(self.syn_words_path)
        self._syn_set_bak = self.syn_set


    def _load_user_dict(self, user_dict_path):
        tokenizer = jieba.Tokenizer()
        if user_dict_path is None:
            return tokenizer
        
        if os.path.isfile(user_dict_path):
            tokenizer.load_userdict(user_dict_path)
        elif os.path.isdir(user_dict_path):
            for fn in os.listdir(user_dict_path):
                fp = os.path.join(user_dict_path, fn)
                if os.path.isfile(fp):
                    tokenizer.load_userdict(fp)
        return tokenizer

    def _load_stop_words(self, stop_words_path):
        if stop_words_path is None:
            return set()

        if os.path.isfile(stop_words_path):
            with open(stop_words_path, 'r') as f:
                return set(line.strip() for line in f)

        if os.path.isdir(stop_words_path):
            stop_words_set = set()
            for fn in os.listdir(stop_words_path):
                fp = os.path.join(stop_words_path, fn)
                if os.path.isfile(fp):
                    with open(fp, 'r') as f:
                        res = set(line.strip() for line in f)
                        stop_words_set.add(res)
            return stop_words_set

    def _load_syn_words(self, syn_words_path):
        """
        通过同义词文件构建同义词集
        """

        if syn_words_path is None:
            return

        fps = []
        if os.path.isfile(syn_words_path):
            fps.append(syn_words_path)
        elif os.path.isdir(syn_words_path):
            for fn in os.listdir(syn_words_path):
                fp = os.path.join(syn_words_path, fn)
                if os.path.isfile(fp):
                    fps.append(fp)

        syn_set_words = []
        word_pairs = []
        for fp in fps:
            with open(fp, 'r') as f:
                for line in f:
                    words = line.strip().split()
                    if len(words) < 2:
                        continue
                    syn_set_words += words
                    for word in words[1:]:
                        word_pairs.append((words[0], word))
        
        syn_set = SynSet(set(syn_set_words))
        for w1, w2 in word_pairs:
            syn_set.union(w1, w2)
        return syn_set

    def _syn_of(self, word):
        if self.syn_set is None:
            return word

        syn = self.syn_set.find_head(word)
        return word if syn is None else syn

    def transform(self, text):
        sub_texts = text.strip().split() # 根据空白字符进行split

        # 分词 + 移除停用词
        words = []
        for sub_t in sub_texts:
            sub_words = [word for word in self.tokenizer.cut(sub_t) if word not in self.stop_words_set]
            words += sub_words

        # 同义词转换
        words = [self._syn_of(word) for word in words]
        return words


class JiebaTokenizerE(JiebaTokenizer):

    def sub_syn_set(self, syn_words_str):
        # 分行
        lines = syn_words_str.split('\n')
        syn_set_words = []
        word_pairs = []
        for line in lines:
            words = line.strip().split()
            if len(words) < 2:
                continue
            syn_set_words += words
            for word in words[1:]:
                word_pairs.append((words[0], word))
        
        syn_set = SynSet(set(syn_set_words))
        for w1, w2 in word_pairs:
            syn_set.union(w1, w2)

        self.syn_set = syn_set

    def reset_syn_set(self):
        self.syn_set = self._syn_set_bak

    def sub_tokenizer(self, user_dict_str):
        tokenizer = jieba.Tokenizer()
        with StringIO(user_dict_str) as f:
            for lineno, ln in enumerate(f, 1):
                line = ln.strip()
                if not isinstance(line, text_type):
                    try:
                        line = line.decode('utf-8').lstrip('\ufeff')
                    except UnicodeDecodeError:
                        raise ValueError('dictionary file must be utf-8')
                if not line:
                    continue
                # match won't be None because there's at least one character
                word, freq, tag = re_userdict.match(line).groups()
                if freq is not None:
                    freq = freq.strip()
                if tag is not None:
                    tag = tag.strip()
                tokenizer.add_word(word, freq, tag)
        self.tokenizer = tokenizer

    def reset_tokenizer(self):
        self.tokenizer = self._tokenizer_bak

    def sub_stop_words_set(self, stop_words_str):
        with StringIO(stop_words_str) as f:
            self.stop_words_set =  set(line.strip() for line in f)

    def reset_stop_words_set(self):
        self.stop_words_set = self._stop_words_set_bak
           