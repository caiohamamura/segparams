#!/usr/bin/env python
#******************************************************************************
#  $Id: gdal_polygonize.py 19392 2010-04-12 18:27:09Z rouault $
# 
#  Project:  GDAL Python Interface
#  Purpose:  Application for converting raster data to a vector polygon layer.
#  Author:   Frank Warmerdam, warmerdam@pobox.com
# 
#******************************************************************************
#  Copyright (c) 2008, Frank Warmerdam
# 
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#******************************************************************************
from subprocess import call
from ctypes import cdll
import ctypes
import os
global baatz, bins, float2
float2 = str
try:
    seg = cdll.LoadLibrary("win64\\TePDISegmentation.dll")
except:
    seg = cdll.LoadLibrary("win32\\TePDISegmentation.dll")
baatz=seg.TeBaatz
bins=seg.TeBins
# =========================================================================
# POLYGONIZE
# =========================================================================    
def polygonize(src_filename, dst_filename):
    try:
        from osgeo import gdal, ogr, osr
    except ImportError:
        import gdal, ogr, osr
    
    import sys
    import os.path
    from glob import glob
    from os import remove
    
    for filename in glob(dst_filename[0:len(dst_filename)-4]+"*"):
        if filename[-3:] != "tif":
            remove(filename)
    
    def Usage():
        print("""
    gdal_polygonize [-o name=value] [-nomask] [-mask filename] raster_file [-b band]
                    [-q] [-f ogr_format] out_file [layer] [fieldname]
    """)
        sys.exit(1)
    
    # =============================================================================
    # 	Mainline
    # =============================================================================
    
    format = 'ESRI Shapefile'
    options = []
    quiet_flag = 0
    src_band_n = 1
    
    dst_layername = None
    dst_fieldname = None
    dst_field = -1
    
    mask = 'default'
    
    gdal.AllRegister()
    
    if src_filename is None or dst_filename is None:
        Usage()
    
    if dst_layername is None:
        dst_layername = 'out'
        
    # =============================================================================
    # 	Verify we have next gen bindings with the polygonize method.
    # =============================================================================
    try:
        gdal.Polygonize
    except:
        print('')
        print('gdal.Polygonize() not available.  You are likely using "old gen"')
        print('bindings or an older version of the next gen bindings.')
        print('')
        sys.exit(1)
    
    # =============================================================================
    #	Open source file
    # =============================================================================
    
    src_ds = gdal.Open( src_filename )
        
    if src_ds is None:
        print('Unable to open %s' % src_filename)
        sys.exit(1)
    
    srcband = src_ds.GetRasterBand(src_band_n)
    
    if mask is 'default':
        maskband = srcband.GetMaskBand()
    elif mask is 'none':
        maskband = None
    else:
        mask_ds = gdal.Open( mask )
        maskband = mask_ds.GetRasterBand(1)
    
    # =============================================================================
    #       Try opening the destination file as an existing file.
    # =============================================================================
    
    try:
        gdal.PushErrorHandler( 'QuietErrorHandler' )
        dst_ds = ogr.Open( dst_filename, update=1 )
        gdal.PopErrorHandler()
    except:
        dst_ds = None
    
    # =============================================================================
    # 	Create output file.
    # =============================================================================
    if dst_ds is None:
        drv = ogr.GetDriverByName(format)
        if not quiet_flag:
            print('Creating output %s of format %s.' % (dst_filename, format))
        dst_ds = drv.CreateDataSource( dst_filename )
    
    # =============================================================================
    #       Find or create destination layer.
    # =============================================================================
    try:
        dst_layer = dst_ds.GetLayerByName(dst_layername)
    except:
        dst_layer = None
    
    if dst_layer is None:
    
        srs = None
        if src_ds.GetProjectionRef() != '':
            srs = osr.SpatialReference()
            srs.ImportFromWkt( src_ds.GetProjectionRef() )
            
        dst_layer = dst_ds.CreateLayer(dst_layername, srs = srs )
    
        if dst_fieldname is None:
            dst_fieldname = 'DN'
            
        fd = ogr.FieldDefn( dst_fieldname, ogr.OFTInteger )
        dst_layer.CreateField( fd )
        dst_field = 0
    else:
        if dst_fieldname is not None:
            dst_field = dst_layer.GetLayerDefn().GetFieldIndex(dst_fieldname)
            if dst_field < 0:
                print("Warning: cannot find field '%s' in layer '%s'" % (dst_fieldname, dst_layername))
    
    # =============================================================================
    #	Invoke algorithm.
    # =============================================================================
    
    if quiet_flag:
        prog_func = None
    else:
        prog_func = gdal.TermProgress
        
    result = gdal.Polygonize( srcband, maskband, dst_layer, dst_field, options,
                            callback = prog_func )
        
    srcband = None
    src_ds = None
    dst_ds = None
    mask_ds = None
    
def SegBaatz(src_filename, dst_filename, scale, compactness, color, w1, w2, w3):
    baatz(src_filename, dst_filename, float2(scale), float2(compactness), float2(color), float2(w1), float2(w2), float2(w3))
    polygonize(dst_filename+'.tif', dst_filename+".shp")