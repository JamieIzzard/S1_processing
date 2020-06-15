#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 17 14:41:17 2020

@author: jizzard
"""

import os
import py_gamma as pg
import numpy as np
from datetime import datetime, timedelta
import sys
from osgeo import osr
from shutil import copyfile
import pandas as pd

unzipped_path = '/geog/data/whale/gamma/jizzard/S1/larsen/unzipped/'
path = '/geog/data/whale/gamma/jizzard/S1/larsen/pairs/'


dem_par = '/geog/data/whale/alpha/jizzard/dems/ant_pen/ant_pen.dem_par' # 3001 * 3121
dem = '/geog/data/whale/alpha/jizzard/dems/ant_pen/ant_pen.dem'






def Get_lut(image, dem, dem_par):
    
    os.chdir(unzipped_path + image) 
    
    slc = image + '.slc'
    slc_par = image + '.par.slc'
    mli = image + '.mli_50'
    mli_par = image + '.mli_50_par'
    

    
    pg.multi_look(slc,\
                 slc_par,\
                 mli,\
                 mli_par,\
                 50,10)
    
    #dem_seg_par = image + '.dem_seg_par'
    dem_seg_par=  'dem_seg_par'
    dem_seg = image + '.dem'
    dem2sar_lookup_table = image + '.dem2sar.lut'
    sim_sar = image + '.sim_sar'
    surface_zenith = image + '.zen'
    normal_orientation = image + '.nml_ori'
    inc_angle = image + '.inc_ang'
    proj_angle = image + '.proj_ang'
    area_factor = '-'
    layover_shadow = '-'
    frame = '-'
    ls_mode = 2 #Possibly 1?
    
    
    
    #Maps Slant Range to Ground Range
    pg.gc_map(mli_par,\
              '-',\
              dem_par,\
              dem,\
              dem_seg_par,\
              dem_seg,\
              dem2sar_lookup_table,\
              1,1,\
              sim_sar,\
              surface_zenith,\
              normal_orientation,\
              inc_angle,\
              proj_angle,\
              area_factor,\
              layover_shadow,\
              frame,\
              ls_mode)
    
    
    mli_par_file = pg.ParFile(mli_par)
    mli_pixels = mli_par_file.get_value('range_samples')
    mli_lines = mli_par_file.get_value('azimuth_lines')
    
    print('mli_pixels: {}, mli_lines: {}'.format(mli_pixels, mli_lines))
    
    
    dem_seg_par_file = pg.ParFile(dem_seg_par)
    pixels = dem_seg_par_file.get_value('width')
    lines = dem_seg_par_file.get_value('nlines')
    
    print('pixels: {}, lines = {}'.format(pixels, lines))
    
    
    
    mli_geo = image + ('mli_50_geo')
    
    #geocode mli to ground range
    pg.geocode_back(mli,\
                    mli_pixels,\
                    dem2sar_lookup_table,\
                    mli_geo,\
                    pixels,\
                    lines,\
                    3,0)
        
    pg.ras_linear(mli_geo,\
              pixels,\
              '-','-','-','-','-','-','-',\
              mli_geo + '.bmp')
    
    pg.ras_linear(mli,\
              mli_pixels,\
              '-','-','-','-','-','-','-',\
              mli + '.bmp')   
        
    mli_geo_swab = mli_geo + '.swab'
    
    pg.swap_bytes(mli_geo, mli_geo_swab, 4)
    
    mli_geotif = image + '.mli_50.tif'
    
    pg.data2geotiff(dem_seg_par,\
                    mli_geo_swab,\
                    2,\
                    mli_geotif)
    
    os.remove(mli_geo_swab)
    
    sar2dem_lookup_table = image + '.sar2dem.lut'
    
    
    pg.gc_map_inversion(dem2sar_lookup_table,\
                        pixels,\
                        sar2dem_lookup_table,\
                        mli_pixels,\
                        mli_lines,\
                        1,2)
    
    inc_angle_sar = inc_angle + '.sar'
    

         
    pg.geocode_back(inc_angle,\
                    pixels,\
                    sar2dem_lookup_table,\
                    inc_angle_sar,\
                    mli_pixels,\
                    mli_lines)
        
    
    
    pg.ras_linear(inc_angle,\
              pixels,\
              '-','-','-','-','-','-','-',\
              inc_angle + '.bmp')
        
    pg.ras_linear(inc_angle_sar,\
              mli_pixels,\
              '-','-','-','-','-','-','-',\
              inc_angle_sar + '.bmp')
    
def Get_tide(pair):
    
    os.chdir(path + pair)
    
    images = [f for f in os.listdir(os.curdir) if os.path.isdir(f)]
    
    def date(x):
            return(x[7:15])
        
    images = sorted(images, key = date) 
    image_a = images[0]
    image_b = images[1]
    
    
    date_a = image_a[7:22]
    date_b = image_b[7:22]   
    
    data_path = '/geog/data/whale/alpha/jizzard/tidal_model/application/DATA/'
    tide_path = '/geog/data/whale/alpha/jizzard/tidal_model/application/'
    out_path = '/geog/data/whale/alpha/jizzard/tidal_model/application/OUT/'
    
    os.chdir(path + pair)
    
    dem_seg_par_file =  image_a + '/dem_seg_par'
    
    seg_dem_par = pg.ParFile(dem_seg_par_file)
    
    
    print('Date:{}'.format(date_a))
    
    
    ps_coords = 'coords_ps'
    latlong_coords = 'coords_latlong'
    
    epost = float(seg_dem_par.get_value('post_east',dtype = int, index = 0))
    npost = float(seg_dem_par.get_value('post_north',dtype = int, index = 0))
    width = seg_dem_par.get_value('width', dtype = int)
    lines = seg_dem_par.get_value('nlines', dtype = int)
    
    
    tl_northing = float(seg_dem_par.get_value('corner_north', dtype = int, index = 0))
    tl_easting = float(seg_dem_par.get_value('corner_east', dtype = int, index = 0))
    
    '''
    br_northing = float(tl_northing + npost * lines)
    br_easting = float(tl_easting + epost * width)
    bl_northing = float(br_northing)
    tr_easting  = float(br_easting)
    tr_northing = float(tl_northing)
    bl_easting  = float(tl_easting)
    R_aoi = '-R' + str(tl_easting)+'/'+str(br_easting)+'/'+str(br_northing)+'/'+str(tl_northing)
    '''
    os.remove('ps_coords')
    
    if 'coords_ps' not in os.listdir('.'):
        f = open(ps_coords, 'w+')
        print('Getting Projected Points') 
        for line in range(0,lines):
            for column in range(0, width):
                east = (tl_easting + epost * column)
                north = (tl_northing + npost * line)
                f.write('%f %f \n' % (east,north))
        print(east)
        print(north)                                       
        f.close()           
        print('converting to lat/long')
        os.system('gdaltransform -s_srs \'+proj=stere +lat_0=-90 +lon_0=0 +lat_ts=-71\' -t_srs \'+proj=latlong\' < ' + ps_coords + ' > ' + latlong_coords)
    
    else:
        print('File Already Exists')
        
    libpath  = '$HOME/v97'
    
    copyfile(latlong_coords, data_path + date_a + '_lonlat.dat')
    copyfile(latlong_coords, data_path + date_b + '_lonlat.dat')
        
    os.chdir(tide_path)

    print('running model for ' + date_a)
    os.system('sh run_sb_get_preds_v3.sh ' + libpath + ' ' + date_a + ' no')
    print('running model for ' + date_b)
    os.system('sh run_sb_get_preds_v3.sh ' + libpath + ' ' + date_b + ' no')
    
    os.chdir(path + pair)
    
    tide_z1 = image_a + '.geo.tide_z'
    tide_z2 = image_b + '.geo.tide_z'
    tide_dz = pair + '.geo.tide_dz'
    
    copyfile(out_path + date_a + '_z', tide_z1)
    os.remove(out_path + date_a + '_z')
    copyfile(out_path + date_b + '_z', tide_z2)
    os.remove(out_path + date_b + '_z')
    
    
    pg.lin_comb(2,\
                tide_z2,\
                tide_z1,\
                0,\
                1, -1,\
                tide_dz,\
                width,\
                1, 0)
    
    sar2dem_lut = image_a + '/' + image_a + '.sar2dem.lut'
    tide_dz_sar = pair + '.sar.tide_dz'
    tide_dz_sar_flip = pair + '.sar.tide_dz.flip'
    
    mli_par = image_a + '/' + image_a + '.mli_50_par'
    mli_parfile = pg.ParFile(mli_par)
    
    mli_width = mli_parfile.get_value('range_samples')
    mli_lines = mli_parfile.get_value('azimuth_lines')
    
    
    
    
    pg.geocode_back(tide_dz,\
                    width,\
                    sar2dem_lut,\
                    tide_dz_sar,\
                    mli_width,\
                    mli_lines,\
                    0, 0)
        
    pg.ras_linear(tide_dz,\
                  width,\
                  '-','-','-','-',-1.5,-0.5,'-',\
                  tide_dz + '.bmp')
    
    
    
    
    #pg.flip(tide_dz_sar, tide_dz_sar_flip, mli_width, 0, 1)
                  
    pg.ras_linear(tide_dz_sar,\
                  mli_width,\
                  '-','-','-','-',-1.5,-0.5,'-',\
                  tide_dz_sar + '.bmp')
        
def Tide_correct(pair):
    
    
    os.chdir(path + pair)
    
    pre_date_str = pair[7:22]
    pre_date = datetime.strptime(pre_date_str,'%Y%m%d_%H%M%S') #
    post_date_str = pair[41:56]
    post_date = datetime.strptime(post_date_str,'%Y%m%d_%H%M%S')
    timedelta_between = post_date - pre_date
    interval = 1/(timedelta_between / timedelta (days=1)) # Returns Fraction to multiply by for meters per day
    print(interval)
    pair_delay = timedelta_between.days
    
    images = [f for f in os.listdir(os.curdir) if os.path.isdir(f)]
    
    def date(x):
            return(x[7:15])
        
    images = sorted(images, key = date) 
    image_a = images[0]
    image_b = images[1]
    
    
    mli_par = image_a + '/' + image_a + '.mli_50_par'
    mli_parfile = pg.ParFile(mli_par)
    
    pixels = mli_parfile.get_value('range_samples')
    lines = mli_parfile.get_value('azimuth_lines')
    
    dem_seg_par_file =  image_a + '/dem_seg_par'
    seg_dem_par = pg.ParFile(dem_seg_par_file)

    geo_width = seg_dem_par.get_value('width', dtype = int)
    geo_lines = seg_dem_par.get_value('nlines', dtype = int)
    
    tide_path = '/geog/data/whale/alpha/jizzard/S1/Ferrigno/tide/'
    vel_map = pair + '.filt.disp' #fcomplex
    #tide_dz_sar_flip = pair + '.sar.tide_dz.flip'
    tide_dz_sar = pair + '.sar.tide_dz'
    inc_angle_sar= image_a + '/' + image_a + '.inc_ang.sar' #float, radians
    vel_out =  pair + '.gnd_detide' #fcomplex
    
    
 
    
    vel_detide_real = pair + '.detide.real'
    vel_out_perday = pair + '.vel.detide.gnd'
    
    os.system(tide_path + 'remove_tidal_offset ' + vel_map + ' ' + tide_dz_sar + ' '\
              + inc_angle_sar + ' ' + str(pair_delay) + ' ' + vel_out + ' '\
              + str(pixels) + ' ' + str(lines))
    
        
    pg.lin_comb_cpx(1, vel_out, 0, 0, interval, 0, vel_out_perday, pixels, 1, 0, 1, 1, 1)
    
    pg.cpx_to_real(vel_out_perday, vel_detide_real, pixels, 3)
    pg.ras_linear(vel_detide_real,pixels,1,'-',1,1,0.0,1.0,1,vel_detide_real + '.bmp' ) 
    
    
    dem2sar_lut = image_a + '/' + image_a + '.dem2sar.lut'
    
    vel_detide_real_geo = vel_detide_real + '.geo'
    vel_detide_real_geo_swab = vel_detide_real_geo + '.swab'
    vel_detide_tif = vel_detide_real_geo + '.tif'    

    
    
    
    
    pg.geocode_back(vel_detide_real, pixels, dem2sar_lut, vel_detide_real_geo, geo_width, '-', '-', 0)
    
    pg.ras_linear(vel_detide_real_geo, geo_width ,1,'-',1,1,0.0,1.0,1,vel_detide_real_geo + '.bmp' ) 
    
    pg.swap_bytes(vel_detide_real_geo, vel_detide_real_geo_swab, 4)
    
    dem_seg_par = image_a + '/dem_seg_par'
    
    pg.data2geotiff(dem_seg_par, vel_detide_real_geo_swab, 2, vel_detide_tif)
    
    geo_tide_dz = pair + '.geo.tide_dz'
    geo_tide_diz_tif = geo_tide_dz + '.tif'
    tide_dz_swab = geo_tide_dz + '.swab'
    pg.swap_bytes(geo_tide_dz, tide_dz_swab, 4)
    pg.data2geotiff(dem_seg_par, tide_dz_swab, 2, geo_tide_diz_tif)

for image in os.listdir(unzipped_path):
    print(image)
    Get_lut(image, dem, dem_par)

for pair in os.listdir(path):
    #Get_tide(pair)
    Tide_correct(pair)

    
   
    
    
                
                    
  
            
    
     
                    
                    
    
            
              

