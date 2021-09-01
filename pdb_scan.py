#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 16:27:23 2021

@author: wmm
"""

import os
from pyrosetta import pose_from_pdb, init
from pyrosetta.rosetta.core.select.residue_selector import SecondaryStructureSelector
init()


'''
process_dir=r'/Users/wmm/Desktop/'
files=os.listdir(process_dir)
for file in files:
  if os.path.splitext(file)[-1]=='.pdb':
      pose=pose_from_pdb(file)
      print(pose.residue(30).name())
  else:
      pass
'''

datapath='/Users/wmm/Downloads/Loop'
data_test_order=0
for file in os.listdir(datapath):
    #print(datapath)
    if file.endswith(".pdb"):
        try:
            print(file)
            print(type(file))
            command="python loop_selector.py "+file+" "+str(data_test_order)
            os.system(command)
            data_test_order+=1
        except Exception as e:
            pass
        continue
    else:
        pass