import sys
sys.path.append('../')

from multiprocessing import Pool
from tqdm import tqdm

from textpair.single.paddle_bow import PaddleBowSim
from textpair.single.ann import Ann

import requests
import json

VOCAB_FILE = '../data/paddle_models/sim_net/data/term2id.dict'
MODEL_PATH = '../data/paddle_models/sim_net/model_files/simnet_bow_pairwise_pretrained_model/'

sim = PaddleBowSim(MODEL_PATH, VOCAB_FILE)
url = 'http://127.0.0.1:5000/sim'
model = 'paddle_bow'

def fun(pair):
    text1, text2 = pair
    data = {'text1': text1, 
            'text2': text2,
            'model': model
           }
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, data = json.dumps(data), headers = headers)
    resp_dict = resp.json()
    return resp_dict['score']


pairs = [('你好', '大家好'),
         ('今天天气不错', '你身体好些了吗'), 
         ('hello', 'world'),
         ('人民团体是指', '人民团体是什么'), 
         ('请问怎么注册账号','怎么注销账号')]  * 300

if __name__ == "__main__":
    ## 同步请求1
    scores1 = []
    for pair in tqdm(pairs):
        score1 = fun(pair)
        scores1.append(score1)

    ## 并发请求
    scores2 = []
    with Pool(processes = 4) as pool:
        with tqdm(total= len(pairs)) as pbar:
            for score2 in pool.imap(fun, pairs):
                scores2.append(score2)
                pbar.update(1)

    ## 同步请求3
    scores3 = []
    for pair in tqdm(pairs):
        score3 = fun(pair)
        scores3.append(score3)

    eps = 1e-8
    diff1 = [i for i in range(len(pairs)) if abs(scores1[i] - scores2[i]) > eps]
    diff2 = [i for i in range(len(pairs)) if abs(scores1[i] - scores3[i]) > eps]
    
    print('同步1与并发2不一致的结果为：', diff1)
    print('同步1与同步3不一致的结果为：', diff2)