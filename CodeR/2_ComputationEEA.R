
# PART 2: Computation of simulated Effect ES & Effect Addition EA (ES-EP) per LUSEES Combination

# Parameters

# 'resDF': DataFrame covering all Simulation Results

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/resDF_0255.Rda')
resDF[is.na(resDF)] = 0

head(resDF)

# 'BL': BaseLine; i.e. mean of MPN set ub by optimal LUS level without EES

BL = aggregate(. ~ LS+DS+AF, data=resDF[resDF$LS=='lc' & resDF$DS=='dn',], mean)[1,]

# A. Computation simulated Effect ES

ES = resDF

ES[,6:80] = 1 - mapply('/', ES[,6:80], as.numeric(BL[,6:80]))
ES = subset(ES, select = -c(PAS, REP))

save(ES, file = paste0('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/ES.Rda'))

ES = aggregate(. ~ LS+DS+AF, data=resDF, mean)

ES[,6:80] = 1 - mapply('/', ES[,6:80], as.numeric(BL[,6:80]))
ES = subset(ES, select = -c(PAS, REP))

save(ES, file = paste0('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/ES_mean.Rda'))

# B. Computation Effect Addition EA

# Paramerter
LS = c('lc', 'lrd', 'lri', 'lsd', 'lsi')
DS = c('dl', 'dm', 'dh')

EA = ES

EA[,4:78] = 1

for (L in LS){

	for (D in DS){

      Es = ES[which(ES$LS==L & ES$DS==D),4:78]

      Ec = ES[which(ES$LS==L & ES$DS=='dn'),4:78]

      Ed = ES[which(ES$LS=='lc' & ES$DS==D ),4:78]

      Ep = Ec + Ed - (Ec * Ed)

      #Ep[Ep < 0] = 0

      #Ea = round((Es - Ep), 2)

      Ea = ((Ep+1) / (Es+1))

      #Ea = Ea * ifelse(abs(Es / Ep) > 0.05, 1, NA)
      #
      #Ea[is.na(Ea)] = 1

      EA[which(EA$LS==L & EA$DS==D),4:78] = Ea

    }
}

# Computation Effect Addition EA; i.e. Deviations of EP & ES

# Store 'LUSEES' as 'EA.Rda'-File

save(EA, file = paste0('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/EA_eA.Rda'))

##


EA = ES

EA[,4:78] = 1

for (L in LS){

	for (D in DS){

      Es = ES[which(ES$LS==L & ES$DS==D),4:78]

      Ec = ES[which(ES$LS==L & ES$DS=='dn' & ES$AF=='an'),4:78]
      Ec = rbind(Ec, Ec, Ec)

      Ed = ES[which(ES$LS=='lc' & ES$DS==D & ES$AF=='an'),4:78]
      Ed = rbind(Ed, Ed, Ed)

      Ep = Ec + Ed - (Ec * Ed)

      #Ep[Ep < -1] = -1

      #Ea = round((Es - Ep), 2)

      Ea = ((Ep+1) / (Es+1))

      #Ea = Ea * ifelse(abs(Es / Ep) > 0.05, 1, NA)
      #
      #Ea[is.na(Ea)] = 1

      EA[which(EA$LS==L & EA$DS==D),4:78] = Ea

    }
}


# Computation Effect Addition EA; i.e. Deviations of EP & ES

# Store 'LUSEES' as 'EA.Rda'-File

save(EA, file = paste0('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/EA_iA.Rda'))


