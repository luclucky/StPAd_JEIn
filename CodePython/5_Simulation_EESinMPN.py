# PART 5: Simulation 'EESinMPN' - ExtremeEventScenarios in MetaPopualtionNetworks

# Packages

import numpy as np
np.set_printoptions(suppress=True)

import psycopg2

from random import *

import multiprocessing

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

# Parameters

# EMI_SHRsurv

co_max = 1250 #DispersalCosts Max

## logGRO

igr = 2.0 # IntrinsicGrowthRate

## DENdepEMI_RATE
     
m_max = 0.20 # EmigrationRate max per MPP
s = 0.5 # Propensity to Disperse

## ExtremeEvents

ee_i = [25, 50, 75] # Intensity
ee_f = [5, 10, 20] # Frequency
ee_v = ['r'] # Interval

ees = [] # ExtremeEvent Combinations

for x in range(len(ee_i)):

    for xx in range(len(ee_f)):

        for xxx in range(len(ee_v)):

            ees.append([ee_i[x], ee_f[xx], ee_v[xxx]])

ees.insert(0, [0, 0, 'n'])

## Simulation

ts = 110 # TimeSpan

#

def dispMODEL(inP):

    # PostgreSQL DB-Connection

    conn = psycopg2.connect("host=??? port=??? dbname=??? user=??? password=???")
    cursor = conn.cursor()

    #

    oS = str(inP[2])

    cursor.execute("""CREATE SCHEMA IF NOT EXISTS """ + str(oS) + """;""")

    conn.commit()

    # Loop over EES, PAS&LUS (i.e. MPN)

    for x in ees:

        pas = 10

        for xx in range(pas):

            lus = 10

            for xxx in range(lus):

                # DataFrame 'mpc': MetaPopulationConnection Parameters 'start' - LineStart (MPP ID) | 'aim' - LineEnd (MPP ID) | 'costs' - DispersalCost Connection

                cursor.execute("""SELECT start, aim, costs FROM mpc_"""+str(inP[1])+"""."""+inP[0]+str(xxx)+"""_pas"""+str(xx)+""";""")
                mpc = cursor.fetchall()
                mpc = [y for y in mpc if y[2] <= co_max]
                mpc = np.array(mpc, dtype=object).T

                # Table SimulationResults per MPN (MetaPopualtionNetwork ;i.e. PAS&LUS Combination) & EES

                cursor.execute("""CREATE TABLE IF NOT EXISTS """+str(oS)+""".mpn$"""+inP[0]+str(xxx)+"""pas"""+str(xx)+"""_ees$"""+str(x[0])+str(x[1])+str(x[2])+""" AS SELECT pts_id, hq FROM mpp_"""+inP[1]+"""."""+inP[0]+str(xxx)+"""_pas"""+str(xx)+""";""")

                conn.commit()

                # DataFrame 'mpp': MetaPopulationPatches Parameters 'pts_id' - MPP ID | 'hq' - MPP HabitatQuality

                cursor.execute("""SELECT pts_id, hq FROM """+str(oS)+""".mpn$"""+inP[0]+str(xxx)+"""pas"""+str(xx)+"""_ees$"""+str(x[0])+str(x[1])+str(x[2])+""" ORDER BY pts_id;""")
                mpp_IDHQ = cursor.fetchall()
                mpp_IDHQ = np.array(np.array(mpp_IDHQ).T)
                mpp_ID = mpp_IDHQ[0]
                mpp_HQ = mpp_IDHQ[1]

                mpp = np.empty([3, len(mpp_ID)])
                mpp[0] = mpp_ID
                mpp[1] = 1
                mpp[2] = mpp_HQ * (0.1 * 100)

                # Share surviving Emmigrants per MPC

                pEs = EMI_SHRsurv(co = mpc[2], co_max = co_max)

                ts_rng = range(ts)

                # 'ts_ee': time steps EE

                if x[1] != 0:

                    ts_ee = np.array(ts_rng[0::x[1]])

                    if x[2] == 'ir':

                        ts_ee = np.array([y + randint(0, x[1]-1) for y in ts_ee])

                    ts_ee = ts_ee + 10

                else:

                    ts_ee = []

                # Simulation per TS (TimeSpan)

                for xxxx in range(ts):

                    # Column 'txxxx' to store Results per TimeSteps

                    cursor.execute("""ALTER TABLE """+str(oS)+""".mpn$"""+inP[0]+str(xxx)+"""pas"""+str(xx)+"""_ees$"""+str(x[0])+str(x[1])+str(x[2])+""" ADD IF NOT EXISTS ts"""+str(xxxx+1)+""" float;""")

                    conn.commit()

                    if xxxx >= 10:

                        # Environmental Extinction (individually) per MPP based on HQ

                        mpp_se = [np.random.choice([0, 1], p=[pR, 1 - pR]) for pR in (1 - mpp_HQ[np.where(mpp[2] > 0.0)]) * 0.12 + 0.01]
                        mpp[1][np.where(mpp[2] > 0.0)] = mpp[1][np.where(mpp[2] > 0.0)] * mpp_se
                        mpp[2][np.where(mpp[2] > 0.0)] = mpp[2][np.where(mpp[2] > 0.0)] * mpp_se

                    if xxxx in ts_ee:

                        # ExtremeEvents Mortality per MPP

                        mpp[2] = mpp[2] - float(x[0])
                        mpp[2][mpp[2] < 0] = 0.0

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

                    for xxxxx in range(len(mpp_c)):

                        # 'conP_idx': Index of MPPs connected to (specific) MPP colonized

                        if mpp_c[xxxxx] in mpc[0] or mpp_c[xxxxx] in mpc[1]:

                            conP_idx = np.hstack(np.array([np.where(mpc[0] == mpp_c[xxxxx])[0].tolist(), np.where(mpc[1] == mpp_c[xxxxx])[0].tolist()]).flatten()).tolist()
                            conP_idx = [int(y) for y in conP_idx]

                        else:
                            
                            continue

                        # 'conP_cf': MPP connected fully colonized

                        conP_cf = []

                        for xxxxxx in conP_idx:

                            if mpc[0][xxxxxx] != mpp_c[xxxxx]:

                                if mpp[2][mpc[0][xxxxxx]-1] >= mpp_HQ[int(mpp[0][mpc[0][xxxxxx]-1]-1)]*100:

                                    conP_cf.append(xxxxxx)

                            else:

                                if mpp[2][mpc[1][xxxxxx]-1] >= mpp_HQ[int(mpp[0][mpc[1][xxxxxx]-1]-1)]*100:

                                    conP_cf.append(xxxxxx)

                        # remove 'conP_cf' from 'conP_idx':

                        [conP_idx.remove(cf) for cf in conP_cf]

                        if conP_idx == []:

                            continue

                        # 'mpp_cEMI': Emigrants per MPP

                        mpp_cEMI = DENdepEMI_RATE(M = m_max, N = mpp[2][int(mpp_c[xxxxx]-1)], K = mpp_HQ[int(mpp_c[xxxxx]-1)]*100, s = s)

                        # Reduce MPP Population by 'mpp_cEMI'

                        mpp[2][int(mpp_c[xxxxx]-1)] = mpp[2][int(mpp_c[xxxxx]-1)] - mpp_cEMI

                        # 'mpp_cEMI_SHRconP': Share 'mpp_cEMI' per MPP connected

                        mpp_cEMI_SHRconP = EMI_SHRconP(COSTs = mpc[2][conP_idx].astype(float))

                        # Adjust MPP connected

                        for xxxxxxx in conP_idx:

                            mpp_cEMI_IMIconP = mpp_cEMI * mpp_cEMI_SHRconP[0] # potential Immigrants to MPP connected

                            mpp_cEMI_SHRconP = mpp_cEMI_SHRconP[1:]

                            mpp_cEMI_IMIconP = mpp_cEMI_IMIconP * pEs[xxxxxxx] # reduce Immigrants by DispersalMortality

                            if mpp_cEMI_IMIconP == 0.0:

                                continue

                            # Update MPP connected Population (if not fully colonized)

                            if mpp[0][mpc[0][xxxxxxx]-1] != mpp_c[xxxxx]: # MPP connected is MPC-START

                                if mpp[2][mpc[0][xxxxxxx]-1] < mpp_HQ[int(mpp[0][mpc[0][xxxxxxx]-1]-1)]*100:

                                    mpp[2][mpc[0][xxxxxxx]-1] = mpp[2][mpc[0][xxxxxxx]-1] + mpp_cEMI_IMIconP

                                mpp_c, ind = np.unique(np.append(mpp_c,[mpp[0][mpc[0][xxxxxxx]-1]]), return_index=True)
                                mpp_c = mpp_c[np.argsort(ind)].astype(int)

                            if mpp[0][mpc[1][xxxxxxx]-1] != mpp_c[xxxxx]: # MPP connected is MPC-AIM

                                if mpp[2][mpc[1][xxxxxxx]-1] < (mpp_HQ[int(mpp[0][mpc[1][xxxxxxx]-1]-1)]*100): # max pop size hq * 100

                                    mpp[2][mpc[1][xxxxxxx]-1] = mpp[2][mpc[1][xxxxxxx]-1] + mpp_cEMI_IMIconP # function to calculate number of individuals in h -> plus mpp_cEMI_IMIconP

                                mpp_c, ind = np.unique(np.append(mpp_c,[mpp[0][mpc[1][xxxxxxx]-1]]), return_index=True)
                                mpp_c = mpp_c[np.argsort(ind)].astype(int)

                    # 'mpp': DataFrame to Update ResultsTable

                    mpp[2] = np.round(mpp[2], 2)
                    mpp[1][mpp[2] == 0.0] = 0
                    mpp[1][mpp[2] > 0.0] = 1

                    # 'toINS_DB_TS': 'mpp' to String

                    toINS_DB_TS = str(np.array(mpp)[[0,2]].T.tolist())[1:-1].replace('[', '(').replace(']', ')')

                    cursor.execute("""UPDATE """+str(oS)+""".mpn$"""+inP[0]+str(xxx)+"""pas"""+str(xx)+"""_ees$"""+str(x[0])+str(x[1])+str(x[2])+""" SET ts"""+str(xxxx+1)+""" = ind_arr FROM (values """+toINS_DB_TS+""") AS c(pts_id_arr, ind_arr) WHERE pts_id = pts_id_arr;""")

                    # see https://www.postgresql.org/docs/11/runtime-config-autovacuum.html

                    cursor.execute("""ALTER TABLE """+str(oS)+""".mpn$"""+inP[0]+str(xxx)+"""pas"""+str(xx)+"""_ees$"""+str(x[0])+str(x[1])+str(x[2])+""" SET (autovacuum_enabled = false, toast.autovacuum_enabled = false);""")
                    
                    conn.commit()

    cursor.close()
    conn.close()

# Multiprocessing; see https://docs.python.org/3/library/multiprocessing.html

def main():

    # Parameters

    NLMs = ['nlmr', 'nlmrc', 'nlmre'] # NLM types applied

    inSs = ['000050050', '100000000', '050000050', '000100000', '050050000', '000000100', '050025025', '025050025', '025025050'] # To Query MPN-Schemas; i.e. 'mpp_...' & 'mpc_...'

    outSs = ['sim_000050050', 'sim_100000000', 'sim_050000050', 'sim_000100000', 'sim_050050000', 'sim_000000100', 'sim_050025025', 'sim_025050025', 'sim_025025050'] # Output-Schemas

    inPs = []

    # ParameterCombinations

    for x in range(len(NLMs)):
        for xx in range(len(inSs)):
            inPs.append([NLMs[x], inSs[xx], outSs[xx]])

    #

    pool = multiprocessing.Pool(processes=9)
    pool.map(dispMODEL, inPs)

    pool.close()
    pool.join()
    
if __name__ in ['__builtin__', '__main__']:
    
    main()
