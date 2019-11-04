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



directory = '/geog/data/whale/alpha/jizzard/S1/Ferrigno/2019/pairs/S1A_IW_20190115_080501_025485_038_S1B_IW_20190121_080419_014589_038/'

os.chdir(os.path.dirname(directory))

def date(x):
    return(x[7:15])

images = sorted(os.listdir('.'), key = date) 
image_a = images[0]
image_b = images[1]
    
im_name = image_a + '_' + image_b
coreg_slc = im_name + '.slc.cor'
coreg_slc_par = im_name + '.par.slc.cor'
lut = im_name + '.lut'
off_par = im_name + '.off'
offsets = im_name + '.offs'
ccp = im_name + '.ccp'
ccs = im_name + '.ccs'
offsets_real = im_name + '.real'
dem_par_name = '/geog/data/whale/alpha/jizzard/dems/ferrigno_10.dem_par'
dem_name = '/geog/data/whale/alpha/jizzard/dems/ferrigno_10.dem'
dem_seg_par = image_a + '/dem_seg_par'
dem_seg = image_a + '/dem_seg'
vel_lut = im_name + '_vel.lut'
vel_dem_seg = im_name + '.dem_seg'
vel_geo = im_name + 'vel.geo'
vel_geo_swab = vel_geo + '_swab'
vel_tif = im_name + '.tif'

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
             lut)#outputr lookup table



pg.SLC_interp_lt(b_slc, a_par_file, b_par_file,\
                 #input 
                 lut,\
                 #input lookup table
                 a_par_file, b_par_file,\
                 #references par files
                 '-',\
                 #no input off par file
                 coreg_slc, coreg_slc_par)
                #Output coregistered images


pg.create_offset(a_par_file, coreg_slc_par, \
                 #inputs
                 off_par,\
                 #output par file
                 1,\
                 #Intensity cross-correlation
                 50,10,\
                 #Range, Azimuth looks
                 0)#non-interactive
 

os.system('offset_pwr_tracking ' + a_slc + ' ' + coreg_slc + ' ' +  a_par_file + ' ' + coreg_slc_par + ' ' + off_par + ' ' + offsets + ' ' + ccp + ' 416 128 - - -1 50 10 - - - - 5 1.0 0 0 0 0 ' + ccs)


#track_to_grid #Need script

pixels=1317
geocoded_width = 10000

#convert complex offsets to real magnitude
pg.cpx_to_real(offsets,\
               #input complex data
               offsets_real,\
               #output real data
               pixels,\
               #Pixels 1317?
               3) #Magnitude


pg.gc_map(coreg_slc_par, off_par, dem_par_name, dem_name, dem_seg_par, vel_dem_seg, vel_lut)

pg.geocode_back(offsets_real, pixels, vel_lut, vel_geo, geocoded_width,'-', 3, 0)

pg.swap_bytes(vel_geo, vel_geo_swab, 4 )

pg.data2geotiff(dem_seg_par, vel_geo_swab, 2, vel_tif)



