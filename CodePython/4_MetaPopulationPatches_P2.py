# PART 4-2: Creation 'MPP' - MetaPopulationPatches

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import multiprocessing

import psycopg2

import pandas as pd

def MPP_HQ(outS):

    # PostgreSQL DB-Connection

    conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
    cursor = conn.cursor()

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """+(outS)+""";""")
    conn.commit()

    for nlm in ['nlmr', 'nlmre', 'nlmrc']:

        lus = 10  # PatchArragmentScenarios

        for x in range(lus):

            pas = 10  # PatchArragmentScenarios

            for xx in range(pas):

                # 'pts_df':  PixelAmount of LT 2, 3 & 4 of LUS-Raster in CatchmentArea per PAS Point (ID 'pts_id')

                cursor.execute("""SELECT pts_id, (cnts).value, (cnts).count FROM (SELECT pts_id, geom, ST_ValueCount(ST_Clip(rast,ca)) AS cnts FROM (SELECT rast FROM lus_""" + str(outS[4:]) + """.""" + str(nlm) + str(x) + """) AS rastER, (SELECT ids AS pts_id, pts.geom, ca.geom AS ca FROM ca.pas_pts_ca_niq AS ca, pas.pas""" +str(xx) + """ AS pts WHERE ca.pts_ids_org IN (pts.ids_org)) AS HP) AS rasT_cnTs WHERE (cnts).value > 1;""")

                pts = cursor.fetchall()
                pts = [y for y in pts]

                pts_df = pd.DataFrame(pts)

                # Calculation of PAS Point Quality based on the LT 4 Share

                if sum(pts_df[1] != 4.0) == len(pts_df[1]):
                    HQ_pts = [1.0] * len(pd.unique(pts_df[0]))
                elif sum(pts_df[1] == 4.0) == len(pts_df[1]):
                    HQ_pts = [0.25] * len(pd.unique(pts_df[0]))
                else:
                    HQ_pts = np.round(pts_df.loc[pts_df[1] != 4.0].groupby(0)[2].sum() / pts_df.groupby(0)[2].sum()  * 0.75 + 0.25, decimals=2).tolist()
                    if sum(np.isnan(HQ_pts)) > 0:
                        HQ_pts = np.array(HQ_pts)
                        HQ_pts[np.where(np.isnan(HQ_pts))[0]] = 0.25

                ID_pts = pd.unique(pts_df[0])

                toINS = np.stack((ID_pts, HQ_pts), axis=-1)

                # Create DB Table 'mpp' MetaPopulationPatches for every PAS & LUS combination

                cursor.execute("""CREATE TABLE IF NOT EXISTS """+str(outS) + """.""" + str(nlm) +str(x)  + """_pas""" +str(xx) + """ AS SELECT pts_id, geom FROM (SELECT ids AS pts_id, geom FROM pas.pas"""+str(xx)+""") AS pts;""")

                cursor.execute("""ALTER TABLE """+str(outS) + """.""" + str(nlm) +str(x)  + """_pas""" +str(xx) + """ ADD COLUMN hq FLOAT DEFAULT 0.25;""")

                # Add 'hq' Habitat Quality (specified by PAS & LUS) to MPP Points

                if len(toINS) > 0:
                    cursor.execute("""UPDATE """+str(outS) + """.""" + str(nlm) +str(x)  + """_pas""" +str(xx) + """ AS zxy SET hq = xyz.hq FROM (SELECT * FROM (VALUES """+str(np.array(toINS).tolist())[1:-1].replace('[', '(').replace(']', ')').replace('\'', '')+""") AS t(pts_id, hq)) AS xyz WHERE zxy.pts_id = xyz.pts_id;""")

                # see https://www.postgresql.org/docs/11/runtime-config-autovacuum.html

                cursor.execute("""ALTER TABLE """+str(outS) + """.""" + str(nlm) +str(x)  + """_pas""" +str(xx) + """ SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")

                conn.commit()

    cursor.close()
    conn.close()

# Multiprocessing; see https://docs.python.org/3/library/multiprocessing.html

def main():

    # Parameters

    outSs = ['mpp_000050050', 'mpp_100000000', 'mpp_050000050', 'mpp_000100000', 'mpp_050050000', 'mpp_000000100', 'mpp_050025025', 'mpp_025050025', 'mpp_025025050']  # Output-Schemas

    #

    pool = multiprocessing.Pool(processes=9)
    pool.map(MPP_HQ, outSs)

    pool.close()
    pool.join()

if __name__ in ['__builtin__', '__main__']:
    main()