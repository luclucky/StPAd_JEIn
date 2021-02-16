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

conn = psycopg2.connect("host=139.14.20.252 port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")
cursor = conn.cursor()

# http://www.postgis.net/docs/manual-dev/postgis_gdal_enabled_drivers.html

cursor.execute("""SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';""")

conn.commit()

vsipath = '/vsimem/from_postgis'

# Raster MetaData: Dimensions | Cell Size

cursor.execute("""SELECT ST_MetaData(rast) As md FROM gd.sn_ras;""")
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

# 'gd.sn_ras' to Array - 'gd.sn_ras': schema 'gd' - GeoData; table 'sn_ras' - StreamNetwork Raster

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM gd.sn_ras;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
STREAM01_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM gd_p3.osm_lu_rst;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
LU_ARRAY = band.ReadAsArray()

np.place(LU_ARRAY, STREAM01_ARRAY == 1, 1)

P2s = 0.5 # P2s :=

FLidx  = np.dstack(np.where(LU_ARRAY == 0)).tolist()[0] # FLidx := FarmLand Pixel Indices

FLnP = len(fl_idx) # FLnP := FarmLand Number of Pixel

np.random.choice(FLnP, int(FLnP*P2s)).tolist()

np.random.choice(len(fl_idx), len(fl_idx)/2)

# Parameters

LTpro = [[[1], 1], [[.5, .25, .25], 1], [[.5, .5], 2], [[1], 2], [[.25, .5, .25], 1], [[.5, 0, .5], 1], [[1], 3], [[.25, .25, .5], 1],  [[.5, .5, 0], 1]] # Proportion terrestrial LT (1,2,3): 'LT' - LanduseTypes

nlm = 10 # Number of LUS per LTpro & NLM algorithm: 'LUS' - LandUseScenarios; 'NLM' - Neutral Landscape Model (see https://besjournals.onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2F2041-210X.12308&file=mee312308-sup-0001-dataS1.pdf)

outSs = ['lus_100000000', 'lus_050025025', 'lus_000050050', 'lus_000100000', 'lus_025050025', 'lus_050000050', 'lus_000000100', 'lus_025025050', 'lus_050050000'] # Output-Schemas

wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]' # 'CRS' - Coordinate Reference System (see https://docs.geotools.org/stable/javadocs/org/opengis/referencing/doc-files/WKT.html)




for x in range(len(LTpro)):

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """ + str(outSs[x]) + """;""")
    conn.commit()

    for xx in range(nlm):

        # Parameters for NLM 'random'

        nlm_R = nlmpy.random(int(nROW), int(nCOL))
        nlm_R = (nlmpy.classifyArray(nlm_R, LTpro[x][0]) + 1) + LTpro[x][1]
        np.place(nlm_R, STREAM01_ARRAY == 1, 1)

        # Parameters for NLM 'random element'

        nlm_RE = nlmpy.randomElementNN(int(nROW), int(nCOL), 1000 * 25)
        nlm_RE = (nlmpy.classifyArray(nlm_RE, LTpro[x][0]) + 1) + LTpro[x][1]
        np.place(nlm_RE, STREAM01_ARRAY == 1, 1)

        # Parameters for NLM 'random cluster'

        nlm_RC = nlmpy.randomClusterNN(int(nROW), int(nCOL), .3825, n='8-neighbourhood')
        nlm_RC = (nlmpy.classifyArray(nlm_RC, LTpro[x][0]) + 1) + LTpro[x][1]
        np.place(nlm_RC, STREAM01_ARRAY == 1, 1)

        ###

        # Raster-Creation & DB-Import

        ## NLM 'random'

        ### Creation raster

        dst_filename = '/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_2nd/LUS/nlm_R.tiff' # Link to store '.tif'-File; Folder has to be created

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

        dataset.GetRasterBand(1).WriteArray(nlm_R)
        dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_R), np.amax(nlm_R), np.mean(nlm_R), np.std(nlm_R))
        dataset.GetRasterBand(1).SetNoDataValue(-999)

        dataset.FlushCache()

        raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

        raster_array = raster.ReadAsArray()

        cmds = 'gdal_calc.py -A "' + dst_filename + '" --outfile="' + dst_filename[:-5] + '_reclas.tif" --calc="(A==4)*2+(A!=4)*A" ' # convert LT raster to DC raster, i.e. LT4 to LT2; 'DC' - DispersalCost
        subprocess.call(cmds, shell=True)

        cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename[:-5] + '_reclas.tif" "' + dst_filename[:-5] + '_rs.tif" -overwrite' # resampe DC raster to 100x100m cell-size
        subprocess.call(cmds, shell=True)

        ## DB-Import

        os.environ['PGPASSWORD'] = '1gis!gis1'

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F ' + str(outSs[x]) + '.nlmr' + str(xx) + ' | psql -d DB_PhD -h 139.14.20.252 -U streib_lucas '
        subprocess.call(cmds, shell=True)

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_rs.tif" -F ' + str(outSs[x]) + '.nlmr' + str(xx) + '_rs | psql -d DB_PhD -h 139.14.20.252 -U streib_lucas '
        subprocess.call(cmds, shell=True)

        ## NLM 'random cluster'

        ### Creation raster

        dst_filename = '/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_2nd/LUS/nlm_Rc.tiff'

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
        dataset.GetRasterBand(1).WriteArray(nlm_RC)

        dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RC), np.amax(nlm_RC), np.mean(nlm_RC), np.std(nlm_RC))
        dataset.GetRasterBand(1).SetNoDataValue(-999)

        print(dataset.GetRasterBand(1).ReadAsArray())

        dataset.FlushCache()

        raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

        raster_array = raster.ReadAsArray()

        cmds = 'gdal_calc.py -A "' + dst_filename + '" --outfile="' + dst_filename[:-5] + '_reclas.tif" --calc="(A==4)*2+(A!=4)*A" '
        subprocess.call(cmds, shell=True)

        cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename[:-5] + '_reclas.tif" "' + dst_filename[:-5] + '_rs.tif" -overwrite'
        subprocess.call(cmds, shell=True)

        ## DB-Import

        os.environ['PGPASSWORD'] = '1gis!gis1'

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F ' + str(outSs[x]) + '.nlmrc' + str(xx) + ' | psql -d DB_PhD -h 139.14.20.252 -U streib_lucas '
        subprocess.call(cmds, shell=True)


        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_rs.tif" -F ' + str(outSs[x]) + '.nlmrc' + str(xx) + '_rs | psql -d DB_PhD -h 139.14.20.252 -U streib_lucas '
        subprocess.call(cmds, shell=True)

        # Raster-Creation & DB-Import

        ## NLM 'random element'

        ### Creation raster

        dst_filename = '/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_2nd/LUS/nlm_RE.tiff'

        driver = gdal.GetDriverByName('GTiff')

        dataset = []

        dataset = driver.Create(dst_filename,
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

        dataset.FlushCache()  # Write to disk.

        dataset.SetProjection(wkt_projection)
        dataset.GetRasterBand(1).WriteArray(nlm_RE)

        dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RE), np.amax(nlm_RE), np.mean(nlm_RE), np.std(nlm_RE))
        dataset.GetRasterBand(1).SetNoDataValue(-999)

        print(dataset.GetRasterBand(1).ReadAsArray())

        dataset.FlushCache()

        raster = gdal.Open(dst_filename, gdal.GA_ReadOnly)

        raster_array = raster.ReadAsArray()

        cmds = 'gdal_calc.py -A "' + dst_filename + '" --outfile="' + dst_filename[:-5] + '_reclas.tif" --calc="(A==4)*2+(A!=4)*A" '
        subprocess.call(cmds, shell=True)

        cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename[:-5] + '_reclas.tif" "' + dst_filename[:-5] + '_rs.tif" -overwrite'
        subprocess.call(cmds, shell=True)

        ## DB-Import

        os.environ['PGPASSWORD'] = '1gis!gis1'

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F ' + str(outSs[x]) + '.nlmre' + str(xx) + ' | psql -d DB_PhD -h 139.14.20.252 -U streib_lucas '
        subprocess.call(cmds, shell=True)

        cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_rs.tif" -F ' + str(outSs[x]) + '.nlmre' + str(xx) + '_rs | psql -d DB_PhD -h 139.14.20.252 -U streib_lucas '
        subprocess.call(cmds, shell=True)

cursor.close()
conn.close()
