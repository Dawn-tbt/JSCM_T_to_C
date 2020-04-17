# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 18:22:54 2020

@author: admin
"""

import pandas as pd

def data_forming(train_path,file1,test_path,file2):
    train_file = pd.read_excel(train_path,sheetname='汉族人名')
    test_file = pd.read_excel(test_path)
    for i in range(len(train_file['藏文名'])):
        train_file.at[i,'藏文名'] = train_file.at[i,'藏文名'].strip().rstrip('་')
    for j in range(len(test_file['藏文名'])):
        test_file.at[j,'藏文名'] = test_file.at[j,'藏文名'].strip().rstrip('་')
    train_file.to_excel(file1,index=False)
    test_file.to_excel(file2,index=False)

if __name__ == '__main__':
        train_path = r'C:\Users\admin\Desktop\藏汉人名表.xlsx'
        test_path = r'C:\Users\admin\Desktop\Ctest1.xlsx'
        file1 = r'C:\Users\admin\Desktop\chinese_name.xlsx'
        file2 = r'C:\Users\admin\Desktop\Ctest.xlsx'
        data_forming(train_path,file1,test_path,file2)
