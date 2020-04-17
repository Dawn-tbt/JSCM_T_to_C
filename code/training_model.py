# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:28:54 2020

@author: admin
"""

import itertools as it
import pandas as pd
import numpy as np
import datetime as t

class N_Gram:
    def __init__(self):
        self.alignments = {'align_list':[],'bi_probability':[],'uni_probability':[]} 
        self.bi_gram = {'bi_gram':[],'probability':[],'count':[]}
        self.uni_gram = {'uni_gram':[],'probability':[]}
        self.right_bi = []
        self.right_u = []
        self.loop = 0
    
    def load_data(self,file_path):
        file = pd.read_excel(file_path)
        ct_name = [list(file['中文名']),list(file['藏文名'])]
        return ct_name
    
    def data_seting(self,c_name_list,t_name_list):
        for i in range(len(c_name_list)):
            c_name = [c for c in c_name_list[i].strip()]
            t_name = t_name_list[i].strip().split('་')
            self.creat_align_unit(c_name,t_name)
        bi_gram,uni_gram = set(),set()
        temp_list = []
        for j in self.alignments['align_list']:
            temp_list.extend(j['bi_gram'])
            bi_gram.update(j['bi_gram'])
            uni_gram.update(j['uni_gram'])
        self.bi_gram['bi_gram'].extend(list(bi_gram))
        self.uni_gram['uni_gram'].extend(list(uni_gram))
        self.bi_gram['probability'].extend([1]*len(self.bi_gram['bi_gram']))
        self.uni_gram['probability'].extend([1]*len(self.uni_gram['uni_gram']))
        for x in self.bi_gram['bi_gram']:
            self.bi_gram['count'].append(temp_list.count(x))
        print("data_setting func is finish!")
    
    def creat_align_unit(self,c_name,t_name):
        align_data = {'raw_name':'་'.join(t_name)+'/'+''.join(c_name),'uni_gram':[],'bi_gram':[]}
        temp_list = []
        if len(c_name) == len(t_name):
            for i in range(len(c_name)):
                align_data['uni_gram'].append(t_name[i] + '-' + c_name[i])
            temp_list.extend(list(map(lambda a,b:a+'/'+b,['BOS']+align_data['uni_gram'],\
                            align_data['uni_gram']+['EOS'])))
            align_data['bi_gram'].extend(temp_list)
            self.alignments['align_list'].append(align_data.copy())
            self.alignments['bi_probability'].append(1)
            self.alignments['uni_probability'].append(1)
        elif len(t_name) < len(c_name):
            index_list = list(it.combinations(list(range(1,len(c_name))),len(t_name)-1))
            for i in range(len(index_list)):
                t=0
                index_list[i] = list(index_list[i]) + [None]
                for j in range(len(t_name)):
                    if t == 0:
                        align_data['uni_gram'].append(t_name[j]+'-'+(''.join(c_name[:index_list[i][j]])))
                    else:
                        align_data['uni_gram'].append(t_name[j]+'-'+(''.join(c_name[index_list[i][j-1]:index_list[i][j]])))
                    t += 1
                temp_list.extend(list(map(lambda a,b:a+'/'+b,['BOS']+align_data['uni_gram'],\
                                 align_data['uni_gram']+['EOS'])))
                align_data['bi_gram'].extend(temp_list)
                self.alignments['align_list'].append(align_data.copy())
                self.alignments['bi_probability'].append(1)
                self.alignments['uni_probability'].append(1)
                temp_list.clear()
                align_data['uni_gram'] = []
                align_data['bi_gram'] = []
        else:
            index_list = list(it.combinations(list(range(1,len(t_name))),len(c_name)-1))
            for i in range(len(index_list)):
                t=0
                index_list[i] = list(index_list[i]) + [None]
                for j in range(len(c_name)):
                    if t == 0:
                        align_data['uni_gram'].append((''.join(t_name[:index_list[i][j]]))+'-'+c_name[j])
                    else:
                        align_data['uni_gram'].append((''.join(t_name[index_list[i][j-1]:index_list[i][j]]))+'-'+c_name[j])
                    t += 1
                temp_list.extend(list(map(lambda a,b:a+'/'+b,['BOS']+align_data['uni_gram'],\
                                 align_data['uni_gram']+['EOS'])))
                align_data['bi_gram'].extend(temp_list)
                self.alignments['align_list'].append(align_data.copy())
                self.alignments['bi_probability'].append(1)
                self.alignments['uni_probability'].append(1)
                temp_list.clear()
                align_data['uni_gram'] = []
                align_data['bi_gram'] = []

    def initial_bi_parameters(self):
        for i in range(len(self.bi_gram['bi_gram'])):
            temp_var1 = self.bi_gram['bi_gram'][i].split('/')[0]
            n = 0
            for j in self.bi_gram['bi_gram']:
                if j.startswith(temp_var1+'/'):
                    n += 1
            self.bi_gram['probability'][i] = 1.0 / n
        for x in range(len(self.alignments['align_list'])):
            temp_var2 = self.alignments['align_list'][x]
            for y in temp_var2['bi_gram']:
                self.alignments['bi_probability'][x] *= self.bi_gram['probability'][self.bi_gram['bi_gram'].index(y)]
        for h in range(len(self.alignments['align_list'])):
            temp_var3 = self.alignments['align_list'][h]['raw_name']
            sum_p = 0
            for k in range(len(self.alignments['align_list'])):
                if temp_var3 == self.alignments['align_list'][k]['raw_name']:
                    sum_p += self.alignments['bi_probability'][k]
            self.alignments['bi_probability'][h] /= sum_p
    
    def e_step_ofb(self):
        segm1,segm2 = 0,0
        for i in range(len(self.bi_gram['bi_gram'])):
            temp_var1 = self.bi_gram['bi_gram'][i]
            temp_var2 = temp_var1.split('/')[0]
            for j in range(len(self.alignments['align_list'])):
                if temp_var1 in self.alignments['align_list'][j]['bi_gram']:
                    segm1 += self.alignments['bi_probability'][j]
                if sum([1 for i in self.alignments['align_list'][j]['bi_gram'] if i.startswith(temp_var2)]) >= 1:
                    segm2 += self.alignments['bi_probability'][j]
            self.bi_gram['probability'][i] = segm1 / segm2
    
    def m_step_ofb(self):
        temp_p = 1
        for i in range(len(self.alignments['align_list'])):
            for j in self.alignments['align_list'][i]['bi_gram']:
                temp_p *= self.bi_gram['probability'][self.bi_gram['bi_gram'].index(j)]
            self.alignments['bi_probability'][i] = temp_p
            temp_p = 1
 
    def initial_uni_parameters(self):
        for i in range(len(self.uni_gram['uni_gram'])):
            temp_var1 = self.uni_gram['uni_gram'][i].split('-')[0]
            n = 0
            for j in self.uni_gram['uni_gram']:
                if j.startswith(temp_var1+'-'):
                    n += 1
            self.uni_gram['probability'][i] = 1.0 / n
        for x in range(len(self.alignments['align_list'])):
            temp_var2 = self.alignments['align_list'][x]
            for y in temp_var2['uni_gram']:
                self.alignments['uni_probability'][x] *= self.uni_gram['probability'][self.uni_gram['uni_gram'].index(y)]
        for h in range(len(self.alignments['align_list'])):
            temp_var3 = self.alignments['align_list'][h]['raw_name']
            sum_p = 0
            for k in range(len(self.alignments['align_list'])):
                if temp_var3 == self.alignments['align_list'][k]['raw_name']:
                    sum_p += self.alignments['uni_probability'][k]
            self.alignments['uni_probability'][h] /= sum_p
    
    def e_step_ofu(self):
        segm1,segm2 = 0,0
        for i in range(len(self.uni_gram['uni_gram'])):
            temp_var1 = self.uni_gram['uni_gram'][i]
            temp_var2 = temp_var1.split('-')[0]
            for j in range(len(self.alignments['align_list'])):
                if temp_var1 in self.alignments['align_list'][j]['uni_gram']:
                    segm1 += self.alignments['uni_probability'][j]
                if sum([1 for i in self.alignments['align_list'][j]['uni_gram'] if i.startswith(temp_var2)]) >= 1:
                    segm2 += self.alignments['uni_probability'][j]
            self.uni_gram['probability'][i] = segm1 / segm2
    
    def m_step_ofu(self):
        temp_p = 1
        for i in range(len(self.alignments['align_list'])):
            for j in self.alignments['align_list'][i]['uni_gram']:
                temp_p *= self.uni_gram['probability'][self.uni_gram['uni_gram'].index(j)]
            self.alignments['uni_probability'][i] = temp_p
            temp_p = 1

    def em_workfor_b(self):
        threshold,first,second = 0.001,[],[]
        print('>***** iteration ' + str(self.loop) + ':bi-gram初始化已启动！*****<')
        self.initial_bi_parameters()
        first.extend(self.bi_gram['probability'])
        while True:
            self.loop += 1
            print('>***** iteration ' + str(self.loop) + ':第' + str(self.loop)+ '次迭代已启动！*****<')
            self.e_step_ofb()
            self.m_step_ofb()
            second.extend(self.bi_gram['probability'])
            if False in list(np.abs(np.array(first) - np.array(second)) < threshold):
                if self.loop == 30:
                    print('>***** 已到循坏最高次数！！！ *****<')
                    break
                else:
                    first.clear()
                    first.extend(second)
                    second.clear()
            else:
                print('>***** 已收敛! *****<')
                break
        self.loop = 0
        
    def good_align(self):
        temp_var1 = []
        uni_gram = set()
        for i in range(len(self.alignments['align_list'])):
            temp_var2 = self.alignments['align_list'][i]['raw_name']
            Max = self.alignments['bi_probability'][i]
            good_align = self.alignments['align_list'][i]
            if temp_var2 not in temp_var1:
                for j in range(len(self.alignments['align_list'])):
                    if self.alignments['align_list'][j]['raw_name'] == temp_var2:
                        if self.alignments['bi_probability'][j] > Max:
                            Max = self.alignments['bi_probability'][j]
                            good_align = self.alignments['align_list'][j]
                temp_var1.append(good_align['raw_name'])
                self.right_bi.extend(good_align['bi_gram'])
                uni_gram.update(good_align['uni_gram'])
                
        self.right_u.extend(list(uni_gram))
    
    def em_workfor_u(self):
        threshold,first,second = 0.001,[],[]
        print('>***** iteration ' + str(self.loop) + ':uni-gram初始化已启动！*****<')
        self.initial_uni_parameters()
        first.extend(self.uni_gram['probability'])
        while True:
            self.loop += 1
            print('>***** iteration ' + str(self.loop) + ':第' + str(self.loop)+ '次迭代已启动！*****<')
            self.e_step_ofu()
            self.m_step_ofu()
            second.extend(self.uni_gram['probability'])
            if False in list(np.abs(np.array(first) - np.array(second)) < threshold):
                if self.loop == 30:
                    print('>***** 已到循坏最高次数！！！ *****<')
                    break
                else:
                    first.clear()
                    first.extend(second)
                    second.clear()
            else:
                print('>***** 已收敛! *****<')
                break
        
    def save_data(self,bi_data_path,uni_data_path,bi_path,uni_path):
        bi_gram = {'good_bi':self.right_bi}
        uni_gram = {'good_u':self.right_u}
        final_data_bi = pd.DataFrame(bi_gram)
        final_data_uni = pd.DataFrame(uni_gram)
        file1 = pd.DataFrame(self.bi_gram)
        file2 = pd.DataFrame(self.uni_gram)
        file1.to_excel(bi_path,index=False)
        file2.to_excel(uni_path,index=False)
        final_data_bi.to_excel(bi_data_path,index=False)
        final_data_uni.to_excel(uni_data_path,index=False)

if __name__ == '__main__':
    load_path = r'C:\Users\admin\Desktop\中文人名\model_data.xlsx'
    save_path1 = r'C:\Users\admin\Desktop\Cgood_bi.xlsx'
    save_path2 = r'C:\Users\admin\Desktop\Cgood_u.xlsx'
    save_bi = r'C:\Users\admin\Desktop\Cbi_gram.xlsx'
    save_uni = r'C:\Users\admin\Desktop\Cuni_gram.xlsx'
    start = t.datetime.now()
    n_gram = N_Gram()
    result = n_gram.load_data(load_path)
    n_gram.data_seting(result[0],result[1])
    n_gram.em_workfor_b()
    n_gram.em_workfor_u()
    n_gram.good_align()
    n_gram.save_data(save_path1,save_path2,save_bi,save_uni)
    end = t.datetime.now()
    print("All is down!")
    print("程序总共运行时间：",(end-start).seconds,'s')
    