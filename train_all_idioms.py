#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 00:13:10 2018

@author: maximoskaliakatsos-papakostas
"""

import sys
import pickle
import os
cwd = os.getcwd()
sys.path.insert(0, cwd+'/CM_train')
sys.path.insert(0, cwd+'/CM_auxiliary')
import CM_TR_TrainingIdiom_class as tic
import Grouping_functions as grp
# use folder of printing functions
sys.path.insert(0, cwd + '/CM_logging')
import harmonisation_printer as prt

mainFolder = cwd + '/training_data/'
logging = True

# ensure logs directory exists
os.makedirs(cwd + '/training_logs', exist_ok=True)

for dirpath, dirnames, filenames in os.walk(mainFolder):
    # consider only directories that contain at least one XML file
    xml_files = [fn for fn in filenames if fn.endswith('.xml')]
    if not xml_files:
        continue
    idiom_name = dirpath.split('/')[-1]
    print('f: ', idiom_name)
    # check if logging is required
    if logging:
        training_log_file = cwd + '/training_logs/' + idiom_name
        prt.initialise_log_file(training_log_file)
    # build idiom from this folder only
    folder_with_trailing_sep = dirpath if dirpath.endswith('/') else (dirpath + '/')
    idiom = tic.TrainingIdiom(folder_with_trailing_sep, logging=logging, log_file=training_log_file)
    idiom = grp.group_gcts_of_idiom(idiom)
    # save learned idiom
    out_path = 'trained_idioms/' + idiom.name + '.pickle'
    if os.path.exists(out_path):
        print('keep (exists):', idiom.name)
        continue
    with open(out_path, 'wb') as handle:
        pickle.dump(idiom, handle, protocol=pickle.HIGHEST_PROTOCOL)