from .base import BaseVectorizer
from .base import BaseTextU, BaseTextUE
from .base import BasePair, BasePairE

from .common import TextNormalizer
from .common import JiebaTokenizerE, JiebaTokenizer
from .ann import Ann

import paddle
import paddle.fluid as fluid

import os
import numpy as np


class PaddleBowVectorizer(BaseVectorizer):
    def __init__(self, vocab_file):
        self._vocab = self._load_vocab(vocab_file)


    def _load_vocab(self, file_path):
    	"""
    	load the given vocabulary
    	"""
    	vocab = {}
    	if not os.path.isfile(file_path):
    	    raise ValueError("vocabulary dose not exist under %s" % file_path)
    	with open(file_path, 'r', encoding="utf-8") as f:
    	    for line in f:
    	        items = line.strip('\n').split("\t")
    	        if items[0] not in vocab:
    	            vocab[items[0]] = int(items[1])
    	vocab["<unk>"] = 0
    	return vocab

    def transform(self, ares):
        words = ares
        vec = []
        for word in words:
            if word in self._vocab:
                vec.append(self._vocab[word])
            else:
                for char in word:
                    if char in self._vocab:
                        vec.append(self._vocab[char])
        if len(vec) == 0:
            vec = [0]
            raise Exception("{}: input vector is empty.".format(self.__class__.__name__))

        return vec


class PaddleBowTextU(BaseTextU):
    def __init__(self, paddle_vocab_path, user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        preprocessor = TextNormalizer()
        analyzer = self._instantiate_analyzer(user_dict_path= user_dict_path,
                                              stop_words_path=stop_words_path,
                                              syn_words_path=syn_words_path
                                             )
        vectorizer = PaddleBowVectorizer(paddle_vocab_path)
        super(PaddleBowTextU, self).__init__(preprocessor = preprocessor,
                                          analyzer = analyzer,
                                          vectorizer = vectorizer
                                         )

    def _instantiate_analyzer(self, user_dict_path,
                              stop_words_path,
                              syn_words_path
                             ):
        analyzer = JiebaTokenizer(user_dict_path= user_dict_path,
                                    stop_words_path=stop_words_path,
                                    syn_words_path=syn_words_path
                                   )       
        return analyzer


class PaddleBowSim(BasePair):
    def __init__(self, paddle_model_path,
                 paddle_vocab_path,
                 user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None,
                 use_cuda = False,
                 task_mode = 'pairwise'
                ):
        self.task_mode = task_mode
        # textu = PaddleBowTextU(paddle_vocab_path,
        #                        user_dict_path=user_dict_path,
        #                        stop_words_path=stop_words_path,
        #                        syn_words_path=syn_words_path
        #                       )
        textu = self._instantiate_textu(paddle_vocab_path,
                                        user_dict_path=user_dict_path,
                                        stop_words_path=stop_words_path,
                                        syn_words_path=syn_words_path
                                       )
        if use_cuda:
            place = fluid.CUDAPlace(0)
        else:
            place = fluid.CPUPlace()

        self.executor = fluid.Executor(place=place)
        self.program, self.feed_var_names, self.fetch_targets = fluid.io.load_inference_model(paddle_model_path, self.executor)
        self.infer_feeder = fluid.DataFeeder( place=place, feed_list=self.feed_var_names, program=self.program)
        super(PaddleBowSim, self).__init__(textu = textu)

    def _instantiate_textu(self, paddle_vocab_path, 
                           user_dict_path,
                           stop_words_path,
                           syn_words_path
                          ):
        textu = PaddleBowTextU(paddle_vocab_path,
                               user_dict_path=user_dict_path,
                               stop_words_path=stop_words_path,
                               syn_words_path=syn_words_path
                              )
        return textu


    def transform(self, vec1, vec2):
        output = self.executor.run(self.program,
                                   feed=self.infer_feeder.feed([[vec1, vec2]]),
                                   fetch_list=self.fetch_targets)
        if self.task_mode == 'pairwise':
            score = list( map(lambda item: (item[0] + 1) / 2, output[1]))[0]
        else:
            score = list(map(lambda item: np.argmax(item), output[1]))[0]

        res = {"score": score,
               "left_vec": output[0]
              }
        return res


class PaddleBowTextUE(PaddleBowTextU, BaseTextUE):
    def __init__(self, paddle_vocab_path, user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None
                ):
        PaddleBowTextU.__init__(self, paddle_vocab_path, user_dict_path,
                                stop_words_path,
                                syn_words_path
                               )

    def _instantiate_analyzer(self, user_dict_path,
                              stop_words_path,
                              syn_words_path
                             ):
        analyzer = JiebaTokenizerE(user_dict_path= user_dict_path,
                                    stop_words_path=stop_words_path,
                                    syn_words_path=syn_words_path
                                   )       
        return analyzer


class PaddleBowSimE(PaddleBowSim, BasePairE):
    def __init__(self, paddle_model_path,
                 paddle_vocab_path,
                 user_dict_path = None,
                 stop_words_path = None,
                 syn_words_path = None,
                 use_cuda = False,
                 task_mode = 'pairwise'
                ):
        PaddleBowSim.__init__(self, paddle_model_path, 
                              paddle_vocab_path,
                              user_dict_path,
                              stop_words_path,
                              syn_words_path,
                              use_cuda,
                              task_mode
                             )

    def _instantiate_textu(self, paddle_vocab_path, 
                           user_dict_path,
                           stop_words_path,
                           syn_words_path
                          ):
        textu = PaddleBowTextUE(paddle_vocab_path,
                               user_dict_path=user_dict_path,
                               stop_words_path=stop_words_path,
                               syn_words_path=syn_words_path
                              )
        return textu   
