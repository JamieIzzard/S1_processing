#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 11:09:39 2019

@author: jizzard
"""

import py_gamma as pg
import os
import numpy as np
import sys

image_a = '21_01'
image_b = '02_02'

file_name = image_a + '/' + image_b

directory = '/geog/data/whale/alpha/jizzard/feature_tracking_test/21_01_02_02/'
os.chdir(os.path.dirname(directory))

if len(os.listdir(image_a)) != 2 and len(os.listdir(image_b)) != 2:
    sys.exit('2 Files needed in image directories')

for file in os.listdir(image_a):
    if file.endswith('.par.slc'):
        a_par_file = image_a + '/' + file
    elif file.endswith('.slc'):
        a_slc = image_a + '/' + file
    
    #if a_par_file not in locals() or a_par_file not in globals():
        #sys.exit('Image a Parameter File not Found')
    #if a_slc not in locals() or a_slc not in globals():
        #sys.exit('Image a Slc File not Found')
        
for file in os.listdir(image_b):
    if file.endswith('.par.slc'):
        b_par_file = image_b + '/' + file
    elif file.endswith('.slc'):
        b_slc = image_b + '/' + file
    #if b_par_file not in locals():
        #sys.exit('Image b Parameter File not Found')
    #if b_slc not in locals():
        #sys.exit('Image b Slc File not Found')   
        
        

           
pg.rdc_trans(a_par_file,\
             0.0, \
             #DEM reference height
             b_par_file,\
             'file.lut' )#outputr lookup table

pg.SLC_interp_lt(b_slc, a_par_file, b_par_file,\
                 #input 
                 'file.lut',\
                 #input lookup table
                 a_par_file, b_par_file,\
                 #references par files
                 '-',\
                 #no input off par file
                 'coregistered.slc', 'coregistered.par.slc')
                #Output coregistered images


pg.create_offset(a_par_file, 'coregistered.par.slc', \
                 #inputs
                 'pair.off',\
                 #output par file
                 1,\
                 #Intensity cross-correlation
                 50,10,\
                 #Range, Azimuth looks
                 0)#non-interactive
                                                                #maybe coregistered slc par 
pg.offset_pwr_tracking(a_slc, 'coregistered.slc', a_par_file, 'coregistered.par.slc',\
                       'pair.off',\
                       #input offset parameter file created with create_offset
                       'pair.offs',\
                       #complex offset estimations in range and azimuth
                       'pair.ccp',\
                       416, 128,\
                       #range and Azimuth windows
                       '-',\
                       #no output in text format
                       '-',\
                       #oversampling factor ovr
                       '-1',\
                       #Threshold
                       50, 10,\
                       #range and azimuth spacing
                       '-','-','-','-',\
                       #rstart rstop azstart azstop
                       5,\
                       #Lanczos interp order
                       1.0,\
                       #bandwidth fraction of low pass filter on complex data (0.0 to 1.0)
                       0,\
                       #no deramp
                       0,\
                       #no intensity low pass filter
                       0,1,\
                       #no print flags (0,0)
                       'pair.ccs')
                        #output ccs


#track_to_grid #Need script

pixels=1317

#convert complex offsets to real magnitude
pg.cpx_to_real('pair.offs',\
               #input complex data
               'pair.real',\
               #output real data
               pixels,\
               #Pixels 1317?
               3) #Magnitude


