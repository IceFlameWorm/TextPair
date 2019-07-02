# Text Pair

NLP中有不少任务涉及比较两段文本的关系，比如词义相似度、语义相似度、字面相似度、文本蕴含、信息检索、FAQ问答等。在不断的学习、探索和实践过程中，尽力尝试把有有关两段文本关系的一些功能实现出来，方便后续的使用。

## 基本框架与流程
初步设计的流程包含以下四个部分：

1. 预处理
2. NLP分析
3. NLU
4. 关系模型

### 预处理

预处理主要负责对原始文本进行一些诸如繁简转化、数字转文本一类的处理，输入是原始文本，输出是处理过的文本。

### NLP分析
对与处理过的文本进行词法、语法相关的分析。输入是预处理过的文本，输出是NLP分析的结果，比如分词，POS，语法树等。

### NLU
基于NLP分析的结果进行自然语言理解，其实就是向量化或者特征提取

### 关系模型
基于NLP分析的结果或者向量化的结果，预测两段文本之间的关系。

## 目前进展
1. 文本预处理的模块：保留中英文和数字，字符小写，繁体变简体，详见 `textpair/single/common.py`中的`TextNormalizer`
2. 分词模块
    1. 对jieba进行了封装
    2. 支持加载用户词表、停用词表和同义词表
    3. 支持在jieba分词的结果上进行同义词转换
3. 基于预训练的中文bert模型+余弦相似度实现了简单的中文语义相似度比较，demo请参见 
    1. 不做预处理：`notebooks/bert_sim_test_[single | pair].ipynb`
    2. 预处理版本：`notebooks/bert_sim_2_test_single.ipynb`
4. 对百度预训练的语义相似度模型进行了封装，demo请参见 `notebooks/paddle_sim_test.ipynb`
5. 文本相似度 web demo，在项目根目录下运行 ```python run.py```，在浏览器访问 `http://127.0.0.1:5000`
6. 语义相似度接口 /sim，目前使用POST方法调用
    1. request header：`Content-Type：application/json`
    2. request body, 示例如下
        ```
        {
            "text1": "大家好才是真的好",
            "text2": "新闻联播每天播放",
            "model": "paddle_bow" # 目前支持 simple_bert 和 paddle_bow，默认为 paddle_bow
        }
        ```
    3. response, 示例如下：
        ```
        {
            "model": "paddle_bow",
            "msg": "successful",
            "score": 0.6761486232280731,
            "status": 0,
            "words1": [
                "大家",
                "好",
                "才",
                "是",
                "真的",
                "好"
            ],
            "words2": [
                "新闻联播",
                "每天",
                "播放"
            ]
        }
        ```