# -*- coding=utf8 -*-
# !/usr/bin/env python

try:
    import cPickle
except:
    import pickle as cPickle

import csv
import json
import random
from datetime import datetime

import dateutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pylab as plb
import scipy.stats
from sklearn.metrics import roc_curve, auc

import contingency as cy


# warnings.filterwarnings('ignore')
# import logging

# logging.basicConfig(level=logging.INFO)
# formatter = logging.Formatter('[%(asctime)s] %(name)s-%(levelname)s: %(message)s')
# log = logging.getLogger('dc')
# log.setLevel(logging.INFO)


# get IRR
def compute_irr(start_principal, cashflow):
    tt = cashflow.copy()
    tt[0] = tt[0] - start_principal
    return np.irr(tt) * 12.0

# assign two-d woe
def assign_woe2(woes, bin1, bin2, values1, values2):
    results = np.zeros(values1.shape[0])
    for i in range(woes.shape[0]):
        for j in range(woes.shape[1]):
            ind = plb.find((values1>=bin1[i]) & (values1<bin1[i+1]) & \
                (values2>=bin2[j]) & (values2<bin2[j+1]))
            if ind.shape[0] > 0:
                results[ind] = woes[i]
    return results

# assign woe2
def assign_woe(woes, bins, values):
    results = np.zeros(values.shape[0])
    for i in range(woes.shape[0]):
        ind = plb.find((values>=bins[i]) & (values<bins[i+1]))
        if ind.shape[0] > 0:
            results[ind] = woes[i]
    return results


def assign_woe_discrete(woes, bins, values):
    results = np.zeros(values.shape[0])
    others = np.ones(values.shape[0])
    for i in range(len(woes)-1):
        inds = values==bins[i]
        others[plb.find(inds==True)] = 0
        if inds.shape[0] > 0:
            results[inds] = woes[i]
        results[plb.find(others==1)] = woes[-1]
    return results


# compute 2-d woe
def woe2(x1, x2, y, bin1=[], bin2=[]):
    l1 = len(bin1)
    l2 = len(bin2)
    woes = np.zeros((l1-1, l2-1))
    counts = np.zeros((l1-1, l2-1))
    targets = np.zeros((l1-1, l2-1))
    for i in range(l1-1):
        for j in range(l2-1):
            inds = plb.find((x1>=bin1[i]) & (x1<bin1[i+1]) & \
                (x2>=bin2[j]) & (x2<bin2[j+1]))
            if inds.shape[0] > 0:
                p = np.mean(y[inds])
                woes[i,j] = np.log(p/(1.0-p))
                counts[i,j] = int(inds.shape[0])
                targets[i,j] = int(np.sum(y[inds]))
            else:
                woes[i,j] = 0
                counts[i,j] = int(0)
                targets[i,j] = int(0)
    return woes, counts, targets

# compute woe
def bins2range(bins):
    '''
    Change
    [  -inf,   5.25,  13.  ,    inf,    nan]
    into
    ['[-inf, 5.25)', '[5.25, 13.00)', '[13.00, inf)', 'np.nan']
    '''
    xticks = []
    for i in xrange(len(bins)-2):
        xticks.append('[{:.2f}, {:.2f})'.format(bins[i], bins[i+1]))
        
    if np.isnan(bins[-1]):
        xticks.append('np.nan')
    else:
        xticks.append('[{:.2f}, {:.2f})'.format(bins[-2], bins[-1]))
        
    return xticks
        
def woe(x, y, bin=5, auto=True, toplot=True):
    if type(bin) != int:
        auto = False
    
    if auto:
        bins = np.zeros(bin+1)
        for i in range(bin+1):
            bins[i] = np.percentile(x, np.maximum(0, np.minimum(100, round(100.0/bin*i))))
    else:
        bins = np.array(bin)
        
    if type(bin) == int and np.unique(x).shape[0]<=10:
        temp = np.sort(np.unique(x))
        bin = temp.shape[0]
        bins = np.zeros(bin+1)
        bins[0:bin] = temp
        bins[-1] = temp[-1]+1

    bin = bins.shape[0]-1

    binx = np.zeros(bin)
    woes = np.zeros(bin)
    counts = np.zeros(bin)
    targets = np.zeros(bin)
    iv = np.zeros(bin)
    
    cnt_pos = sum(y)
    cnt_neg = len(y) - cnt_pos

    for i in range(bin):
        inds = (x >= bins[i]) & (x < bins[i+1])
        #p1 = np.mean(y[inds])+0.00000000000000001
        #woes[i] = np.log(p1/(1.0-p1))
        counts[i] = np.sum(inds)
        targets[i] = np.sum(y[inds])
        
        p1 = 1.0 * targets[i] / cnt_pos + 0.00000000000000001
        p2 = 1.0 * (counts[i] - targets[i]) / cnt_neg
        woes[i] = np.log(p1/p2)
        iv[i] = (p1 - p2) * woes[i]
        
        binx[i] = np.mean(x[inds])
        
    has_na = False
    if sum(pd.isnull(x)) > 0:
        # Add bin for NA
        counts = np.append(counts, [sum(pd.isnull(x))])
        targets = np.append(targets,
                            [sum((y_t for y_t, b_na in zip(y, pd.isnull(x)) if b_na))])
        p1 = 1.0 * targets[-1] / cnt_pos + 0.00000000000000001
        p2 = 1.0 * (counts[-1] - targets[-1]) / cnt_neg
        woes = np.append(woes, [np.log(p1/p2)])
        iv  = np.append(iv, [(p1 - p2) * woes[-1]])
        
        bins = np.append(bins, [np.nan])
        binx = np.append(binx, [np.nan])
        
        has_na = True
        
    if toplot:
        plt.bar(np.arange(1,len(binx)+1), counts)
        if has_na:
            plt.bar(len(binx), counts[-1], alpha=.8, color='g')
            
        plt.bar(np.arange(1,len(binx)+1), targets, color='r')
        ax2 = plt.twinx()
        plt.plot(np.arange(1,len(binx)+1)+0.5, woes, '.-k', linewidth=2, markersize=10)
        plt.xticks(np.arange(1, len(binx)+1)+0.5, bins2range(bins))
        for i, j in zip(np.arange(len(x))+1.5, woes):
            ax2.annotate(str(round(j, 2)), xy=(i, j), va="center", ha="left",
                         bbox=dict(boxstyle="round", fc="w"))

    return woes, bins, counts, targets, iv

def grouptest( data,factor,target,moderatiolow,moderatiohigh ):
    #print('begin testing')

    for f in factor:
        #print('Testing factor',f)
        # find the mode, special dealing 
        mode=data[f].mode()
        data_mode=data.ix[data[f]==mode[0]]
        print('Mode=',mode[0],'Mode count=',data_mode[target].count())
        moderatio=float(data_mode[target].count())/float(len(data))
        print('moderatio',format(moderatio,'5f'))
        if moderatio>moderatiohigh :
            print('Data Mode Error')
            print(f,'test is over\n')
            continue
        elif ( moderatio>moderatiolow) :
            ind10=data_mode[target].ix[data_mode[target]==1].count()
            ind00=data_mode[target].ix[data_mode[target]==0].count()
            print('Mode Default=',ind10,'Mode NonDefault=',ind00)
            drate0=float(ind10)/float(data_mode[target].count())
            print('Mode DefaultRate=',format(drate0,'5f'))
            data_nonmode=data.ix[data[f] != mode[0]]
            gt(data_nonmode,f,target)
        else:
            print('No special Mode')
            gt(data,f,target)


def gt(data,f,target):
        # grouptest nonmode data    
        x0=data[f].quantile(0.01)
        x1=data[f].quantile(0.2)
        x2=data[f].quantile(0.4)
        x3=data[f].quantile(0.6)
        x4=data[f].quantile(0.8)
        x5=data[f].quantile(.99)

##        x0=float(data[f].quantile(0))
##        x1=float(data[f].quantile(0.2))
##        x2=float(data[f].quantile(0.4))
##        x3=float(data[f].quantile(0.6))
##        x4=float(data[f].quantile(0.8))
##        x5=float(data[f].quantile(1.0))

        print('Five Group range',x0,x1,x2,x3,x4,x5)


        c1=data[target].ix[(data[f]>=x0)&(data[f]<=x1)].count()
        c2=data[target].ix[(data[f]>x1)&(data[f]<=x2)].count()
        c3=data[target].ix[(data[f]>x2)&(data[f]<=x3)].count()
        c4=data[target].ix[(data[f]>x3)&(data[f]<=x4)].count()
        c5=data[target].ix[(data[f]-x4>0)&(data[f]-x5<=0)].count()
        print('Five Group Count',c1,c2,c3,c4,c5)

        data_default=data.ix[data[target]==1]
        data_nondefault=data.ix[data[target]==0]
        ind11=data_default[target].ix[(data_default[f]>=x0)&(data_default[f]<=x1)].count()
        ind12=data_default[target].ix[(data_default[f]>x1)&(data_default[f]<=x2)].count()
        ind13=data_default[target].ix[(data_default[f]>x2)&(data_default[f]<=x3)].count()
        ind14=data_default[target].ix[(data_default[f]>x3)&(data_default[f]<=x4)].count()
        ind15=data_default[target].ix[(data_default[f]>x4)&(data_default[f]<=x5)].count()
        print('Five Group Default Count',ind11,ind12,ind13,ind14,ind15)
        try:
            drate1=float(ind11)/float(data[target].ix[(data[f]>=x0)&(data[f]<=x1)].count())
        except ZeroDivisionError:
            print('group1 error')
            drate1=-1
        try:
            drate2=float(ind12)/float(data[target].ix[(data[f]>x1)&(data[f]<=x2)].count())
        except ZeroDivisionError:
            print('group2 error')
            drate2=-1
        try:
            drate3=float(ind13)/float(data[target].ix[(data[f]>x2)&(data[f]<=x3)].count())
        except ZeroDivisionError:
            print('group3 error')
            drate3=-1
        try:
            drate4=float(ind14)/float(data[target].ix[(data[f]>x3)&(data[f]<=x4)].count())
        except ZeroDivisionError:
            print('group4 error')
            drate4=-1
        try:
            drate5=float(ind15)/float(data[target].ix[(data[f]>x4)&(data[f]<=x5)].count())
        except ZeroDivisionError:
            print('group5 error')
            drate5=-1

        print('Five Group DefaultRate',format(drate1,'5f'),format(drate2,'5f'),format(drate3,'5f'),format(drate4,'5f'),format(drate5,'5f'))
        #print(f,'test is over\n)
        plt.subplot(2,1,2)
        plt.bar(np.array([x0, x1, x2, x3, x4]), np.log(np.maximum(0, np.array([drate1, drate2, drate3, drate4, drate5]))))

        print('Five Group DefaultRate',format(drate1,'5f'),format(drate2,'5f'),format(drate3,'5f'),format(drate4,'5f'),format(drate5,'5f'))
        print(f,'test is over\n\n')
        return


def factordivide(data,f,point):
    l=len(data[f])
    v1=data[f].ix[data[f]>point]
    v2=data[f].ix[data[f]<point]
    v3=np.zeros(l)

    data['v1']=v1
    data['v2']=v2
    data['v3']=v3
    return data
        
# split data
# df -- dataframe
# split -- ratio to split out float (0, 1)
# seed -- random seed to use
def split_data(df, split, seed=1):
    random.seed(seed)
    rows = random.sample(df.index, int(round(split*(df.shape[0]))))
    df_split = df.ix[rows]
    df_remaining = df.drop(rows)
    return df_split, df_remaining, rows

def hump_variable(df, variable, split_pt):
    inds1 = df[variable] <= split_pt
    inds2 = df[variable] > split_pt
    df[variable+'_1'] = np.zeros(df.shape[0])
    df[variable+'_2'] = np.zeros(df.shape[0])
    df[variable+'_3'] = np.zeros(df.shape[0]) 
    df[variable+'_1'][inds1] = split_pt - df[variable][inds1]
    df[variable+'_2'][inds2] = df[variable][inds2] - split_pt
    df[variable+'_3'][inds1] = 1.0
    return df 

# Turn a categorical series to a few columns of dummy variables
# each unique value will be a separate column
# 
# s - a data series
def get_dummies_column(s):
    vc = s.value_counts()
    names = vc.index
    length = vc.values.shape[0]

    #print(names)
    column_name = s.name;
    row_num = s.shape[0]
    #print(row_num)

    data = np.zeros((row_num, length))

    column_names = ['']*(length)
    for i in xrange(length):
        column_names [i] = column_name + '_' + names[i]
        data[:, i] = (s == names[i]).astype(int)

    return pd.DataFrame(data, s.index, columns=column_names)

# Turn a list of categorical series to dummy series, append them,
def process_dummies(data, columns):
    df = data;
    for i in xrange(len(columns)):
        column = columns[i]
        df[column] = df[column].astype(str)
        dummy_series = get_dummies_column(df[column])
        df = pd.concat([df, dummy_series], axis=1)
    return df

# clean up, floor values to 2*p99 by default 
def treat_floor(df, names):
    for name in names:
        temp = df[name].quantile(0.99)
        if temp >= 0:
            df[name] = np.minimum(2.0 * temp, df[name])
        else:
            df[name] = np.minimum(0.5 * temp, df[name])
    return df

# clean up, ceiling values to p1*2 by default
def treat_ceiling(df, names):
    for name in names:
        temp = df[name].quantile(0.01)
        if temp > 0:
            df[name] = np.maximum(temp*0.5, df[name])
        else:
            df[name] = np.maximum(temp*2.0, df[name])
    return df

# Evaluate output of a logit
# Plot appropriate figures: KS/AUC, score distribution/average score
def evaluate_performance(all_target, predicted, toplot=True):
    fpr, tpr, thresholds = roc_curve(all_target, predicted)
    roc_auc = auc(fpr, tpr)
    ks = max(tpr-fpr)
    maxind = plb.find(tpr-fpr == ks)

    event_rate = sum(all_target) / 1.0 / all_target.shape[0]
    cum_total = tpr * event_rate + fpr * (1-event_rate)
    minind = plb.find(abs(cum_total - event_rate) == min(abs(cum_total - event_rate)))
    if minind.shape[0] > 0:
        minind = minind[0]

    print('KS=' + str(round(ks, 3)) + ', AUC=' + str(round(roc_auc,2)) +', N='+str(predicted.shape[0]))
    print('At threshold=' + str(round(event_rate, 3)) + ', TPR=' + str(round(tpr[minind],2)) + ', ' + str(int(round(tpr[minind]*event_rate*all_target.shape[0]))) + ' out of ' + str(int(round(event_rate*all_target.shape[0]))))
    print('At threshold=' + str(round(event_rate, 3)) + ', FPR=' + str(round(fpr[minind],2)) + ', ' + str(int(round(fpr[minind]*(1.0-event_rate)*all_target.shape[0]))) + ' out of ' + str(int(round((1.0-event_rate)*all_target.shape[0])))  )
    
    # Score average by percentile
    binnum = 10
    ave_predict = np.zeros((binnum))
    ave_target = np.zeros((binnum))
    indices = np.argsort(predicted)
    binsize = int(round(predicted.shape[0]/1.0/binnum))
    for i in range(binnum):
        startind = i*binsize
        endind = min(predicted.shape[0], (i+1)*binsize)
        ave_predict[i] = np.mean(predicted[indices[startind:endind]])
        ave_target[i] = np.mean(all_target[indices[startind:endind]])
    print('Ave_target: ' + str(ave_target))
    print('Ave_predicted: ' + str(ave_predict))
    
    if toplot:
        # KS plot
        plt.figure(figsize=(20,6))
        plt.subplot(1,3,1)
        plt.plot(fpr, tpr)
        #plt.hold
        plt.plot([0,1],[0,1], color='k', linestyle='--', linewidth=2)
        plt.title('KS='+str(round(ks,2))+ ' AUC='+str(round(roc_auc,2)), fontsize=20)
        plt.plot([fpr[maxind], fpr[maxind]], [fpr[maxind], tpr[maxind]], linewidth=4, color='r')
        plt.plot([fpr[minind]], [tpr[minind]], 'k.', markersize=10)

        plt.xlim([0,1])
        plt.ylim([0,1])
        plt.xlabel('False positive', fontsize=20); plt.ylabel('True positive', fontsize=20);
        
        #print('At threshold=' + str(round(event_rate, 3)))
        #print(str(round(fpr[minind],2)))
        #print(str(int(round(fpr[minind]*(1.0-event_rate)*all_target.shape[0]))))
        #print(str(int(round((1.0-event_rate)*all_target.shape[0]))) )
        
    
        # Score distribution score
        plt.subplot(1,3,2)
        #print(predicted.columns)
        plt.hist(predicted, bins=20)
        # plt.hold
        plt.axvline(x=np.mean(predicted), linestyle='--')
        plt.axvline(x=np.mean(all_target), linestyle='--', color='g')
        plt.title('N='+str(all_target.shape[0])+' Tru='+str(round(np.mean(all_target),3))+' Pred='+str(round(np.mean(predicted),3)), fontsize=20)
        plt.xlabel('Target rate', fontsize=20)
        plt.ylabel('Count', fontsize=20)
        
        plt.subplot(1,3,3)
        plt.plot(ave_predict, 'b.-', label='Prediction', markersize=5)
        #plt.hold
        plt.plot(ave_target, 'r.-', label='Truth', markersize=5)
        plt.legend(loc='lower right')
        plt.xlabel('Percentile', fontsize=20)
        plt.ylabel('Target rate', fontsize=20)

    return ks

# Get header row of a file
def get_header(fi):
    f = open(fi, 'r')
    g = csv.reader(f)
    head = g.next()
    head = [x.replace('\xef\xbb\xbf', '') for x in head]
    f.close()
    return head

# Get string for columns to keep to pass to awk
def get_column_string(header, columns, marker='$'):
    ss = marker + str(header.index(columns[0])+1)
    for i in range(1, len(columns)):
        ss = ss + ',' + marker + str(header.index(columns[i])+1)
    return ss

# get dataframe that correspond to a unique field
def get_data(g, currentrow, header, fieldtomatch, tomatch):
    if len(currentrow) == 0:
        return [], []
    index = header.index(fieldtomatch)
    if currentrow[index] > tomatch:
        return [], currentrow
    elif currentrow[index] < tomatch:
        while True:
            try:
                row = g.next()
                currentrow = row
                if row[index] > tomatch:
                    return [], currentrow
                elif row[index] == tomatch:
                    break
            except StopIteration:
                return [], []
    
    rows = [currentrow]
    while True:
        try:
            row = g.next()
            if row[index] == tomatch:
               rows.append(row)
            else:
                return pd.DataFrame(rows, columns=header), row
        except StopIteration:
            return pd.DataFrame(rows, columns=header), []

# save an object to a file
def save_object(obj, filename):
    with open(filename, 'wb') as output:
        cPickle.dump(obj, output, -1)

# locate bins for numeric variables
def bin_loc(value,uvbucket):
    if pd.isnull(value):
        # NA bins
        return (-np.inf, -np.inf)
    
    bins = np.empty(0)
    for i in range(len(uvbucket)-1):
       if value >= uvbucket[i] and value < uvbucket[i+1]:
           bins = (uvbucket[i],uvbucket[i+1])
           break
    
    return bins


def woe_calc(bad,good,goodfreq,badfreq):
    target_rt = float(bad)/float(badfreq)
    non_target_rt = float(good)/float(goodfreq)
    if float(bad) != 0.0 and float(bad)/(float(bad) + float(good)) != 1.0:
        woe = np.log(float(target_rt/non_target_rt))  
    elif target_rt == 0.0:
        woe = -99999999.0  
    elif float(bad)/(float(bad) + float(good)) == 1.0:
        woe = 99999999.0  
    return woe

def woe_calc_base(bad,good):
    try:
        woe = np.log(float(bad/float(bad+good))/float(good/float(bad+good))) 
    except:
        woe = -999999  
    return woe


# main function: get the reference table for numeric variables
def main_get_numeric_ref_table(df,var,tgt,max_bins):
    start_time = datetime.now()

    '''
    ------- Initialize: create the numeric bins -------#
    '''
    # create bucket
    if len(df[var].unique()) < max_bins:
        # NA would be the last bin if exists
        uvalue = np.sort(df[var].unique())
        uvdiff = np.append(np.diff(uvalue).astype(float)/2,0)
        uvbucket = np.append(np.nanmin(uvalue), uvalue + uvdiff)
    else:
        # uvalue = np.empty(0)
        # for i in np.arange(max_bins+1):
            # try:
                # uvalue = np.unique((np.append(uvalue, df[var].quantile(float(i)/float(max_bins)))))
            # except:
                # pass
        q = df.ix[~df[var].isnull(), [var]] \
                .quantile(1.*np.arange(max_bins+1)/max_bins) \
                .drop_duplicates()
                
        uvalue = list(q[var])
        uvdiff = np.append(np.diff(uvalue).astype(float)/2,0)
        uvbucket = np.append(np.nanmin(uvalue), uvalue + uvdiff)
        
        # Drop empty bucket
        b_bc = np.bincount(np.digitize(df[var].values, uvbucket))
        b_idx = np.where(b_bc == 0)
        uvbucket = np.delete(uvbucket, b_idx[0][1:])
        
        if df[var].isnull().sum() > 0:
            # Append nan bin
            uvbucket = np.append(uvbucket, np.nan)

    uvbucket[0] = -np.inf
    if np.isnan(uvbucket[-1]):
        uvbucket[-2] = np.inf
    else:
        uvbucket[-1] = np.inf

    df[var+'_bin'] = df[var].apply(lambda x: bin_loc(x,uvbucket))
    
    col_t = [c for c in df.columns if c != var and c != tgt][0]
    ds = df[[var+'_bin', tgt, col_t]].groupby([var+'_bin',tgt]).count().unstack().fillna(value=0)
    #ds = df[[var+'_bin',tgt]].groupby([var+'_bin',tgt]).count().unstack()[var+'_bin'].fillna(value=0) 
    #ds['pop'] = ds[1] + ds[0]
    ds['bin'] = [[str(i[0]),str(i[1])] for i in list(ds.index)]
    ds = ds.reset_index(drop = True)
    chisq = []
    for i in range(ds.shape[0]-1):
        chisq.append(cy.chi2_contingency(ds.iloc[[i,i+1]][[0,1]])[0])
    chisq.append(9999999.0)
    ds['chisq'] = chisq
    ds.columns =ds.columns.swaplevel(0, 1).droplevel()
    ds.columns=[0,1,'bin','chisq']
    
    '''
    #------- chimerge: merge the adjacent bins, except bin for NA (bin as ['-inf', '-inf']) -------#
    '''
    start_time = datetime.now()
    inds_na = ds['bin'].apply(lambda b: b == ['-inf', '-inf'])
    while (ds.shape[0] > 5) or (ds.shape[0] >  2 and ds.ix[~inds_na, 'chisq'].min() <= scipy.stats.chi2.ppf(0.95, 1)):
        start_time = datetime.now()
        # calculate chisquare statistic
        chisq = []
        for i in range(ds.shape[0]-1):
            chisq.append(cy.chi2_contingency(ds.irow([i,i+1])[[0,1]])[0])  
        chisq.append(9999999.0)   
        ds['chisq'] = chisq
        
        # locate the smallest chisq stat bin by index
        #k = np.where(ds.chisq == ds.chisq.min())[0][0] ]
        ds_idx_list = list(ds.index)
        k = ds_idx_list.index(ds[ds['chisq'] == ds.ix[~inds_na, 'chisq'].min()].index[0])

        #print(ds.ix[ds_idx_list[k:k+2]],ds.shape[0],k)
        # merge the adjacent bins, drop the second bin
        ds.ix[ds_idx_list[k],0:2] = ds.ix[ds_idx_list[k],0:2] + ds.ix[ds_idx_list[k+1],0:2]
        ds['bin'].ix[ds_idx_list[k]] = [ds['bin'].ix[ds_idx_list[k]][0],ds['bin'].ix[ds_idx_list[k+1]][1]]
        ds = ds.drop(ds_idx_list[k+1],axis=0)
        ds=ds.reset_index(drop = True)
        #print(ds.ix[ds_idx_list[k:k+2]],ds.shape[0],k)
        ds_idx_list = list(ds.index)
        if k != 0:
            ds['chisq'].ix[ds_idx_list[k-1]] = cy.chi2_contingency(ds.ix[ds_idx_list[k-1:k+1],0:2])[0]
        if k < ds.shape[0] - 1:
            ds['chisq'].ix[ds_idx_list[k]] = cy.chi2_contingency(ds.ix[ds_idx_list[k:k+2],0:2])[0]
        else:
            ds['chisq'].ix[ds_idx_list[k]] = 9999999.0
        
        inds_na = ds['bin'].apply(lambda b: b == ['-inf', '-inf'])
        end_time = datetime.now()
        #print('  Duration of merge bins for each iteration: {}'.format(end_time - start_time)) 
        #if ds.chisq.min() > scipy.stats.chi2.ppf(0.95, 1):
        #    break      
    end_time = datetime.now()
    

    print("\n  #--------------- 3. Merge bins by chisq rules Done --------------#")
    print('  Duration of merge bins by chisq rules: {}'.format(end_time - start_time))  
    print("  shape of the reduced table: {}".format(ds.shape)) 


    '''
    #-------- chimerge: control bin size, except bin for NA (bin as ['-inf', '-inf']) -------#
    '''
    inds_na = ds['bin'].apply(lambda b: b == ['-inf', '-inf'])
    ds_na = ds[inds_na]
    
    ds = ds[~inds_na]
    pop_cut = df.shape[0] / 20
    ds['pop'] = ds[0] + ds[1]
    
    while ds['pop'].min() < pop_cut and ds.shape[0] > 2:
        # calculate chisquare statistic
        chisq = []
        for i in range(ds.shape[0]-1):
            chisq.append(cy.chi2_contingency(ds.irow([i,i+1])[[0,1]])[0])  
        chisq.append(9999999.0)   
        ds['chisq'] = chisq 

        # locate the smallest size by index
        ds_idx_list = list(ds.index)
        k = ds_idx_list.index(ds[ds['pop'] == ds['pop'].min()].index[0])
        if k == len(ds_idx_list) - 1 :
            k -= 1      
        elif ds['chisq'].ix[ds_idx_list[k]] > ds['chisq'].ix[ds_idx_list[k-1]]:
            k -= 1

        # merge the adjacent binsssss, drop the second bin   
        ds.ix[ds_idx_list[k],0:2] = ds.ix[ds_idx_list[k],0:2] + ds.ix[ds_idx_list[k+1],0:2]
        ds['bin'].ix[ds_idx_list[k]] = [ds['bin'].ix[ds_idx_list[k]][0],ds['bin'].ix[ds_idx_list[k+1]][1]]      
        ds = ds.drop(ds_idx_list[k+1],axis=0)
        ds['pop'] = ds[0] + ds[1]
        
    # Add NaN bin back
    ds = pd.concat([ds, ds_na])
    ds['pop'] = ds[0] + ds[1]
    ds['dft_rto'] = 1.0 * ds[1] / ds['pop']

    print("\n  #--------------- 4. Done: merge bins by bin size --------------#")  
    print("  shape of the reduced table: {}".format(ds.shape))


    '''
    #------- get the reference table -------#
    '''
    ds = ds.reset_index(drop=True)

    ds['ref_table'] = None
    goodfreq = ds[0].sum()  
    badfreq = ds[1].sum()
    ds[var+'_nwoe'] = ds.apply(lambda x: woe_calc(x[1],x[0],goodfreq,badfreq), axis=1)
    ds['ref_table'] = ds['bin'].apply(lambda x: x[0] + '_' + x[1])

    # IVs
    ds[var + '_IVs'] = ds.apply(lambda x: x[var+'_nwoe'] * (float(x[1])/badfreq - float(x[0])/goodfreq), axis=1)
    
    # Set order of columns
    ds = ds.reindex_axis([0, 1, 'bin', 'dft_rto', 'chisq', 'pop', 'ref_table', var+'_nwoe', var+'_IVs'], axis=1)

    ref_table = {}
    ref_table = dict(zip(ds['ref_table'],ds[var +'_nwoe']))   
    ref_table['base'] = woe_calc_base(ds[1].sum(),ds[0].sum())
    end_time = datetime.now()
    
    print("\n  #--------------- get the reference table --------------#") 
    print('  Duration of getting the reference table: {}'.format(end_time - start_time)) 

    # IV
    # ref_table['IVs'] = ds[var + '_IVs']
    ref_table['IV'] = sum(ds[var + '_IVs'])

    return ref_table, ds[var + '_IVs'], ds

# reference table from bins
def main_get_numeric_ref_table_fr_bins(df, var, tgt, bins):
    start_time = datetime.now()
    uvbucket = bins
    if df[var].isnull().sum() > 0 and np.nan not in uvbucket:
            # Append nan bin
            uvbucket = np.append(uvbucket, np.nan)
    uvbucket[0] = -np.inf
    if np.isnan(uvbucket[-1]):
        uvbucket[-2] = np.inf
    else:
        uvbucket[-1] = np.inf

    df[var+'_bin'] = df[var].apply(lambda x: bin_loc(x, uvbucket))
    
    col_t = [c for c in df.columns if c != var and c != tgt][0]
    ds = df[[var+'_bin', tgt, col_t]].groupby([var+'_bin',tgt]).count().unstack().fillna(value=0)
    #ds = df[[var+'_bin',tgt]].groupby([var+'_bin',tgt]).count().unstack()[var+'_bin'].fillna(value=0) 
    #ds['pop'] = ds[1] + ds[0]
    ds['bin'] = [[str(i[0]),str(i[1])] for i in list(ds.index)]
    ds = ds.reset_index(drop = True)
    chisq = []
    for i in range(ds.shape[0]-1):
        chisq.append(cy.chi2_contingency(ds.iloc[[i,i+1]][[0,1]])[0])
    chisq.append(9999999.0)   
    ds['chisq'] = chisq
    ds.columns =ds.columns.swaplevel(0, 1).droplevel()
    ds.columns=[0, 1, 'bin', 'chisq']
    
    # Add necessary columns
    ds['pop'] = ds[0] + ds[1]
    ds['dft_rto'] = 1.0 * ds[1] / ds['pop']
    ds['ref_table'] = ds['bin'].apply(lambda x: x[0] + '_' + x[1])
    
    goodfreq = ds[0].sum()  
    badfreq = ds[1].sum()
    ds[var+'_nwoe'] = ds.apply(lambda x: woe_calc(x[1],x[0],goodfreq,badfreq), axis=1)
    
    # IVs
    ds[var+'_IVs'] = ds.apply(lambda x: x[var+'_nwoe'] * (float(x[1])/badfreq - float(x[0])/goodfreq), axis=1)
    
    # Set order of columns
    ds = ds.reindex_axis([0, 1, 'bin', 'dft_rto', 'chisq', 'pop', 'ref_table', var+'_nwoe', var+'_IVs'], axis=1)
    
    # Reference table
    ref_table = {}
    ref_table = dict(zip(ds['ref_table'],ds[var +'_nwoe']))
    ref_table['base'] = woe_calc_base(ds[1].sum(),ds[0].sum())
    ref_table['IV'] = sum(ds[var + '_IVs'])
    
    return ref_table, ds[var + '_IVs'], ds

# Update WOE reference table
def update_numeric_woe_info(ref_table, var, b_stat,
                            ref_table_f, b_stat_f, df_iv_f):
    # Update WOE reference table
    df_numeric_ref_table = pd.read_csv(ref_table_f)
    df_numeric_ref_table.drop(df_numeric_ref_table.loc[df_numeric_ref_table['Var_Name'] == var].index,
                              inplace=True)

    df_ref_table_tmp = pd.DataFrame(ref_table.items(), columns=['Var_Value', 'Ref_Value'])
    df_ref_table_tmp['Var_Name'] = var
    df_numeric_ref_table = pd.concat((df_numeric_ref_table, df_ref_table_tmp), axis=0)

    df_numeric_ref_table.to_csv(ref_table_f, index=False)
    
    def get_bin_range(ref_table, var=None):
        '''
        Get bin range from reference table.
        
        Var_Value  Ref_Value     Var_Name
        -inf_0.5   0.179195  count_phone
         1.5_inf  -0.096664  count_phone
         0.5_1.5   0.049708  count_phone
            base  -3.933759  count_phone
              IV   0.012190  count_phone

        >>> get_bin_range(df_numeric_ref_table, 'count_phone')
        [-inf, 0.5, 1.5, inf]
        '''
        if var is None:
            # ref_table has only one variable, and no Var_Name
            vv = ref_table['Var_Value']
        else:
            vv = ref_table.ix[ref_table['Var_Name'] == var, 'Var_Value']
        
        b_lst = []
        for v in vv:
            if 'base' == v or 'iv' == v.lower():
                continue
            t_lst = v.split('_')
            b_lst.extend([float(b) for b in t_lst])
        
        b_lst = sorted(list(set(b_lst)))
        b_lst[-1] += .1
        return b_lst

    # Bin stats
    with open(b_stat_f, 'a') as bf:
        # TODO
        b_stat.to_csv(bf, sep='~', index=False, encoding='utf8')
        bf.write(str(get_bin_range(df_numeric_ref_table, var)))
        bf.write('\n')

    # IV
    df_iv = pd.read_csv(df_iv_f, encoding='utf8')
    df_iv.ix[df_iv['var'] == var, 'iv'] = ref_table['IV']
    df_iv.to_csv(df_iv_f, index=False, encoding='utf8')

#cvlookup function
def cvlookup(table,key):
    if table.has_key(key):
        if table[key] == '-99999999.0' :
            value = table['base']
        else:    
            value = table[key]
    else:
        value = table['base']    
    return value


#nvlookup function
def nvlookup(table,value):
    # keylist = table.keys()
    # keylist.sort()
    # keymaxrange = keylist[-2]
    # keyminrange = keylist[0]
    # keymax = keylist[-2].split('_')
    # keymin = keylist[0].split('_')
    
    ref = None
    for key in table.keys():
        if key.lower() == 'base' or key.lower() == 'iv':
            continue
            
        krange = map(np.float, key.split('_'))
        if pd.isnull(value) and krange[1] == -np.inf:
            ref = table[key]
            break
            
        if value >=  krange[0] and value < krange[1]:
            if table[key] == '-99999999.0':
                ref = table['base']
            else:
                ref = table[key]
            break
        # elif value > keymax[1]:
            # ref = table[keymaxrange]
        # elif value < keymin[1]):
            # ref = table[keyminrange]
                
    return ref


def calc_nominal_woe(df, var, tgt):
    '''
    Calculate woe for nominal variable.
    
    Return: ref_table, IV, binned_df
    '''
    # 
    if df[var].count() == 0:
        return None, None, None
        
    # Make NA as a bin
    vval_na = 'NA'
    i = 0
    while vval_na in df[var].values:
        vval_na = 'NA_{:02d}'.format(i)
        i += 1
        
    df.fillna({var: vval_na}, inplace=True)
    
    # ds = df[[var, tgt, 'userid']].groupby([var, tgt]).count().unstack().fillna(value=0)
    col_t = [c for c in df.columns if c != var and c != tgt][0]
    ds = df[[var, tgt, col_t]].groupby([var, tgt]).count().unstack().fillna(value=0)
    ds.columns = ds.columns.droplevel(0)
    ds.reset_index(inplace=True)
    
    # Change to list
    ds[var] = ds[var].apply(lambda v: [v])
    
    # Merge small bins first
    is_small = ((ds[0] + ds[1]) / df.shape[0]) < 0.02
    while sum(is_small) > 0:
        small_sum = ds.loc[is_small].sum()
        ds.drop(ds[is_small].index, inplace=True)
        ds = ds.append(pd.DataFrame(small_sum).transpose(), ignore_index=True)
        
        # Population ratio after sum
        pop_rto = ((ds[0] + ds[1]) / df.shape[0])
        is_small = pop_rto < 0.02
        if sum(is_small) == 1:
            # To merge into 2nd least bin when merged bin is still too small
            is_small[pop_rto[:-1].argmin()] = True
    
    # dft_rto = df[[var, tgt]].groupby(var).mean().rename(columns={tgt: 'dft_rto'}).reset_index()
    # ds = ds.merge(dft_rto, on=var).sort_values('dft_rto').reset_index(drop=True)
    ds['dft_rto'] = ds[1] / ds[[0, 1]].sum(axis=1)
    ds = ds.sort_values('dft_rto').reset_index(drop=True)
    
    # Replace NA back
    try:
        df.replace({var: {vval_na: np.nan}}, inplace=True)
    except TypeError:
        # TypeError: Cannot compare types 'ndarray(dtype=float64)' and 'str'
        # Only float in this column
        pass

    # Calc initial chisquare statistic
    chisq = []
    for i in range(ds.shape[0]-1):
        chisq.append(cy.chi2_contingency(ds.iloc[[i,i+1]][[0,1]])[0])  
    chisq.append(9999999.0)
    ds['chisq'] = chisq

    '''
    #------- chimerge: merge the adjacent bins -------#
    '''
    # min_bin = max(np.ceil(1.0 * ds.shape[0] / 3), 5)
    # while (ds.shape[0] > min_bin) and (ds.chisq.min() <= scipy.stats.chi2.ppf(0.95, 1)):
    while (ds.shape[0] > 5) or (ds.shape[0] >  2 and ds.chisq.min() <= scipy.stats.chi2.ppf(0.95, 1)):
        # locate the smallest chisq stat bin by index
        ds_idx_list = list(ds.index)
        k = ds_idx_list.index(ds[ds.chisq == ds.chisq.min()].index[0])

        # merge the adjacent bins, drop the second bin
        ds.ix[ds_idx_list[k], [var, 0, 1]] = ds.ix[[ds_idx_list[k], ds_idx_list[k+1]], [var, 0, 1]].sum()
        ds.ix[ds_idx_list[k], 'dft_rto'] = 1.0 * ds.ix[ds_idx_list[k], 1] / (ds.ix[ds_idx_list[k], 0] + ds.ix[ds_idx_list[k], 1])

        ds = ds.drop(ds_idx_list[k+1], axis=0)
        ds=ds.reset_index(drop=True)
        if k != 0:
            ds.ix[ds_idx_list[k-1], 'chisq'] = cy.chi2_contingency(ds.iloc[ds_idx_list[k-1:k+1]][[0, 1]])[0]

        if k < ds.shape[0] - 1:
            ds.ix[ds_idx_list[k], 'chisq'] = cy.chi2_contingency(ds.iloc[ds_idx_list[k:k+2]][[0, 1]])[0]
        else:
            ds.ix[ds_idx_list[k], 'chisq'] = 9999999.0


    '''
    #-------- chimerge: control bin size -------#
    '''
    pop_cut = float(ds[0].sum() + ds[1].sum())/20
    ds['pop'] = ds[0] + ds[1]

    # print(pop_cut)
    while (ds.shape[0] > 2
           and (ds['pop'].min() < pop_cut 
           or ds.chisq.min() <= scipy.stats.chi2.ppf(0.99, 1))) or ds[1].min() <= 0:
        # calculate chisquare statistic
        chisq = []
        for i in range(ds.shape[0]-1):
            chisq.append(cy.chi2_contingency(ds.iloc[[i,i+1]][[0,1]])[0])
        chisq.append(9999999.0)
        ds['chisq'] = chisq 

        # locate the smallest size by index
        ds_idx_list = list(ds.index)
        k = ds_idx_list.index(ds[ds['pop'] == ds['pop'].min()].index[0])
        if k == len(ds_idx_list) - 1:
            k -= 1      
        elif ds.ix[ds_idx_list[k], 'chisq'] > ds.ix[ds_idx_list[k-1], 'chisq']:
            k -= 1

        # merge the adjacent bins, drop the second bin    
        ds.ix[ds_idx_list[k], [var, 0, 1, 'pop']] = ds.ix[[ds_idx_list[k], ds_idx_list[k+1]], [var, 0, 1, 'pop']].sum()
        ds.ix[ds_idx_list[k], 'dft_rto'] = 1.0 * ds.ix[ds_idx_list[k], 1] / (ds.ix[ds_idx_list[k], 0] + ds.ix[ds_idx_list[k], 1])
        ds = ds.drop(ds_idx_list[k+1], axis=0)
        ds = ds.reset_index(drop=True)

    '''
    #------- Calculate woe & IV -------#
    '''
    goodfreq = ds[0].sum()
    badfreq = ds[1].sum()
    ds[var+'_cwoe'] = ds.apply(lambda x: woe_calc(x[1], x[0], goodfreq, badfreq), axis=1)

    # IVs
    ds[var+'_IVs'] = ds.apply(lambda x: x[var+'_cwoe'] * (float(x[1])/badfreq - float(x[0])/goodfreq), axis=1)
    IV = ds[var+'_IVs']
    
    # Set stats of other's bin the same as that of the bin where least value locates
    # For data has not appeared
    vval_min = df[var].value_counts().argmin()
    ds = pd.concat([ds, ds.loc[ds[var].apply(lambda v_lst: vval_min in v_lst)]], ignore_index=True)
    ds.ix[ds.tail(1).index, var] = 'other'
    
    # Set var column (1st) to the last (to be readable)
    ds = ds.reindex_axis(list(ds.columns[1:])+[ds.columns[0]], axis=1)

    '''
    #------- get the reference table -------#
    '''
    def is_in_bin(v_lst, v_val, vval_na):
        if 'other' == v_lst:
            return False
        if pd.isnull(v_val):
            return vval_na in v_lst
        else:
            return v_val in v_lst
    
    # ref_table = pd.DataFrame({'var_name': len(df[var].unique())})
    uniq_val = df[var].unique()
    ref_dict = {}
    for v_val in uniq_val:
        ref_dict[v_val] = ds.ix[ds[var].apply(lambda v_lst: is_in_bin(v_lst, v_val, vval_na)), var+'_cwoe'].values[0]

    ref_dict['other'] = ds.ix[ds[var] == 'other', var+"_cwoe"].values[0]

    ref_table = pd.DataFrame.from_dict(ref_dict, orient='index')
    ref_table = ref_table.reset_index().rename(columns={'index': 'var_value', 0: 'woe'})
    ref_table['var_name'] = var
    ref_table = ref_table.reindex_axis(['var_name', 'var_value', 'woe'], axis=1)

    return ref_table, IV, ds


def set_nominal_woe(df, ref_table):
    for v in ref_table['var_name'].unique():
        ref_tbl_v = ref_table.loc[ref_table['var_name'] == v]
        try:
            df[v]
        except KeyError:
            # log.info("No column \"{}\" found".format(v))
            try:
                print("No column \"{}\" found".format(v))
            except UnicodeEncodeError:
                print(u"No column \"{}\" found".format(v))
            continue

        df[v+'_cwoe'] = ref_tbl_v.ix[ref_tbl_v['var_value'] == 'other', 'woe'].values[0]
        for vval in ref_tbl_v['var_value']:
            if 'other' == vval:
                continue
            
            if pd.isnull(vval):
                inds = pd.isnull(df[v])
                df.ix[inds, v+'_cwoe'] = ref_tbl_v.ix[pd.isnull(ref_tbl_v['var_value']), 'woe'].values[0]
            else:
                try:
                    # It's float value
                    inds = df[v] == float(vval)
                except (ValueError, UnicodeEncodeError):
                    # It's string
                    col_v = df[v].apply(lambda r: r.decode('utf8') if isinstance(r, str) else r if isinstance(r, unicode) else str(r).decode('utf8'))
                    inds = col_v == vval
                    
                df.ix[inds, v+'_cwoe'] = ref_tbl_v.ix[ref_tbl_v['var_value'] == vval, 'woe'].values[0]


# ## Update nominal woe needed
def calc_nominal_bin_stats_fr_reftable(df, ref_table, tgt):
    # t0 = time.clock()
    var = ref_table.ix[0, 'var_name']
    tmp = pd.merge(df, ref_table[['woe', 'var_value']], how='left', left_on=var, right_on='var_value')
    tmp.ix[tmp[var].isnull(), 'woe'] = ref_table.ix[ref_table['var_value'].isnull(), 'woe'].values
    ds = tmp[['woe', tgt, var]].groupby(['woe', tgt]).agg(len).unstack().fillna(value=0)
    # t1 = time.clock()
    # print("{0}: {1}s elapsed".format(var, t1-t0))

    ds.columns = ds.columns.droplevel(0)
    ds.reset_index(inplace=True)

    dft_rto = tmp[['woe', tgt]].groupby('woe').mean().rename(columns={tgt: 'dft_rto'}).reset_index()
    ds = ds.merge(dft_rto, on='woe').sort_values('dft_rto').reset_index(drop=True)

    ds['chisq'] = np.nan
    ds['pop'] = ds[[0, 1]].sum(axis=1)

    # Add values of variable
    ds = ds.merge(pd.DataFrame(ref_table.groupby('woe')['var_value'].agg(lambda x: list(x))).rename(columns={0: var}), left_on='woe', right_index=True)

    # Update and rename woe
    goodfreq = ds[0].sum()
    badfreq = ds[1].sum()
    ds['woe'] = ds[[0, 1]].apply(lambda tgt: woe_calc(tgt[1], tgt[0], goodfreq, badfreq), axis=1)
    ds.rename(columns={'woe': var+'_cwoe'}, inplace=True)
    
    # IV
    ds[var+'_IVs'] = ds.apply(lambda x: x[var+'_cwoe'] * (float(x[1])/badfreq - float(x[0])/goodfreq), axis=1)
    
    # For data has not appeared
    vval_min = df[var].value_counts().argmin()
    ds = pd.concat([ds, ds.loc[ds[var].apply(lambda v_lst: vval_min in v_lst)]], ignore_index=True)
    ds.ix[ds.tail(1).index, var] = 'other'
    
    # Re-order columns
    ds = ds.reindex_axis(list(ds.columns[1:6])+[var+'_cwoe', var+'_IVs', var], axis=1)
    
    return ds


# def set_nominal_woe_by_dict(df, ref_dict):
    # ref_table = pd.DataFrame()
    # for k, v in ref_dict.iteritems():
        # df_t = pd.DataFrame.from_dict({k: v}).reset_index().groupby('index')[k].apply(lambda x: pd.DataFrame(x.values[0])).reset_index(level=0).rename(columns={'index': 'woe', 0: 'var_value'})
        # df_t['var_name'] = k
        # ref_table = pd.concat([ref_table, df_t], axis=0)
        
    # set_nominal_woe(df, ref_table)
    # return ref_table
def calc_nominal_fr_dict_bin(df, ref_dict, tgt):
    '''
    var = 'studyLevel'
    ref_dict = {'studyLevel': {0: [np.nan],
                               1: ["本科", "专升本", "博士", "硕士", "硕士研究生"],
                               2: ["专科(高职)", "专科（高职）", "专科"]}}

    ref_table, IV, ds = dc.calc_nominal_fr_dict_bin(x_train, ref_dict, target)
    dc.set_nominal_woe(x_train, ref_table)
    dc.set_nominal_woe(x_test, ref_table)
    dc.update_nominal_woe_info(ref_table, var, b_stat,
                               ref_table_cvar_f, b_stat_cvar_f, iv_cvar_f)
    '''
    k = ref_dict.keys()[0]
    v = ref_dict.values()[0]
    ref_table = pd.DataFrame.from_dict({k: v}).reset_index().groupby('index')[k].apply(lambda x: pd.DataFrame(x.values[0])).reset_index().drop(['level_1'], axis=1).rename(columns={'index': 'woe', 0: 'var_value'})
    ref_table['var_name'] = k
    
    t0 = datetime.now()
    ds = calc_nominal_bin_stats_fr_reftable(df, ref_table, tgt)
    print("{0}: {1}s elapsed".format(k, datetime.now()-t0))
    IV = ds.ix[ds[k]!='other', k+'_IVs']
    
    # ### Update reference table
    def is_in_bin(v_lst, v_val, vval_na):
        if 'other' == v_lst:
            return False
        if pd.isnull(v_val):
            return vval_na in v_lst
        else:
            return v_val in v_lst
            
    var = k
    uniq_val = df[var].unique()
    ref_dict2 = {}
    for v_val in uniq_val:
        ref_dict2[v_val] = ds.ix[ds[var].apply(lambda v_lst: is_in_bin(v_lst, v_val, vval_na=np.nan)), var+'_cwoe'].values[0]
        
    ref_dict2['other'] = ds.ix[ds[var] == 'other', var+"_cwoe"].values[0]
    
    ref_table = pd.DataFrame.from_dict(ref_dict2, orient='index')
    ref_table = ref_table.reset_index().rename(columns={'index': 'var_value', 0: 'woe'})
    ref_table['var_name'] = var
    ref_table = ref_table.reindex_axis(['var_name', 'var_value', 'woe'], axis=1)
    
    # set_nominal_woe(df, ref_table)
    return ref_table, IV, ds


# Update WOE reference table
def update_nominal_woe_info(ref_table, var, b_stat,
                            ref_table_f, b_stat_f, df_iv_f):
    # Update WOE reference table
    nominal_ref_table = pd.read_csv(ref_table_f)
    nominal_ref_table.drop(nominal_ref_table.loc[nominal_ref_table['var_name'] == var].index,
                           inplace=True)

    nominal_ref_table = pd.concat((nominal_ref_table, ref_table), axis=0)

    nominal_ref_table.to_csv(ref_table_f, index=False)
    
    # Bin stats
    with open(b_stat_f, 'aw') as bf:
        # TODO
        b_stat.to_csv(bf, sep='~', index=False, encoding='utf8')
        bf.write('\n')

    # IV
    df_iv = pd.read_csv(df_iv_f, encoding='utf8')
    df_iv.ix[df_iv['var'] == var, 'iv'] = b_stat.ix[b_stat[var]!='other', var+'_IVs'].sum()
    df_iv.to_csv(df_iv_f, index=False)


def main_apply_ref_table(datain,ref_table,var):
    datain['cwoe_' + var] = datain[var].apply(lambda x: cvlookup(ref_table,str(x)))
    return datain


def main_apply_numeric_ref_table(datain,ref_table,var):
    datain[var+'_nwoe'] = datain[var].apply(lambda x: nvlookup(ref_table,x))
    return datain


class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyJSONEncoder, self).default(obj)
            
            
''' ID number '''
def get_id_age(id_s, ref_date=None):
    if ref_date is None:
        ref_date = datetime.now()
    
    age_birthdate = pd.to_datetime(id_s.apply(lambda i: str(i)[6:14]), errors='coerce')
    age = pd.Series(len(age_birthdate)*[np.nan], index=age_birthdate.index)
    age.loc[~pd.isnull(age_birthdate)] = age_birthdate.loc[~pd.isnull(age_birthdate)].apply(lambda bd: dateutil.relativedelta.relativedelta(ref_date, bd).years)
    return age
    
    
def gender_fr_id(id_no):
    try:
        gender = int(id_no[-2]) % 2
        if gender == 0:
            gender = 2
    except ValueError:
        gender = 0
    
    return gender
    
    
def get_id_gender(id_s):
    return id_s.apply(gender_fr_id)
