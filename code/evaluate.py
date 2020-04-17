{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "》\t***** 数据加载成功 *****\t《\n",
      "》\t***** 评价函数已启动 *****\t《\n",
      "\t 最终得分为：83.50 % \t\n",
      "》\t***** 评价函数耗时:0秒 *****\t 《\n",
      "》\t***** 数据保存成功 *****\t《\n"
     ]
    }
   ],
   "source": [
    "import pandas as pd\n",
    "import datetime as t\n",
    "\n",
    "class EL:\n",
    "    '''\n",
    "    评价类\n",
    "    '''\n",
    "    def __init__(self):\n",
    "        self.correct_name = {'raw_name':[],'pre_name':[],'trans_name':[],'length':[]}\n",
    "        self.score = []\n",
    "    def load_data(self,file_path):\n",
    "        '''\n",
    "        加载数据\n",
    "        '''\n",
    "        temp_var = []\n",
    "        file = pd.read_excel(file_path)\n",
    "        for i in range(len(file['source_name'])):\n",
    "            self.correct_name['raw_name'].append(file['source_name'][i])\n",
    "            temp_var.extend(list(set(file.at[i,'refe_name1'].strip()+file.at[i,'refe_name2'].strip()+file.at[i,'refe_name3'].strip())))\n",
    "            self.correct_name['pre_name'].append(temp_var.copy())\n",
    "            self.correct_name['trans_name'].append(file.at[i,'trans_name'].strip())\n",
    "            self.correct_name['length'].append(max([len(file.at[i,'refe_name1'].strip()),len(file.at[i,'refe_name2'].strip()),len(file.at[i,'refe_name3'].strip())]))\n",
    "            temp_var.clear()\n",
    "        print(\"》\\t***** 数据加载成功 *****\\t《\")\n",
    "    def _caculate(self):\n",
    "        '''\n",
    "        功能：计算每个音译名的得分\n",
    "        '''\n",
    "        n = 0\n",
    "        for i in range(len(self.correct_name['trans_name'])):\n",
    "            N = len(self.correct_name['trans_name'][i])\n",
    "            for j in self.correct_name['trans_name'][i]:\n",
    "                if j in self.correct_name['pre_name'][i]:\n",
    "                    n += 1\n",
    "            if len(self.correct_name['trans_name'][i]) > self.correct_name['length'][i] and n == N:\n",
    "                n -= 1\n",
    "                N -= 1\n",
    "            self.score.append(round(n/N,2))\n",
    "            n = 0\n",
    "        return sum(self.score)/len(self.correct_name['raw_name'])\n",
    "    def evaluation(self):\n",
    "        '''\n",
    "        功能：评价，输出评价值\n",
    "        '''\n",
    "        print(\"》\\t***** 评价函数已启动 *****\\t《\")\n",
    "        start = t.datetime.now()\n",
    "        print(\"\\t 最终得分为：{:.2f} % \\t\".format(self._caculate()*100))\n",
    "        end = t.datetime.now()\n",
    "        print(\"》\\t***** 评价函数耗时:{:.0f}秒 *****\\t 《\".format((end-start).seconds))\n",
    "    \n",
    "    def save_data(self,path):\n",
    "        save_dict = {'name':self.correct_name['raw_name'],'trans_name':self.correct_name['trans_name'],'score':self.score}\n",
    "        result_file = pd.DataFrame(save_dict)\n",
    "        result_file.to_excel(path,index=False)\n",
    "        print(\"》\\t***** 数据保存成功 *****\\t《\")\n",
    "if __name__ == '__main__':\n",
    "    path1 = r'C:\\Users\\admin\\Desktop\\正向音译3.xlsx'\n",
    "    path2 = r'C:\\Users\\admin\\Desktop\\评价结果.xlsx'\n",
    "    el = EL()\n",
    "    el.load_data(path1)\n",
    "    el.evaluation()\n",
    "    el.save_data(path2)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
