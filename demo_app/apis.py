from .app import app
from flask import request, jsonify

from textpair.pair.simple_bert import BertSemantic
from textpair.pair.pair_ann import PairAnn

BERT_MODEL_FILE = './data/bert/pytorch/bert-base-chinese.tar.gz'
BERT_VOCAB_FILE = './data/bert/pytorch/bert-base-chinese-vocab.txt'

sim_pipeline = BertSemantic(bert_model_file = BERT_MODEL_FILE,
                            bert_vocab_file = BERT_VOCAB_FILE
                           )

@app.route("/sim")
def sim():
    res = {}
    text1 = request.args.get('text1')
    text2 = request.args.get('text2')
    if text1 is None or text2 is None:
        res['status'] = -1
        res['msg'] = 'error: text1 or text2 is not set.'
        return jsonify(res)
    
    ann = PairAnn(text1, text2)
    try:
        ann = sim_pipeline(ann)
    except Exception as e:
        res['status'] = -2
        res['msg'] = "error: failed to run the model."
        print(e)
        return jsonify(res)
    else:
        res['status'] = 0
        res['msg'] = 'successful'
        res['score'] = float(ann.score)
        return jsonify(res)
