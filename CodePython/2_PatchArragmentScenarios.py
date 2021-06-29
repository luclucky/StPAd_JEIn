# PART 2: 'PAS' - PatchArrangementScenarios

# Packages

import random

import psycopg2

# PostgreSQL DB-Connection

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

# A. Euclidean distance calculation between all ( less 2500 m) 'pas_pts', outTable 'pas_pts_ed' if less 2500 m: 'pas_pts' - PatchArrangementScenario Points, i.e. all eligible; 'pas_pts_ed' -  PatchArrangementScenario Points EuclideanDistance

cursor.execute("""CREATE TABLE gd.pas_pts_ed (start int, start_xy text, aim int, aim_xy text, geom geometry, distance float);""")
conn.commit()

cursor.execute("""SELECT ids FROM gd.pas_pts""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:

    cursor.execute("""INSERT INTO gd.pas_pts_ed SELECT a.ids AS start, ST_AsText(a.geom) AS start_xy, b.ids AS aim, ST_AsText(b.geom) AS aim_xy, ST_makeline(a.geom, b.geom) AS geom, ST_Distance(a.geom, b.geom) AS distance FROM (SELECT * FROM gd.pas_pts WHERE ids = """+str(x)+""") a, (SELECT * FROM gd.pas_pts WHERE ST_DWithin(geom, (SELECT geom FROM gd.pas_pts WHERE ids = """+str(x)+"""), 2500)) b WHERE a.ids <> b.ids;""")

    conn.commit()

cursor.execute("""ALTER TABLE gd.pas_pts_ed SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")
conn.commit()

# B. Creation random PAS

# Parameters

pas = 10 # Number of PAS: 'pas' PatchArrangementScenarios

mpp_p = 0.2 # Proportion of 'gd.pas_pts' eligible as MPP: 'mpp' - MetaPopulationPatches; 'p' - Proportion

#

cursor.execute("""CREATE SCHEMA IF NOT EXISTS pas;""")
conn.commit()

# PatchArrangementScenario Points: IDS | XY-Coordinates

cursor.execute("""SELECT ids, ST_AsText(geom) FROM gd.pas_pts;""")

pts =  cursor.fetchall()

pts = [list(y) for y in pts]

pts = [[int(y[0]),[float(y[1].split(' ',1)[0][6:]), float(y[1].split(' ',1)[1][:-1])]] for y in pts]

pts_IDS = [int(y[0]) for y in pts]
pts_X = [float(y[1][0]) for y in pts]
pts_Y = [float(y[1][1]) for y in pts]
pts_XY = [y[1] for y in pts]

# random Selection of PAS + corresponding PAS_ed: 'pas_ed' - PatchArrangementScenario EuclidianDistance

for x in range(pas): # Iterate over PAS

    # PAS

    pts_pas = random.sample(pts_IDS, int(len(pts_IDS)*mpp_p+0.5))

    cursor.execute("""CREATE TABLE pas.pas"""+str(x)+""" AS SELECT * FROM gd.pas_pts WHERE ids IN ("""+str(pts_pas)[1:-1]+""");""")

    cursor.execute("""ALTER TABLE pas.pas"""+str(x)+""" RENAME COLUMN ids TO ids_org;""")

    cursor.execute("""ALTER TABLE pas.pas"""+str(x)+""" ADD column ids bigserial;""")

    cursor.execute("""ALTER TABLE pas.pas"""+str(x)+""" SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")

    conn.commit()

    # PAS_ed

    cursor.execute("""SELECT ids_org FROM pas.pas"""+str(x)+""";""")

    ids = cursor.fetchall()
    ids = [int(y[0]) for y in ids]

    cursor.execute("""CREATE TABLE pas.pas"""+str(x)+"""_ed AS SELECT * FROM gd.pas_pts_ed WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")

    cursor.execute("""UPDATE pas.pas"""+str(x)+"""_ed a SET start = ids FROM pas.pas"""+str(x)+""" b WHERE a.start = b.ids_org;""")

    cursor.execute("""UPDATE pas.pas"""+str(x)+"""_ed a SET aim = ids FROM pas.pas"""+str(x)+""" b WHERE a.aim = b.ids_org;""")

    # see https://www.postgresql.org/docs/11/runtime-config-autovacuum.html

    cursor.execute("""ALTER TABLE pas.pas"""+str(x)+"""_ed SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")

    conn.commit()

cursor.close()
conn.close()
