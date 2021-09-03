#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 10:27:00 2021

@author: wmm
"""


import os
import sys
import pandas as pd
import requests
import xlwt
import time
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES=5
## 调用pyrosetta中的二级结构选择器
from pyrosetta import pose_from_pdb, init
from pyrosetta.rosetta.core.select.residue_selector import SecondaryStructureSelector
from pyrosetta.rosetta.protocols.membrane import get_secstruct
init()


## test code
# 根据残基编号来选择
#from pyrosetta.rosetta.core.select.residue_selector import ResidueIndexSelector
# 根据具体的Pose编号选择, example
#pose=pose_from_pdb("7ni6.pdb")
#pose_index_selector=ResidueIndexSelector('40,42,44')
#residue_selector=pose_index_selector.apply(pose)
#print(residue_selector)
#name为氨基酸全名
#print(pose.residue(40).name())
#name1为缩写
#print(pose.residue(40).name())


## 读取pdb文件
##pose=pose_from_pdb("test.pdb")
pose=pose_from_pdb(sys.argv[1])
#print(sys.argv)

## 二级结构选择器筛选出需要的二级结构
## E：beta折叠 H:α-螺旋 L:loop无规卷曲,选择所有该类型的二级结构区间。
ss_selector=SecondaryStructureSelector('L') #选择所有loop无规卷曲；
selected=ss_selector.apply(pose)
index_list=[index+1 for index, i in enumerate(selected) if i==1]
#print(index_list)


## 准备一个excel文件，存入之后收集到的所有数据
work_book=xlwt.Workbook(encoding='utf-8')
sheet=work_book.add_sheet('sheet1', cell_overwrite_ok=True)


## 利用滑动窗口，提取其中连续的序列的数字，作为index用于下一步提取氨基酸序列
linker_sequence_number=[]
left_anchor=0
right_anchor=1
current_linker=[index_list[0]]
list_length=len(index_list)
while right_anchor < list_length:
    ## 如果数字连续，当前窗口向右边延展，左边不动
    if index_list[right_anchor] == index_list[right_anchor-1]+1:
        current_linker.append(index_list[right_anchor])
        right_anchor+=1
    else:
        ## 如果数字断开，则当前窗口左端调到断开的地方重新计数
        if len(current_linker) >= 2:
            linker_sequence_number.append(current_linker)
        else:
            pass
        current_linker=[]
        left_anchor=right_anchor
        right_anchor+=1
        current_linker=[index_list[left_anchor]]
print(linker_sequence_number)



## 利用上一步提取到的index，提取linker sequence, linker_secondary_structure, 存入linker_sequence
linker_sequence=[]
current_sequence=''
n=0
for sequence in linker_sequence_number:
    for res_number in sequence:
        current_sequence=current_sequence+pose.residue(res_number).name1()
    linker_sequence.append(current_sequence)
    left_point=sequence[0]
    right_point=sequence[-1]
    linker_region=str(left_point)+"-"+str(right_point)
    linker_length=len(current_sequence)
    uniprot_id=sys.argv[1].split("-")[1]
    print(uniprot_id)
    sheet.write(n,1,current_sequence)
    sheet.write(n,2,uniprot_id)
    sheet.write(n,3,linker_region)
    sheet.write(n,4,linker_length)
    current_sequence=''
    n+=1
print(linker_sequence)

## 提取linker二级结构信息
secondary_sequence=''.join(get_secstruct(pose))
secondary_sequence_list=[]
current_secondary_sequence=''
n=0
for sequence in linker_sequence_number:
    for res_number in sequence:
        current_secondary_sequence=current_secondary_sequence+secondary_sequence[res_number]
    secondary_sequence_list.append(current_secondary_sequence)
    L_count=current_secondary_sequence.count("L")
    seq_length=len(current_secondary_sequence)
    L_rate=float(L_count / seq_length)
    print(current_secondary_sequence)
    sheet.write(n,5,current_secondary_sequence)
    sheet.write(n,6,L_rate)
    if L_rate <= 0.3:
        sheet.write(n, 7, "True")
    else:
        sheet.write(n, 7, "False")
    current_secondary_sequence=''
    n+=1


'''
## 利用多肽序列计算API，计算读取出的序列的信息，并储存到excel里
## 利用GOR4二级结构预测工具计算获得的linker的二级结构
n=0
time_text=1
for linker_item in linker_sequence:
    data="title=&notice="+linker_item+"&ali_width=70"
    headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
             "Accept-Encoding": "gzip, deflate, br",
             "Accept-Language": "zh-CN,zh;q=0.9",
             "Cache-Control": "max-age=0",
             "Connection": "close",
             "Content-Length": "96",
             "Content-Type": "application/x-www-form-urlencoded",
             "Host": "npsa-prabi.ibcp.fr",
             "Origin": "https://npsa-prabi.ibcp.fr",
             "Referer": "https://npsa-prabi.ibcp.fr/cgi-bin/npsa_automat.pl?page=/NPSA/npsa_gor4.html",
             "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
             "sec-ch-ua-mobile": "?0",
             "Sec-Fetch-Dest": "document",
             "Sec-Fetch-Mode": "navigate",
             "Sec-Fetch-Site": "same-origin",
             "Sec-Fetch-User": "?1",
             "Upgrade-Insecure-Requests": "1",
             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
             }
    url="https://npsa-prabi.ibcp.fr/cgi-bin/secpred_gor4.pl"
    if time_text%5 == 0:
        time.sleep(5)
    else:
        res=requests.post(url, data=data, headers=headers, verify=False)
        res_text=res.text
        bs=BeautifulSoup(res_text,'lxml')
        if bs.select("code"):
            secondary_info=bs.select("code")[0].text.split("\n")[4]
            print("secondary_info:", secondary_info)
            c_count=secondary_info.count("c")
            seq_length=len(secondary_info)
            c_rate=float(c_count/seq_length)
            sheet.write(n,5,secondary_info)
            sheet.write(n,6,c_rate)
            if c_rate <= 0.3:
                sheet.write(n,7,"True")
            else:
                sheet.write(n,7,"False")
        else:
            secondary_info="no data"
            print("secondary_info:", secondary_info)
            sheet.write(n,5,"no data")
            sheet.write(n,6,"no data")
            sheet.write(n,7,"no data")
        n+=1
        time_text+=1

'''

work_book.save(sys.argv[2]+'Loop_extract.xls')













