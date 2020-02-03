#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 09:52:26 2020

@author: jizzard
"""

import os
import py_gamma as pg
import sys
import shutil
from datetime import datetime, timedelta

def date(x):
    return(x[7:15])

directory = '/geog/data/whale/alpha/jizzard/S1/Ferrigno/2019/insar/pairs/'


os.chdir(directory)

pair = 'S1A_IW_20180225_080442_020760_038_S1B_IW_20180303_080400_009864_038'

os.chdir(pair)

images = sorted(os.listdir('.'), key = date) 
image_a = 'S1A_IW_20180225_080442_020760_038'
image_b = 'S1B_IW_20180303_080400_009864_038'


int_off_par = pair + '.int_off'
int_offs = pair + '.int_offs'
int_ccp = pair + '.int_ccp'
int_ccs = pair + '.int_ccs'
coffs = pair + '.coffs'
b_interp = image_b + '.interp'
b_interp_par = image_b + '.interp_par'
interf = pair + '.int'
a_mli = image_a + '.mli'
a_mli_par = image_a + '.mli_par'
b_mli = image_b + '.mli'
b_mli_par = image_b + '.mli_par'
baseline = pair + '.base'
int_flt = pair + '.flt'
cc = pair + '.cc'
dem_par = '/geog/data/whale/alpha/jizzard/dems/ferrigno_100.dem_par'
dem = '/geog/data/whale/alpha/jizzard/dems/ferrigno.dem'
dem_seg_par = 'dem_seg.par'
lut = pair + '.lut'
flt_geo = pair + '.flt.geo'
phase_geo = pair + '.phase.geo'
phase_geo_swab = pair + '.phase.geo.swab'
phase_tif = pair + '.phase.tif'






for file in os.listdir(image_a):
    if file.endswith('.par.slc'):
        a_par_file = image_a + '/' + file
    elif file.endswith('038.slc'): #038
        a_slc = image_a + '/' + file
    
for file in os.listdir(image_b):
    if file.endswith('.par.slc'):
        b_par_file = image_b + '/' + file
    elif file.endswith('038.slc'): #038
        b_slc = image_b + '/' + file
   

#Create Offset Parameter Files           output /ICC/rlks/azlks/noninteractive                                
pg.create_offset(a_par_file, b_par_file, int_off_par, 1, 1, 1, 0)

#Estimate Offset Between Images
pg.offset_pwr(a_slc, b_slc, a_par_file, b_par_file,\
              int_off_par, #Input offset par file\
              int_offs, #Output offsets\
              int_ccp, #Cross Correlation\
              250, 50, #Range Patch, Az Patch size, Same values as insar.csh\
              '-', #no text output\
              4,#Oversampling Faxctor 2?\
              '-', '-',#Offset estimates in range, azimuth. Same values as insar.csh (Varies regionally) 160, 240\
              0.0,#cross correlation threshold\
              5, #Lanczoc 4? Too low but in adrians script\
              '-' , '-' , #no deramp\
              int_ccs) #cross-correlation stdev


#Estimate offset polynomial
pg.offset_fit(int_offs,\
              int_ccp,\
              int_off_par,\
              coffs, #Culled Offset estimates\
              '-', #No text Output\
              0.06,#Cross-correlation threshold\
              4, #Polynomial parameters\
              0, #Non-interactive\
              )        
    
#Coregistration based on estimated offsets   
pg.SLC_interp(b_slc,\
              a_par_file,\
              b_par_file,\
              int_off_par,\
              b_interp, #b_slc resampled onto a_slc geometry\
              b_interp_par,\
              0, 0) # do all lines
  
#Calculate Interferogram    
pg.SLC_intf(a_slc,\
            b_interp,\
            a_par_file,\
            b_interp_par,\
            int_off_par,\
            interf, # Output Interferogram\
            5 , 1, #Range Looks, AzLooks\
            0, '-') #All file
     
pg.multi_look(a_slc,\
             a_par_file,\
             a_mli,\
             a_mli_par,\
             5, 1,#Rlks,Azlks\
             0, '-', 1.0, 1.0)         

pg.multi_look(b_interp,\
             b_interp_par,\
             b_mli,\
             b_mli_par,\
             5, 1,#Rlks,Azlks\
             0, '-', 1.0, 1.0)         

mli_par_obj = pg.ParFile(a_mli_par)#dem_seg_par
mli_width = mli_par_obj.get_value('range_samples', dtype = int)  
print(mli_width)  
  
#Make bmp 
pg.rasmph_pwr24(interf,\
                a_mli,\
                mli_width,# Width, 16000/range_looks\
                1, 1,\
                0, 1, 1, 1, 0.35, 1,\
                pair + 'interf.bmp')   

#Estimate Baseline    
pg.base_init(a_par_file,\
             b_par_file,\
             int_off_par,\
             interf,\
             baseline, #Output\
             4, #Method Flag FFT\
             2048, 2048,# Range and Azimuth FFT
             '-','-')#Offset to centre

#Subtract Flat earth phase
pg.ph_slope_base(interf,\
                 a_par_file,\
                 int_off_par,\
                 baseline,\
                 int_flt,#Output Interferogram with flat earth phase added\
                 )
    
#Estimate Coherence    
pg.cc_wave(int_flt,\
           a_mli,\
           b_mli,\
           cc,#Output Coherence\
           mli_width, #Mli_pixels\
           5.0, 5.0,#WindowSize\
           0)#Constant Weighting

#Generate Coherence Image    
pg.rascc(cc,\
         a_mli,\
         mli_width,\
         1,1,0,1,1,\
         0.0, 0.2,#correlation scale linear\
         '-', '-', '-',\
         pair + '_cc.bmp')
    
#Generate flt bmp    
pg.rasmph_pwr24(int_flt,\
                a_mli,\
                mli_width,\
                1,1,0,1,1,1,0.35,1,\
                pair + '.flt.bmp')
    
#calculate Geocoding lut
pg.gec_map(a_par_file,\
           int_off_par,\
           dem_par,\
           0,\
           dem_seg_par,\
           lut) # Output
    
dem_seg_par_obj = pg.ParFile(dem_seg_par)#dem_seg_par
geocoded_width = dem_seg_par_obj.get_value('width', dtype = int) 
print(geocoded_width)   
    
#Geocode to Map coordinates    
pg.geocode_back(int_flt, #input\
                mli_width,#width\
                lut,\
                flt_geo, #Output\
                geocoded_width,0,\
                1, 1)


pg.cpx_to_real(flt_geo,\
               phase_geo,\
               geocoded_width,\
               4)#Phase
    
    
pg.swap_bytes(phase_geo,phase_geo_swab,4)

pg.data2geotiff(dem_seg_par, phase_geo_swab,2,phase_tif)
        
        
        
        
        
