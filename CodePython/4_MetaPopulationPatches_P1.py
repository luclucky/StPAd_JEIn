# PART 4-1: Creation 'MPP' - MetaPopulationPatches

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import psycopg2

import pandas as pd

# PostgreSQL DB-Connection

conn = psycopg2.connect("host=139.14.20.252 port=5432 dbname=DB_PhD_03 user=streib_lucas password=1gis!gis1")
cursor = conn.cursor()

#

vsipath = '/vsimem/from_postgis'

# A. MPP-CatchmentArea calculation per PAS

cursor.execute("""CREATE SCHEMA IF NOT EXISTS ca;""") # 'ca' - CatchmentArea

conn.commit()

# StreamNetwork LineSegments 'sn_lns_mlt' & LineNodes 'sn_lns_mlt_pts' + specific IDs

cursor.execute("""CREATE TABLE ca.sn_lns_mlt AS SELECT ST_Multi((ST_Dump(ST_Multi(geom))).geom) AS geom FROM gd.sn_lns;""")

cursor.execute("""ALTER TABLE ca.sn_lns_mlt ADD COLUMN line SERIAL;""") # add Line IDs

cursor.execute("""CREATE TABLE ca.sn_lns_mlt_pts AS SELECT (ST_DumpPoints(geom)).geom, line, (ST_DumpPoints(geom)).path[2] AS position FROM ca.sn_lns_mlt;""") # create LineNodes (pts) + Line ID + LineNodePosition

# Add PAS IDs 'pts_ids_org' to (intersecting) LineNodes 'sn_lns_mlt_pts'

cursor.execute("""ALTER TABLE ca.sn_lns_mlt_pts ADD COLUMN pts_ids_org INT;""")
cursor.execute("""UPDATE ca.sn_lns_mlt_pts SET pts_ids_org = 0;""")

conn.commit()

pas = 10  # Number of PAS: 'pas' - PatchArrangementScenarios

for x in range(pas):

    cursor.execute("""UPDATE ca.sn_lns_mlt_pts AS l SET pts_ids_org = p.ids_org FROM (SELECT * FROM pas.pas"""+str(x)+""") AS p WHERE ST_Intersects(p.geom, l.geom);""")

conn.commit()

# DataFrame 'DF_pts_TC': 'line' - LineID | 'position' - LineNodePosition | 'X' 'Y' - XY-Coordinates

cursor.execute("""SELECT line, position, pts_ids_org, ST_X(geom) AS X, ST_Y(geom) AS Y FROM ca.sn_lns_mlt_pts;""")
pts = cursor.fetchall()
pts = [y for y in pts]
pts = np.round_(pts, decimals=1)

DF_pts = pd.DataFrame(data=pts)
DF_pts_TC = DF_pts[DF_pts[2].notna()].sort_values(by=[2], ascending=False).reset_index(drop=True) # ;sort 'DF_pts' descending by PAS ID, i.e. 'pts_ids_org'

# 'ca.pas_pts_ca': UpstreamCatchment (Polygon) per PAS Point

cursor.execute("""CREATE TABLE ca.pas_pts_ca(pts_ids_org serial, geom geometry);""")
conn.commit()

for x in range(len(DF_pts_TC)): # Loop over all PAS Points

    if DF_pts_TC.iloc[x,2] == 0:

        break

    else:

        # Identify UpstreamNodes of MainLine for PAS Point

        DF_pts_TC_x = DF_pts[(DF_pts[0] == DF_pts_TC.iloc[x,0]) & (DF_pts[1] < DF_pts_TC.iloc[x,1])].append(DF_pts_TC.iloc[x]).sort_values(by=[1], ascending=False).reset_index(drop=True)

        # Calculate (Line)Distance 'dist' of UpstreamNodes to PAS Point

        DF_pts_TC_x[5] = np.nan

        DF_pts_TC_x.iloc[0,5] = 0

        disT = 0

        for xx in range(len(DF_pts_TC_x)-1):

            disT = np.sqrt((DF_pts_TC_x.iloc[xx,3] - DF_pts_TC_x.iloc[xx+1,3]) ** 2 + (DF_pts_TC_x.iloc[xx,4] - DF_pts_TC_x.iloc[xx+1,4]) ** 2)

            DF_pts_TC_x.iloc[xx+1,5] = DF_pts_TC_x.iloc[xx,5] + disT

        # Remove UpstreamNodes with 'dist' >= 10000m

        if DF_pts_TC_x[5].max() > 10000:

            inD = DF_pts_TC_x[DF_pts_TC_x[5].gt(10000)].index[0] + 1

            DF_pts_TC_x_lin = DF_pts_TC_x[:inD]

        else:

            DF_pts_TC_x_lin = DF_pts_TC_x

        # Add UpstreamNode of intersecting SideLines by identical XY to UpstreamNodes of MainLine to 'DF_pts_TC_x_lin' + (Line)Distance based on intersecting MainLineNode

        DF_pts_TC_x_lin_add = DF_pts[DF_pts.index.isin(pd.merge(DF_pts.iloc[:, 3:5].reset_index(), DF_pts_TC_x_lin.iloc[:, 3:5], how='inner').set_index('index').index)]

        if len(DF_pts_TC_x_lin_add[DF_pts_TC_x_lin_add[0] != DF_pts_TC.iloc[x, 0]]) != 0:

            DF_pts_TC_x_lin_add = DF_pts_TC_x_lin_add[DF_pts_TC_x_lin_add[0] != DF_pts_TC.iloc[x,0]].reset_index(drop=True)
            DF_pts_TC_x_lin_add[5] = np.nan

            DF_pts_TC_x_lin_add.set_index([3,4], inplace=True)
            DF_pts_TC_x_lin_add[5].update(DF_pts_TC_x_lin.set_index([3,4])[5])
            DF_pts_TC_x_lin_add = DF_pts_TC_x_lin_add.reset_index()

            DF_pts_TC_x_lin_add = DF_pts_TC_x_lin_add.reindex(sorted(DF_pts_TC_x_lin_add.columns), axis=1)

            DF_pts_TC_x_lin = pd.concat([DF_pts_TC_x_lin, DF_pts_TC_x_lin_add]).reset_index(drop=True)

            # Add (all) UpstreamNodes of (all) SideLines to 'DF_pts_TC_x_lin' + calculate (Line)Distance to PAS point

            while len(DF_pts_TC_x_lin_add) > 0:

                for xxx in range(len(DF_pts_TC_x_lin_add)):

                    DF_pts_TC_add_xx = DF_pts[(DF_pts[0] == DF_pts_TC_x_lin_add.iloc[xxx,0]) & (DF_pts[1] < DF_pts_TC_x_lin_add.iloc[xxx,1])].append(DF_pts_TC_x_lin_add.iloc[xxx]).sort_values(by=[1], ascending=False).reset_index(drop=True)

                    for xxxx in range(len(DF_pts_TC_add_xx) - 1):

                        # Calculate (Line)Distance 'dist' of UpstreamNodes to PAS Point

                        disT = np.sqrt((DF_pts_TC_add_xx.iloc[xxxx, 3] - DF_pts_TC_add_xx.iloc[xxxx + 1, 3]) ** 2 + (DF_pts_TC_add_xx.iloc[xxxx, 4] - DF_pts_TC_add_xx.iloc[xxxx + 1, 4]) ** 2)

                        DF_pts_TC_add_xx.iloc[xxxx + 1, 5] = DF_pts_TC_add_xx.iloc[xxxx, 5] + disT

                    # Remove UpstreamNodes with 'dist' >= 10000m

                    if DF_pts_TC_add_xx[5].max() > 10000:

                        inD = DF_pts_TC_add_xx[DF_pts_TC_add_xx[5].gt(10000)].index[0] + 1

                        DF_pts_TC_x_lin_xx = DF_pts_TC_add_xx[:inD]

                    else:

                        DF_pts_TC_x_lin_xx = DF_pts_TC_add_xx

                    DF_pts_TC_x_lin = pd.concat([DF_pts_TC_x_lin, DF_pts_TC_x_lin_xx[1:]]).reset_index(drop=True)

                # 'DF_pts_TC_x_lin' : DataFrame including all LineNodes of UpstreamLineNetwork <= 10000m for PAS Point

                xy = DF_pts[DF_pts.index.isin(pd.merge(DF_pts.iloc[:,3:5].reset_index(), DF_pts_TC_x_lin.iloc[:,3:5], how='inner').set_index('index').index)]

                DF_pts_TC_x_lin_add = pd.concat([xy, DF_pts_TC_x_lin.iloc[:,0:5], DF_pts_TC_x_lin.iloc[:,0:5]]).drop_duplicates(keep=False).reset_index(drop=True)

                DF_pts_TC_x_lin_add = pd.merge(DF_pts_TC_x_lin_add, DF_pts_TC_x_lin, left_on=[3,4], right_on = [3,4]).iloc[:,[0,1,2,3,4,8]]
                DF_pts_TC_x_lin_add.columns = [0,1,2,3,4,5]

                DF_pts_TC_x_lin = pd.concat([DF_pts_TC_x_lin, DF_pts_TC_x_lin_add]).reset_index(drop=True)

        # 'comb_LP': DataFrame 'DF_pts_TC_x_lin' reduced to DB Table 'ca.sn_lns_mlt_pts' 'line' (LineID) & 'position' (LineNodePosition)

        comb_LP = DF_pts_TC_x_lin.iloc[:,0:2].values.astype(int)

        #  'comb_LP' UpstreamLineNetwork buffered by 100m rsp. UpstreamCatchement of PAS Point to DB Table 'ca.pas_pts_ca'

        cursor.execute("""INSERT INTO ca.pas_pts_ca(pts_ids_org, geom) VALUES ("""+str(DF_pts_TC.iloc[x,2])+""", (SELECT ST_Union(buf.geom) AS geom FROM (SELECT ST_Buffer(ST_MakeLine(linS.geom),100) AS geom FROM (SELECT * FROM ca.sn_lns_mlt_pts WHERE (line, position) IN ("""+str(np.array(comb_LP).tolist())[1:-1].replace('[', '(').replace(']', ')')+""") ORDER BY line, POSITION) AS linS GROUP BY linS.line) AS buf));""")

        conn.commit()

cursor.execute("""CREATE TABLE ca.pas_pts_ca_niq AS SELECT DISTINCT * FROM ca.pas_pts_ca;""")

conn.commit()
