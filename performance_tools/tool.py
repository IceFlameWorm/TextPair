# coding=utf8
import keras
import h5py
from keras.callbacks import ModelCheckpoint,ReduceLROnPlateau
from keras import backend as K
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from keras.layers import Input, Flatten, Dense
from keras.models import Model
import os
import numpy as np
from PIL import Image
import traceback
from keras.models import model_from_json

def multi_processing(fn, args):
    from multiprocessing import Pool as Pool
    from multiprocessing import cpu_count as cpu_count
    try:
        pool10 = Pool(cpu_count())
        output = pool10.map(fn, args)
        pool10.close()
        pool10.join()
        return output
    except Exception, e:
        error_msg = " ".join([
            "哎呀！多进程报错了！",

            str(traceback.format_exc())
        ])

        raise Exception(error_msg)

def get_image_info(image_path):
    """
    get input x info
    """
    img_rows, img_cols=128,128
    im=Image.open(image_path).resize((img_rows, img_cols))
    im=np.array(im)
        
    #im=im.reshape(3,im.shape[0],im.shape[1])
   
    return im.astype('float32')
        

def get_target_imagepath(image_path,category_num):
    """
    category：
            0-userid,
            1-isbad,
            2-gender: 1 male,0 female,
            3-age
    """
    basename=os.path.basename(image_path).split(".")[0].split("_")
    an=int(basename[category_num])
    return an


       
def age_bucket(age,cut_bins,labels):
    """
    Input
    ----
    age : 20,45,32,11,34  list or array
    
    cut_bins: [0,20,30,40,50,100] 左闭右开
    
    lables : [1,2,3,4,5]

    Return
    -----
        array
    """
    
    age_new=pd.cut(age,right=False,bins=cut_bins,labels=labels)
    age_new=np.array(age_new)
    return age_new


def get_image_location_list(mypath,limit,category_num):
    """
    return: image_list,answer_list
    """
   
    image_list=[]
    answer_list=[]
    for parent, dirnames, filenames in os.walk(mypath, topdown=False):
        for ix, filename in enumerate(filenames[:limit]):
            image_path = os.path.join(parent, filename)
            an=get_target_imagepath(image_path,category_num)
            image_list.append(image_path)
            answer_list.append(an)
    return image_list,answer_list

def get_image_location(mypath,limit,category_num):
    """
    category：
            0-userid,
            1-isbad,
            2-gender: 1 male,0 female,
            3-age
            
    ------
    return: yield ('image_path', target_value)
    """
    for parent, dirnames, filenames in os.walk(mypath, topdown=False):
        for ix, filename in enumerate(filenames[:limit]):
            image_path = os.path.join(parent, filename)
            an=get_target_imagepath(image_path,category_num)
            
            yield image_path,an


def list_all_files(directory, extensions=None):
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            base, ext = os.path.splitext(filename)
            joined = os.path.join(root, filename)
            if extensions is None or ext.lower() in extensions:
                yield joined

def get_target_rate(y_data):
    """
    No return.
    print(Target rate : xxxx)
    """
    
    target_rate=sum(y_data[:,1])*1.0/len(y_data[:,1])
    print(('Target rate : {}'.format(target_rate)))



def load_model_from_json(json_path):
    """
    载入存好的网络结构
    
    input: json文件地址
    return: model
    """
    with open(json_path, 'r') as json_file:
        loaded_model_json=json_file.read()   
    model=model_from_json(loaded_model_json)
    
    return model

def image_save_npy(data,npy_name,save_path=None):
    """
    data: 处理好的图片数据
    npy_name： npy的文件名
    save_path：保存的路径
    ----
    No return
    
    """
    if save_path:
        path = os.path.join(save_path,npy_name+'.npy')
    else:
        path = npy_name+'.npy'
        
    np.save(path,data)











