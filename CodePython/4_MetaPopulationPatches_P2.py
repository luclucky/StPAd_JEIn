# PART 4-2: Creation 'MPP' - MetaPopulationPatches

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import psycopg2

import pandas as pd

# PostgreSQL DB-Connection

conn = psycopg2.connect("host=139.14.20.252 port=5432 dbname=DB_PhD_03 user=streib_lucas password=1gis!gis1")
cursor = conn.cursor()

cursor.execute("""CREATE SCHEMA IF NOT EXISTS mpp;""")
conn.commit()

pas = 10  # PatchArragmentScenarios

for x in range(pas):

    # 'pts_df':  PixelAmount of LT 2, 3 & 4 of LUS-Raster in CatchmentArea per PAS Point (ID 'pts_id')

    cursor.execute("""SELECT pts_id, (cnts).value, (cnts).count FROM (SELECT pts_id, geom, ST_ValueCount(ST_Clip(rast,ca)) AS cnts FROM (SELECT rast FROM lus.osm) AS rastER, (SELECT ids AS pts_id, pts.geom, ca.geom AS ca FROM ca.pas_pts_ca_niq AS ca, pas.pas""" +str(x) + """ AS pts WHERE ca.pts_ids_org IN (pts.ids_org)) AS HP) AS rasT_cnTs WHERE (cnts).value > 1;""")

    pts = cursor.fetchall()
    pts = [y for y in pts]

    pts_df = pd.DataFrame(pts)
    pts_df = pts_df.sort_values(0)

    # Calculation of PAS Point Quality based on the LT 4 Share

    A_LT4 = pts_df.loc[pts_df[1] == 4.0].groupby(0)[2].sum()

    A_LT2 = pts_df.loc[pts_df[1] == 2.0].groupby(0)[2].sum()
    A_LT2 = A_LT2 * 0.5

    A_LTn = A_LT2.add(A_LT4, fill_value=0)

    A_B = pts_df.groupby(0)[2].sum()

    HQ_pts = np.round(1 - (A_LTn / A_B), decimals=2).tolist()

    if sum(np.isnan(HQ_pts)) > 0:
        HQ_pts = np.array(HQ_pts)
        HQ_pts[np.where(np.isnan(HQ_pts))[0]] = 1

    ID_pts = pd.unique(pts_df[0])

    toINS = np.stack((ID_pts, HQ_pts), axis=-1)

    # Create DB Table 'mpp' MetaPopulationPatches for every PAS & LUS combination

    cursor.execute("""CREATE TABLE IF NOT EXISTS mpp.pas""" +str(x) + """ AS SELECT pts_id, geom FROM (SELECT ids AS pts_id, geom FROM pas.pas"""+str(x)+""") AS pts;""")

    cursor.execute("""ALTER TABLE mpp.pas""" +str(x) + """ ADD COLUMN hq FLOAT DEFAULT 0.0;""")

    # Add 'hq' Habitat Quality (specified by PAS & LUS) to MPP Points

    if len(toINS) > 0:
        cursor.execute("""UPDATE mpp.pas""" +str(x) + """ AS zxy SET hq = xyz.hq FROM (SELECT * FROM (VALUES """+str(np.array(toINS).tolist())[1:-1].replace('[', '(').replace(']', ')').replace('\'', '')+""") AS t(pts_id, hq)) AS xyz WHERE zxy.pts_id = xyz.pts_id;""")

    # see https://www.postgresql.org/docs/11/runtime-config-autovacuum.html

    cursor.execute("""ALTER TABLE mpp.pas""" +str(x) + """ SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")

    conn.commit()

cursor.close()
conn.close()
