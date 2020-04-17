# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 16:46:53 2020

@author: admin
"""

import pandas as pd
import numpy as np
import datetime as t


class Generate_cname:
    def __init__(self):
        self.uni_data = {'uni_gram':[],'uni_prob':[]}
        self.bi_data = {'bi_gram':[],'bi_prob':[],'count':[]}
        self.trans_result = {'source_name':[],'target_name':[],'trans_name':[]}
        self.right_u = []
        
        
    def load_data(self,test_path,uni_path,bi_path,uni_path1):
        test_file = pd.read_excel(test_path)
        uni_file = pd.read_excel(uni_path)
        uni_file1 = pd.read_excel(uni_path1)
        bi_file = pd.read_excel(bi_path)
        for r in list(uni_file1['good_u']):
            self.right_u.append(r.strip())
        for i in range(len(uni_file['uni_gram'])):
            self.uni_data['uni_gram'].append(uni_file.at[i,'uni_gram'].strip())
        for j in range(len(bi_file['bi_gram'])):
            self.bi_data['bi_gram'].append(bi_file.at[j,'bi_gram'].strip())
        for x in range(len(test_file['藏文名'])):
            self.trans_result['source_name'].append(test_file.at[x,'藏文名'].strip())
            self.trans_result['target_name'].append(test_file.at[x,'中文名'].strip())
        self.bi_data['bi_prob'].extend(list(bi_file['probability']))
        self.bi_data['count'].extend(list(bi_file['count']))
        self.uni_data['uni_prob'].extend(list(uni_file['probability']))

    def viterbi_search(self,t_name):
        trans_candidate = []
        temp_list = []
        over_point = 0
        for i in t_name:
            for j in self.right_u:
                if j.startswith(i+'-'):
                    temp_list.append(j)
            if temp_list:
                trans_candidate.append(temp_list.copy())
                temp_list.clear()
            else:
                temp_list.append(i+'-'+'*')
                trans_candidate.append(temp_list.copy())
                temp_list.clear()
        G = [[0 for j in i] for i in trans_candidate]
        X = [[0 for x in y] for y in trans_candidate]
        for x in range(len(trans_candidate)):
            for y in range(len(trans_candidate[x])):
                if x == 0:
                    temp_var2 = 'BOS' + '/' + trans_candidate[x][y]
                    if temp_var2 in self.bi_data['bi_gram']:
                        G[x][y] = np.log10(self.bi_data['bi_prob'][self.bi_data['bi_gram'].index(temp_var2)])
                        X[x][y] = -1
                    else:
                        G[x][y] = np.log10(self.li_smooth(temp_var2))
                        X[x][y] = -1
                else:
                    for z in range(len(trans_candidate[x-1])):
                        temp_var2 = trans_candidate[x-1][z] + '/' + trans_candidate[x][y]
                        if temp_var2 in self.bi_data['bi_gram']:
                            temp_list.append(G[x-1][z] + np.log10(self.bi_data['bi_prob'][self.bi_data['bi_gram'].index(temp_var2)]))
                        else:
                            temp_list.append(G[x-1][z] + np.log10(self.li_smooth(temp_var2)))
                    G[x][y] = min(temp_list)
                    X[x][y] = temp_list.index(G[x][y])
                    temp_list.clear()
            if x == len(trans_candidate)-1:
                for h in range(len(trans_candidate[x])):
                    temp_var = trans_candidate[x][h] + '/' + 'EOS'
                    if temp_var in self.bi_data['bi_gram']:
                        temp_list.append(G[x][h] + np.log10(self.bi_data['bi_prob'][self.bi_data['bi_gram'].index(temp_var)]))
                    else:
                        temp_list.append(G[x][h] + np.log10(self.li_smooth(temp_var)))
                over_point = temp_list.index(min(temp_list))
                temp_list.clear()
        t1 = len(trans_candidate) - 1
        temp = trans_candidate[-1][over_point].split('-')[1]
        t2 = X[-1][over_point]
        while t2 >= 0:
            t1 -= 1
            temp = trans_candidate[t1][t2].split('-')[1] + temp
            t2 = X[t1][t2]
        temp.strip()
        return temp

    def li_smooth(self,bi_gram):
        x1,x2 = 0.5,0.5
        c1,c2 = 0,0
        y1,y2 = 0,0
        loop = 0
        while True:
            loop += 1
            for i in range(len(self.bi_data['bi_gram'][:50])):
                up1 = x1 * self.bi_data['bi_prob'][i] * self.bi_data['count'][i]
                down1 = x1 * self.bi_data['bi_prob'][i] + x2 * self.uni_data['uni_prob'][self.uni_data['uni_gram'].index(self.bi_data['bi_gram'][i].split('/')[1])]
                up2 = self.bi_data['count'][i] * x2 * self.uni_data['uni_prob'][self.uni_data['uni_gram'].index(self.bi_data['bi_gram'][i].split('/')[1])]
                down2 = x1 * self.bi_data['bi_prob'][i] + x2 * self.uni_data['uni_prob'][self.uni_data['uni_gram'].index(self.bi_data['bi_gram'][i].split('/')[1])]
                c1 += up1 / down1
                c2 += up2 / down2
            y1 = c1 / (c1 + c2)
            y2 = c2 / (c1 + c2)
            if abs(x1-y1) < 0.01 and abs(x2-y2) < 0.01:
                break
            else:
                if loop == 20:
                    print('已达最高迭代次数！')
                    break
                else:
                    x1 = y1
                    x2 = y2
        if bi_gram.split('/')[0] in self.uni_data['uni_gram']:
            result = y1 * min(self.bi_data['bi_prob']) + y2 * self.uni_data['uni_prob'][self.uni_data['uni_gram'].index(bi_gram.split('/')[0])]
        else:
            result = y1 * min(self.bi_data['bi_prob']) + y2 * 1
        return result

    def generate_candidate(self):
        for i in range(len(self.trans_result['source_name'])):
            temp_var = self.trans_result['source_name'][i].split('་')
            result = self.viterbi_search(temp_var)
            self.trans_result['trans_name'].append(result)
        
    def save_data(self,path):
        trans_data = pd.DataFrame(self.trans_result)
        trans_data.to_excel(path,index=False)
        
    
    def evaluate(self):
        n1,n2 = 0,0
        P,R,F1 = 0,0,0
        N = len(self.trans_result['source_name'])
        for i in range(len(self.trans_result['target_name'])):
            if self.trans_result['trans_name'][i]:
                n1 += 1
                if self.trans_result['target_name'][i] == self.trans_result['trans_name'][i]:
                    n2 += 1
        R = (n1 / N)
        P = (n2 / n1)
        if P == 0 or R == 0:
            F1 = 0
        else:
            F1 = ((2 * P * R) / (P + R)) * 100
        
        print("F1:{:.2f}% P:{:.2f}% R:{:.2f}%".format(F1,P*100,R*100))


if __name__ == '__main__':
    test_file = r'C:\Users\admin\Desktop\藏族人名\test_data3.xlsx'
    uni_file1 = r'C:\Users\admin\Desktop\Cuni_gram.xlsx'
    uni_file2 = r'C:\Users\admin\Desktop\Cgood_u.xlsx'
    bi_file = r'C:\Users\admin\Desktop\Cbi_gram.xlsx'
    result_file = r'C:\Users\admin\Desktop\正向音译3.xlsx'
    cname = Generate_cname()
    start = t.datetime.now()
    cname.load_data(test_file,uni_file1,bi_file,uni_file2)
    cname.generate_candidate()
    cname.evaluation()
    cname.save_data(result_file)
    end = t.datetime.now()
    print('程序总共运行时间：',(end-start).seconds,'s.')