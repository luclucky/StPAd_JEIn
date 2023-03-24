# PART 5: Simulation 'EESinMPN' - ExtremeEventScenarios in MetaPopualtionNetworks

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import pandas as pd

import psycopg2

from random import *

import multiprocessing

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

# import matplotlib.pyplot as plt
# import matplotlib.cm as cm

from scipy.stats import skewnorm

import random

# Functions

def EMI_SHRsurv(co, co_max): # Share Emigrants Surving Dispersal 'P': Calcualted for all MPC based on DispersalCost 'co' in relation to maximal DispersalCost 'co_max'

    Es = co * 0.0
    Es[np.where(co < co_max)] = (1 - (co[np.where(co < co_max)] / co_max))**2

    return Es

def logGRO(K, N, r, t): # LogarithmicGrowth

    Nt = (K * N) / (N + (K - N) * np.exp(-r*t))

    return Nt

def DENdepEMI_RATE(M, N, K, s): # DensityDependendEmigrationRate

    EmRa = N * M * (N / (K)) **(s+1)
    return EmRa

def EMI_SHRconP(COSTs): #  Share Emigrants per connected Patch: Calcualted based on Connecntions DispersalCosts

    CO_rev = ((COSTs-max(COSTs))*-1+min(COSTs))
    percIND = np.round(CO_rev**3/sum(CO_rev**3),2)

    return percIND            

# Scenarios

## L_S - Land use scenarios

L_c = [0.5] * 25

L_ri = list(np.linspace(0.5,1.0,25)) # ramped increase intensive Agriculture
L_rd = list(np.linspace(0.5,0.0,25))

L_si = [0.5] * 12 + [0.75] + [1.0] * 12
L_sd = [0.5] * 12 + [0.25] + [0.0] * 12

L_S = [L_c, L_ri, L_rd, L_si, L_sd]

## D_S - Drought scenarios

skw = [0,-2.5,-5.0]

D_S = []

mor = list(np.round(np.logspace(np.log(0.1), np.log(10), 100, base=np.exp(1)), 0) * 10)

D_S.append([list(mor), [[0] * 100]])

# import matplotlib.pyplot as plt

# plt.bar(list(range(1,101)), height = mor, color='black', width=-1)
# plt.axis('off')

col = plt.cm.rainbow(np.linspace(0, 1, 2 * 100))[100:]
fig, ax = plt.subplots(1, 1)

for a in skw:

    x = np.linspace(skewnorm.ppf(0.0001, a), skewnorm.ppf(0.9999, a), 100)
    # x = np.linspace(skewnorm.ppf(0.01, a, loc=0, scale=2), skewnorm.ppf(0.99, a, loc=0, scale=2), 100)

    cdf = skewnorm.cdf(x, a)
    pdf = skewnorm.pdf(x, a)

    p = []
    for yy in range(len(cdf)):
        if yy > 0:
            p.append(cdf[yy] - cdf[yy-1])
        else:
            p.append(cdf[yy])

    ax.plot(range(0,100), p, 'r-', lw=5, color=col[0])
    plt.ylim(0,0.035)
    plt.axis('off')

    D_S.append([list(mor), list(cdf)])

conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
cursor = conn.cursor()

cursor.execute("""CREATE SCHEMA IF NOT EXISTS ds;""")
conn.commit()

DS_name = ['Dn','Dl', 'Dm', 'Dh']

cloNAM = ['rep INT']
[cloNAM.append('ts_'+str(x)+' FLOAT') for x in range (75)]
cloNAM = str(cloNAM)[1:-1].replace("'", '')

cloS = ['rep']
[cloS.append('ts_'+str(x)) for x in range (75)]
cloS = str(cloS)[1:-1].replace("'", '')

for x in range(len(D_S)):

    cursor.execute("""CREATE TABLE IF NOT EXISTS ds.""" + str(DS_name[x]) + """ (""" + str(cloNAM) + """);""")
    conn.commit()

    for xx in range(50):

        roW = [xx]

        for xxx in range(75):

            D_S[x][1]

            if DS_name[x] == 'Dn':

                roW.append(0.0)

            else:

                roW.append(random.choices(D_S[x][0], cum_weights=D_S[x][1])[0])

        cursor.execute("""INSERT INTO ds.""" + str(DS_name[x]) + """(""" + str(cloS) + """) VALUES (""" + str(roW)[1:-1] + """)""")

    conn.commit()

# A_F - Evolutionary adaptation

A_F = [1, 0.5, 0.0]

###

COMB = []

for x in L_S:
    for xx in D_S:
        for xxx in A_F:
            COMB.append([x,xx,xxx])

#

LS_name = ['Lc', 'Lrd', 'Lri', 'Lsd', 'Lsi']
DS_name = ['Dn','Dl', 'Dm', 'Dh']
AF_name = ['Ah', 'Am', 'An']

COMB_N = []

for x in LS_name:

    for xx in DS_name:

        for xxx in AF_name:

            n = str(x+'_'+xx+'_'+xxx)

            COMB_N.append([n])


nCOMB = [COMB[x] + COMB_N[x] for x in range(len(COMB))]

# Parameters

# EMI_SHRsurv

co_max = 1250  # DispersalCosts Max

## logGRO

igr = 2.0  # IntrinsicGrowthRate

## DENdepEMI_RATE

m_max = 0.20  # EmigrationRate max per MPP
s = 0.5  # Propensity to Disperse

ts = 75 # TimeSpan

PAS = 10

REP = 10

def dispMODEL(C):

    # PostgreSQL DB-Connection

    conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
    cursor = conn.cursor()

    oS = str('sim_2_'+C[3]).lower()

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """ + str(oS) + """;""")
    conn.commit()

    cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = '""" + str(oS) + """';""")
    procTABs = cursor.fetchall()
    procTABs = [t[0] for t in procTABs]

    # DataFrame DroughtMortality

    cursor.execute("""SELECT * FROM ds.""" + str(C[3].split('_')[1]) + """ ORDER BY rep;""")
    dM = cursor.fetchall()
    dM = np.array(dM)

    for x in range(PAS):

        for xx in range(REP):

            if """pas"""+str(x)+"""_rep"""+str(xx) in procTABs:
                continue

            print(str(C[3])+': pas '+str(x)+' rep '+str(xx))

            cursor.execute("""SELECT pts_id, (cnts).value, (cnts).count FROM (SELECT pts_id, geom, ST_ValueCount(ST_Clip(rast,ca)) AS cnts FROM (SELECT rast FROM lus.osm) AS rastER, (SELECT ids AS pts_id, pts.geom, ca.geom AS ca FROM ca.pas_pts_ca_niq AS ca, pas.pas""" +str(x) + """ AS pts WHERE ca.pts_ids_org IN (pts.ids_org)) AS HP) AS rasT_cnTs;""")

            pts = cursor.fetchall()
            pts = [y for y in pts]

            pts_df = pd.DataFrame(pts)
            pts_df = pts_df.sort_values(0)

            pts_df.rename(columns={0: 'ID', 1: 'LT', 2: 'CNT'}, inplace=True)

            pts_df = pts_df.groupby(['ID','LT']).sum().unstack().stack(dropna=False).fillna(0).reset_index()

            # Calculation of PAS Point Quality based on the LT 4 Share

            A_LT4 = pts_df.loc[pts_df['LT'] == 4.0].groupby('ID')['CNT'].sum()

            A_LT2_b = pts_df.loc[pts_df['LT'] == 2.0].groupby('ID')['CNT'].sum()

            A_B = pts_df.groupby('ID')['CNT'].sum()

            ###

            # DataFrame 'mpc': MetaPopulationConnection Parameters 'start' - LineStart (MPP ID) | 'aim' - LineEnd (MPP ID) | 'costs' - DispersalCost Connection

            cursor.execute("""SELECT start, aim, costs FROM mpc.pas"""+str(x)+""";""")
            mpc = cursor.fetchall()
            mpc = [y for y in mpc if y[2] <= co_max]
            mpc = np.array(mpc, dtype=object).T

            # Table SimulationResults per MPN (MetaPopualtionNetwork ;i.e. PAS&LUS Combination) & EES

            cursor.execute("""CREATE TABLE IF NOT EXISTS """+str(oS)+""".pas"""+str(x)+"""_rep"""+str(xx)+""" AS SELECT pts_id, hq FROM mpp.pas"""+str(x)+""";""")
            conn.commit()

            cursor.execute("""CREATE TABLE IF NOT EXISTS """+str(oS)+""".pas"""+str(x)+"""_rep"""+str(xx)+""" AS SELECT pts_id, hq FROM mpp.pas"""+str(x)+""";""")
            conn.commit()

            # DataFrame 'mpp': MetaPopulationPatches Parameters 'pts_id' - MPP ID | 'hq' - MPP HabitatQuality

            cursor.execute("""SELECT pts_id, hq FROM """+str(oS)+""".pas"""+str(x)+"""_rep"""+str(xx)+""" ORDER BY pts_id;""")
            mpp_IDHQ = cursor.fetchall()
            mpp_IDHQ = np.array(np.array(mpp_IDHQ).T)
            mpp_ID = mpp_IDHQ[0]
            mpp_HQ = mpp_IDHQ[1]

            mpp = np.empty([3, len(mpp_ID)])
            mpp[0] = mpp_ID
            mpp[1] = 1
            mpp[2] =  mpp_HQ * (1 * 100)

            # Share surviving Emmigrants per MPC

            pEs = EMI_SHRsurv(co = mpc[2], co_max = co_max)

            # Simulation per TS (TimeSpan)

            L_M_t = []

            for t in range(ts):

                # Column 't' to store Results per TimeSteps

                cursor.execute("""ALTER TABLE """+str(oS)+""".pas"""+str(x)+"""_rep"""+str(xx)+""" ADD IF NOT EXISTS ts"""+str(t+1)+""" float;""")
                conn.commit()

                # LUS

                if t < 25:
                    A_LT2 = (A_LT2_b * 0.5).astype(int) # Start - Landscape of 50% extensive and intensive agriculture (A_LT2)

                if t >= 25 and t < 50:
                    A_LT2 = (A_LT2_b * C[0][t-25]).astype(int)

                if t >= 50:
                    A_LT2 = (A_LT2_b * C[0][24]).astype(int)

                A_LTn = A_LT2.add(A_LT4, fill_value=0)

                mpp_HQ = np.array(np.round(1 - (A_LTn / A_B), decimals=2))

                # DES

                M_t = dM[xx][t+1]

                L_M_t.append(M_t)

                if len(L_M_t) > 1:

                    M_t = M_t * (1 - np.mean(L_M_t[-6:-1]) * 0.01 * C[2])

                mpp[2] = mpp[2] - M_t
                mpp[2][mpp[2] < 0] = 0.0

                #

                if len(mpp[0][np.where(mpp[2] > 0.0)].astype(int)) == 0: # Stop Simulation if all MPP extinct

                    mpp[1][mpp[2] == 0.0] = 0
                    break

                # Parameters (HQ & N) for MPP colonized

                mpp_c = mpp[0][np.where(mpp[2] > 0.0)].astype(int)

                mpp_c_HQ = mpp_HQ[mpp_c-1]

                mpp_c_POP = mpp[2][mpp_c-1]

                # PopulationGrowth MPP colonized / not extinct

                mpp_c_POP = logGRO(K = mpp_c_HQ*100, N = mpp_c_POP, r = igr, t = 1)

                mpp[2][mpp_c-1] = np.round(mpp_c_POP.astype(float), 3)

                # Dispersal per MPP - Immigration / Recolonization MPPs connected

                for c in range(len(mpp_c)):

                    # 'conP_idx': Index of MPPs connected to (specific) MPP colonized

                    if mpp_c[c] in mpc[0] or mpp_c[c] in mpc[1]:

                        conP_idx = np.hstack(np.array([np.where(mpc[0] == mpp_c[c])[0].tolist(), np.where(mpc[1] == mpp_c[c])[0].tolist()]).flatten()).tolist()
                        conP_idx = [int(y) for y in conP_idx]

                    else:

                        continue

                    # 'conP_cf': MPP connected fully colonized

                    conP_cf = []

                    for cc in conP_idx:

                        if mpc[0][cc] != mpp_c[c]:

                            if mpp[2][mpc[0][cc]-1] >= mpp_HQ[int(mpp[0][mpc[0][cc]-1]-1)]*100:

                                conP_cf.append(cc)

                        else:

                            if mpp[2][mpc[1][cc]-1] >= mpp_HQ[int(mpp[0][mpc[1][cc]-1]-1)]*100:

                                conP_cf.append(cc)

                    # remove 'conP_cf' from 'conP_idx':

                    [conP_idx.remove(cf) for cf in conP_cf]

                    if conP_idx == []:

                        continue

                    # 'mpp_cEMI': Emigrants per MPP

                    mpp_cEMI = DENdepEMI_RATE(M = m_max, N = mpp[2][int(mpp_c[c]-1)], K = mpp_HQ[int(mpp_c[c]-1)]*100, s = s)

                    # Reduce MPP Population by 'mpp_cEMI'

                    mpp[2][int(mpp_c[c]-1)] = mpp[2][int(mpp_c[c]-1)] - mpp_cEMI

                    # 'mpp_cEMI_SHRconP': Share 'mpp_cEMI' per MPP connected

                    mpp_cEMI_SHRconP = EMI_SHRconP(COSTs = mpc[2][conP_idx].astype(float))

                    # Adjust MPP connected

                    for ccc in conP_idx:

                        mpp_cEMI_IMIconP = mpp_cEMI * mpp_cEMI_SHRconP[0] # potential Immigrants to MPP connected

                        mpp_cEMI_SHRconP = mpp_cEMI_SHRconP[1:]

                        mpp_cEMI_IMIconP = mpp_cEMI_IMIconP * pEs[ccc] # reduce Immigrants by DispersalMortality

                        if mpp_cEMI_IMIconP == 0.0:

                            continue

                        # Update MPP connected Population (if not fully colonized)

                        if mpp[0][mpc[0][ccc]-1] != mpp_c[c]: # MPP connected is MPC-START

                            if mpp[2][mpc[0][ccc]-1] < mpp_HQ[int(mpp[0][mpc[0][ccc]-1]-1)]*100:

                                mpp[2][mpc[0][ccc]-1] = mpp[2][mpc[0][ccc]-1] + mpp_cEMI_IMIconP

                            mpp_c, ind = np.unique(np.append(mpp_c,[mpp[0][mpc[0][ccc]-1]]), return_index=True)
                            mpp_c = mpp_c[np.argsort(ind)].astype(int)

                        if mpp[0][mpc[1][ccc]-1] != mpp_c[c]: # MPP connected is MPC-AIM

                            if mpp[2][mpc[1][ccc]-1] < (mpp_HQ[int(mpp[0][mpc[1][ccc]-1]-1)]*100): # max pop size hq * 100

                                mpp[2][mpc[1][ccc]-1] = mpp[2][mpc[1][ccc]-1] + mpp_cEMI_IMIconP # function to calculate number of individuals in h -> plus mpp_cEMI_IMIconP

                            mpp_c, ind = np.unique(np.append(mpp_c,[mpp[0][mpc[1][ccc]-1]]), return_index=True)
                            mpp_c = mpp_c[np.argsort(ind)].astype(int)

                # 'mpp': DataFrame to Update ResultsTable

                mpp[2] = np.round(mpp[2], 2)
                mpp[1][mpp[2] == 0.0] = 0
                mpp[1][mpp[2] > 0.0] = 1

                # 'toINS_DB_TS': 'mpp' to String

                toINS_DB_TS = str(np.array(mpp)[[0,2]].T.tolist())[1:-1].replace('[', '(').replace(']', ')')

                cursor.execute("""UPDATE """+str(oS)+""".pas"""+str(x)+"""_rep"""+str(xx)+""" SET ts"""+str(t+1)+""" = ind_arr FROM (values """+toINS_DB_TS+""") AS c(pts_id_arr, ind_arr) WHERE pts_id = pts_id_arr;""")

                # see https://www.postgresql.org/docs/11/runtime-config-autovacuum.html

                cursor.execute("""ALTER TABLE """+str(oS)+""".pas"""+str(x)+"""_rep"""+str(xx)+""" SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")

                conn.commit()

    cursor.close()
    conn.close()

# Multiprocessing; see https://docs.python.org/3/library/multiprocessing.html

def main():

    pool = multiprocessing.Pool(processes=10)
    pool.map(dispMODEL, nCOMB)

    pool.close()
    pool.join()
    
if __name__ in ['__builtin__', '__main__']:
    
    main()
