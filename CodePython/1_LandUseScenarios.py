# PART 1: Creation 'LUS' - LandUseScenarios

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import gdal

import os

import psycopg2

import subprocess

from nlmpy import nlmpy

# PostgreSQL DB-Connection

conn = psycopg2.connect("host=139.14.20.252 port=5432 dbname=DB_PhD_03 user=streib_lucas password=1gis!gis1")
cursor = conn.cursor()

# http://www.postgis.net/docs/manual-dev/postgis_gdal_enabled_drivers.html

cursor.execute("""SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';""")

conn.commit()

vsipath = '/vsimem/from_postgis'

# Raster MetaData: Dimensions | Cell Size

cursor.execute("""SELECT ST_MetaData(rast) As md FROM gd.sn_rst;""")
raster_MD = cursor.fetchall()
raster_MD = [float(xx) for xx in raster_MD[0][0][1:-1].split(',')]

nCOL = int(raster_MD[2])
nROW = int(raster_MD[3])
grid = np.zeros((nCOL, nROW))

X_DIM = np.arange(grid.shape[0])
Y_DIM = np.arange(grid.shape[1])

X_ll = raster_MD[0]
Y_ll = raster_MD[1]

cellSIZE = raster_MD[4]

#

ds = band = None
gdal.Unlink(vsipath)

# 'gd.sn_rst' to Array - 'gd.sn_rst': schema 'gd' - GeoData; table 'sn_rst' - StreamNetwork Raster

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM gd.sn_rst;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
STREAM01_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM gd.osm_lu_rst;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
LU_ARRAY = band.ReadAsArray()

# LU_ARRAY cell values to LT-class

np.place(LU_ARRAY, LU_ARRAY == 0, 2)
np.place(LU_ARRAY, LU_ARRAY == 3, 3)
np.place(LU_ARRAY, LU_ARRAY == 4, 4)

np.place(LU_ARRAY, STREAM01_ARRAY == 1, 1)

LU_ARRAY.astype(int)

wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]' # 'CRS' - Coordinate Reference System (see https://docs.geotools.org/stable/javadocs/org/opengis/referencing/doc-files/WKT.html)

# Raster-Creation & DB-Import

## Creation raster

dst_filename = '/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/LUS/OSM.tiff' # Link to store '.tif'-File; Folder has to be created

driver = gdal.GetDriverByName('GTiff')

dataset = []

dataset = driver.Create(
    dst_filename,
    int(nCOL),
    int(nROW),
    1,
    gdal.GDT_Float32)

dataset.SetGeoTransform((
    X_ll,
    cellSIZE,
    0,
    Y_ll,
    0,
    -cellSIZE))

dataset.FlushCache()

dataset.SetProjection(wkt_projection)

dataset.GetRasterBand(1).WriteArray(LU_ARRAY)
dataset.GetRasterBand(1).SetNoDataValue(-999)

dataset.FlushCache()

raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

raster_array = raster.ReadAsArray()

cmds = 'gdal_calc.py -A "' + dst_filename + '" --outfile="' + dst_filename[:-5] + '.tif" ' # convert LT raster to DC raster, i.e. LT4 to LT2; 'DC' - DispersalCost
subprocess.call(cmds, shell=True)

cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename[:-5] + '.tiff" "' + dst_filename[:-5] + '_rs.tif" -overwrite' # resampe DC raster to 100x100m cell-size
subprocess.call(cmds, shell=True)

## DB-Import

os.environ['PGPASSWORD'] = '???'
os.environ['PGPASSWORD'] = '1gis!gis1'

cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F lus.osm | psql -d DB_PhD_03 -h 139.14.20.252 -U streib_lucas '
subprocess.call(cmds, shell=True)

cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_rs.tif" -F lus.osm_rs | psql -d DB_PhD_03 -h 139.14.20.252 -U streib_lucas '
subprocess.call(cmds, shell=True)

cursor.close()
conn.close()
