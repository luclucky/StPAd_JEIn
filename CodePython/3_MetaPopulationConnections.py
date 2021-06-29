# PART 3: Creation 'MPC' - MetaPoppulationConnections

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import gdal

import psycopg2

from skimage.graph import route_through_array

# Functions

def ind_to_Xcoord(ind_x): # X-Coordinate from X-PixelIndex

    coord_x = ind_x * cr_gt[1] + cr_gt[0] + cr_gt[1]/2

    return(coord_x)

def ind_to_Ycoord(ind_y):  # Y-Coordinate from Y-PixelIndex

    coord_y = ind_y * cr_gt[5] + cr_gt[3] + cr_gt[5]/2

    return(coord_y)

# PostgreSQL DB-Connection

conn = psycopg2.connect("host=139.14.20.252 port=5432 dbname=DB_PhD_03 user=streib_lucas password=1gis!gis1")
cursor = conn.cursor()

# http://www.postgis.net/docs/manual-dev/postgis_gdal_enabled_drivers.html

cursor.execute("""SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';""")
conn.commit()

#

cursor.execute("""CREATE SCHEMA IF NOT EXISTS mpc;""")
conn.commit()

pas = 10  # Number of PAS: 'pas' - PatchArrangementScenarios

for x in range(pas):

    cursor.execute("""SELECT start, start_xy, aim, aim_xy, distance FROM pas.pas"""+str(x)+"""_ed;""")

    pas_ed = cursor.fetchall()

    pas_ed = [list(y) for y in pas_ed]

    pas_ed = [[y[0],[float(y[1].split(' ',1)[0][6:]), float(y[1].split(' ',1)[1][:-1])],y[2],[float(y[3].split(' ',1)[0][6:]), float(y[3].split(' ',1)[1][:-1])], y[4]] for y in pas_ed]

    p_con = [[y[2], y[0]]for y in pas_ed],[[y[0], y[2]]for y in pas_ed] # Patches connected: 'p_con' - Patches CONnected

    for xx in range(int(len(p_con[0])/2)): # Remove equal, opposite Connections from 'pas_ed', e.g. 4-6 & 6-4

        y = p_con[0][xx]

        for z in range(len(p_con[0])):

            yy = p_con[1][z]

            if yy == y:

                p_con[0].pop(z)
                p_con[1].pop(z)
                pas_ed.pop(z)
                break

    vsipath = '/vsimem/from_postgis'

    cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM lus.osm_rs;""")

    gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

    cost_raster = gdal.Open(vsipath)

    gdal.Unlink(vsipath)

    cr_array = cost_raster.ReadAsArray()
    cr_array = cr_array * 25.0 # DC raster * DC

    cr_gt = cost_raster.GetGeoTransform()

    cursor.execute("""DROP TABLE IF EXISTS mpc.pas"""+str(x)+""";""")

    cursor.execute("""CREATE TABLE mpc.pas"""+str(x)+""" (start bigint, aim bigint, geom geometry, costs double precision);""")

    for xx in range(len(pas_ed)): # Processing START, AIM, GEOMETRY, COSTS per MPC

        start_x = int((pas_ed[xx][1][0] - cr_gt[0]) / cr_gt[1]) # START: X Coordinate to Index
        start_y = int((pas_ed[xx][1][1] - cr_gt[3]) / cr_gt[5]) # START: Y Coordinate to Index

        aim_x = int((pas_ed[xx][3][0] - cr_gt[0]) / cr_gt[1]) # AIM: X Coordinate to Index
        aim_y = int((pas_ed[xx][3][1] - cr_gt[3]) / cr_gt[5]) # AIM: Y Coordinate to Index

        indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y], fully_connected=True)

        indices = np.array(indices).T # PixelIndex

        coor = []

        mpc_nodes = ""

        for xxx in range(len(indices[0])):

            coor.append([ind_to_Xcoord(indices[0][xxx]), ind_to_Ycoord(indices[1][xxx])]) # PixelIndex to Coordinate

            mpc_nodes = mpc_nodes + "ST_MakePoint("+str(coor[xxx][0]) + ', ' + str(coor[xxx][1])+"),"

        mpc_nodes = mpc_nodes[:-1]

        cursor.execute("""INSERT INTO mpc.pas"""+str(x)+""" (start, aim, geom, costs) VALUES ("""+str(pas_ed[xx][0])+""", """+str(pas_ed[xx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mpc_nodes)+"""]), 25832), """+str(weight)+""");""")

        cursor.execute("""UPDATE mpc.pas"""+str(x)+""" SET costs = 50 WHERE costs = 0;""")
        conn.commit()

cursor.close()
conn.close()
