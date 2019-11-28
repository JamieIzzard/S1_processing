#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 12:35:10 2019

@author: jizzard
"""
import os
import py_gamma as pg
import sys
import shutil



path = '/geog/data/whale/beta/jizzard/2018_c/pairs/'
pair_list = open(r'/geog/data/whale/alpha/jizzard/S1/Ferrigno/2019/pair_list.txt','w')
    

for pair in os.listdir(path):
    

    
    os.chdir(path + pair)
    

    images = [f for f in os.listdir(os.curdir) if os.path.isdir(f)]
    
    def date(x):
            return(x[7:15])
        
    images = sorted(images, key = date) 
    image_a = images[0]
    image_b = images[1]
    
    
    
    
    for file in os.listdir(image_a):
            if file.endswith('.par.slc'):
                a_par_file = image_a + '/' + file
                a_par = pg.ParFile(a_par_file)
      
    off = pair + '.off'    
    off_par = pg.ParFile(off)  
        
                
    width = off_par.get_value('offset_estimation_range_samples', dtype = int)
    lines = off_par.get_value('offset_estimation_azimuth_samples', dtype = int)
                
    ccp = pair + '.ccp'
    ccs = pair + '.ccs'
    offs = pair + '.offs'
    snr = pair + '.snr'
    sflt = pair + '.sflt'
    nflt = pair + '.nflt'
    nflt2 = pair + '.nflt2'
    nozero = pair + '.nozero'
    offsets_real = pair + '.real'
    dem_par_name = '/geog/data/whale/alpha/jizzard/dems/ferrigno_100.dem_par'
    dem_name = '/geog/data/whale/alpha/jizzard/dems/ferrigno_100.dem' #This is a large dem that covers the greater Ferrigno Area
    dem_seg_par = '/geog/data/whale/alpha/jizzard/dems/ferrigno_100.dem_seg_par'
    dem_seg = image_a + '/dem_seg'
    vel_lut = pair + '_vel.lut'
    vel_dem_seg = pair + '.dem_seg'
    vel_geo = pair + '.vel.geo'
    vel_geo_swab = vel_geo + '_swab'
    vel_tif = pair + '.vel.tif'
    disp_map = pair + '.disp'
    gnd = pair + '.gnd'
    coreg_slc_par = pair + '.par.slc.cor'
    
    pair_list.write(vel_geo + '\n' )
    
    
    max_velocity = 10.0
    snr_threshold = 5.0
    
    dem_seg_par = pg.ParFile(dem_seg_par)
    geocoded_width = dem_seg_par.get_value('width', dtype = int)
    print(geocoded_width)

    
    
    
    
    #Calculation Signal to Noise Ration
    pg.ratio(ccp, ccs, snr, width, 1, 1, 0)
    
    os.system('/geog/data/whale/alpha/ggluck/bin/threshold_snr ' + offs + ' ' + snr + ' ' + sflt + ' ' + str(snr_threshold) + ' ' + str(width) + ' ' + str(lines) + ' NaN 1')
    
    os.system('/geog/data/whale/alpha/ggluck/bin/noise_filter ' + sflt + ' ' + nflt + ' ' + str(width) + ' ' + str(lines) + ' 3 3 2.5 1 1 nan 5 4.0 ' + str(max_velocity))
    
    os.system('/geog/data/whale/alpha/ggluck/bin/noise_filter ' + nflt + ' ' + nflt2 + ' ' + str(width) + ' ' + str(lines) + ' 7 7 3.0 21 5 nan 5 10.0 ' + str(max_velocity))
    
    pg.replace_values(nflt2, 'nan', 0.0, nozero, width)
                                                        #Was missing
    pg.offset_tracking(nozero, ccp, a_par_file, off, disp_map, '-', 2, '-', 0)# 
        
    pg.lin_comb_cpx(1, disp_map, 0, 0, 0.16667, 0, gnd, width, 1, 0, 1, 1, 1)
        
        
    
        
        #convert complex offsets to real magnitude
    pg.cpx_to_real(gnd,\
                   #input complex data
                   offsets_real,\
                   #output real data
                   width,\
                   #Pixels 
                   3) #Magnitude
        
        
    pg.gc_map(coreg_slc_par, off, dem_par_name, dem_name, dem_seg_par, vel_dem_seg, vel_lut)
        
    pg.geocode_back(offsets_real, width, vel_lut, vel_geo, geocoded_width,'-', 3, 0)
        
    pg.swap_bytes(vel_geo, vel_geo_swab, 4 )
        
    pg.data2geotiff(dem_seg_par, vel_geo_swab, 2, vel_tif)
    
    os.remove(vel_lut)
    os.remove(disp_map)
    os.remove(nflt)
    #os.remove(nflt2)
    #os.remove(nozero)
    #os.remove(offsets_real)
    os.remove(sflt)
    os.remove(snr)
    #os.remove(vel_geo)
    os.remove(vel_geo_swab)
    os.remove(gnd)
    
    os.chdir(path)

    
    '''
    os.chdir(pair + '/' + image_a)
    for files in os.listdir('.'):
            
        if files.endswith('par_files'):
            shutil.rmtree(files)
        if files.endswith('.lut'):
            os.remove(files)
        if files.endswith('sim_sar'):
            os.remove(files)
                
    os.chdir(path + '/' + pair + '/' + image_b)
                 
    for files in os.listdir('.'):
        
        if files.endswith('par_files'):
            shutil.rmtree(files)
        if files.endswith('.lut'):
            os.remove(files)
        if files.endswith('sim_sar'):
            os.remove(files)
        if files.endswith('038.slc'):
            os.remove(files)
            
        os.chdir(path)
    '''
    
pair_list.close()    
