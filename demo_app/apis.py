from .app import app
from flask import request, jsonify
from flask import make_response, abort, send_file, send_from_directory

from textpair.single.paddle_bow import PaddleBowSimE
from textpair.single.simple_bert import BertSim2E
from textpair.single.ann import Ann

from .auth import access_token_required

import json
import os
FILE_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(FILE_PATH, '../data')

BERT_PATH = os.path.join(DATA_PATH, 'bert/pytorch')
BERT_MODEL_PATH = os.path.join(BERT_PATH, 'bert-base-chinese.tar.gz')
BERT_VOCAB_PATH = os.path.join(BERT_PATH, 'bert-base-chinese-vocab.txt')

PADDLE_PATH = os.path.join(DATA_PATH, 'paddle_models/sim_net')
PADDLE_MODEL_PATH = os.path.join(PADDLE_PATH, 'model_files/simnet_bow_pairwise_pretrained_model')
PADDLE_VOCAB_PATH = os.path.join(PADDLE_PATH, 'data/term2id.dict')


class SimFactory(object):
    _mapi = {'simple_bert': None,
             'paddle_bow': None
            }

    _mapc = {"simple_bert": lambda: BertSim2E(bert_model_path = BERT_MODEL_PATH, bert_vocab_path = BERT_VOCAB_PATH),
             "paddle_bow": lambda: PaddleBowSimE(paddle_model_path = PADDLE_MODEL_PATH, paddle_vocab_path = PADDLE_VOCAB_PATH)
            } 

    @classmethod
    def get_model(cls, name):
        if name not in cls._mapi:
            return

        if cls._mapi[name] is None:
            cls._mapi[name] = cls._mapc[name]()
        return cls._mapi[name]
            

@app.route("/sim", methods = ['POST'])
@access_token_required
def sim():
    res = {}
    try:
        req_data = request.get_data()
        req_dict = json.loads(req_data)
    except Exception as e:
        res['status'] = -1
        res['msg'] = "failed to parse request body."
        print(e)
        return jsonify(res)
    
    text1 = req_dict.get('text1')
    text2 = req_dict.get('text2')
    if text1 is None or text2 is None:
        res['status'] = -2
        res['msg'] = 'error: text1 or text2 is not set.'
        return jsonify(res)
    
    res['text1'] = text1
    res['text2'] = text2

    model_name = req_dict.get('model', 'simple_bert')
    model = SimFactory.get_model(model_name)

    if model is None:
        res['status'] = -3
        res['msg'] = "no available model"
        return jsonify(res)

    model.reset_tokenizer()
    user_dict_str = req_dict.get('user_dict_str')
    if user_dict_str is not None:
        try:
            model.sub_tokenizer(user_dict_str)
        except Exception as e:
            res['status'] = -4
            res['msg'] = 'Error: failed to sub tokenizer, please check the format.'
            print(e)
            return jsonify(res)

    model.reset_stop_words_set()
    stop_words_str = req_dict.get('stop_words_str')
    if stop_words_str is not None:
        try:
            model.sub_stop_words_set(stop_words_str)
        except Exception as e:
           res['status'] = -5
           res['msg'] = 'Error: failed to sub stop_words, please check the format.'
           print(e)
           return jsonify(res)
       
    model.reset_syn_set()
    syn_words_str = req_dict.get('syn_words_str')
    if syn_words_str is not None:
        try:
            model.sub_syn_set(syn_words_str)
        except Exception as e:
            res['status'] = -6
            res['msg'] = 'Error: failed to sub syn_set, please check the format.'
            print(e)
            return jsonify(res)

    try:
        ann1 = Ann(text1)
        ann2 = Ann(text2)
        out = model(ann1, ann2)
    except Exception as e:
        res['status'] = -7
        res['msg'] = "error: failed to run the model."
        print(e)
        return jsonify(res)
    else:
        res['status'] = 0
        res['msg'] = 'successful'
        res['words1'] = ann1.ares
        res['words2'] = ann2.ares
        res['model'] = model_name
        res['score'] = float(out['score'])
        return jsonify(res)



SAMPLES_DIR = os.path.join(FILE_PATH, 'static/samples')

@app.route('/samples/<file_name>', methods = ['GET'])
def download_samples(file_name):
    fp = os.path.join(SAMPLES_DIR, file_name)
    if not os.path.exists(fp):
        abort(404)
    
    resp = make_response(send_file(fp, as_attachment=True))
    return resp


ACCESS_TOKEN_TXT = os.path.join(FILE_PATH, 'access_token.txt')
@app.route('/access_token', methods = ['GET'])
def get_access_token():
    with open(ACCESS_TOKEN_TXT, 'r') as f:
        return f.read().strip()