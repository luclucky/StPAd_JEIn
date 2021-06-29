
require("RPostgreSQL")
library(vioplot)
library(ggplot2)
library(reshape)
library(stringr)

#####

drv = dbDriver("PostgreSQL")

con = dbConnect(drv, dbname = "DB_PhD_03", host = "139.14.20.252", port = 5432, user = "streib_lucas", password = "1gis!gis1")

LS = c('Lc', 'Lrd', 'Lri', 'Lsd', 'Lsi')
DS = c('Dn','Dl', 'Dm', 'Dh')
AF = c('Ah', 'Am', 'An')

SCHEMAs = c()

for (x in LS){

  for( xx in DS){

    for (xxx in AF){

      n = paste('SIM_2_',x,'_',xx,'_',xxx, sep="")

      n = tolower(n)

      SCHEMAs = append(SCHEMAs, n)

    }
  }
}

PASs = 10
REPs = 10

resDF = setNames(data.frame(matrix(ncol = 80, nrow = length(SCHEMAs) * PASs * REPs)), c('LS', 'DS', 'AF', 'PAS', 'REP', paste0('t ', seq(1:75))))

head(resDF)

roW = 1

for (SCHEMA in SCHEMAs){

  for (PAS in c(1:PASs)){

    for (REP in c(1:REPs)){

      resDF[roW, 1] = str_split(SCHEMA, "_")[[1]][3]
      resDF[roW, 2] = str_split(SCHEMA, "_")[[1]][4]
      resDF[roW, 3] = str_split(SCHEMA, "_")[[1]][5]
      resDF[roW, 4] = PAS-1
      resDF[roW, 5] = REP-1

      print(paste(SCHEMA,'.pas',PAS-1,'_rep',REP-1, sep = ''))

      colNMS = dbGetQuery(con, paste("SELECT column_name FROM information_schema.columns WHERE table_schema = '", SCHEMA,"' AND table_name  = 'pas",PAS-1,'_rep',REP-1,"' ORDER BY ordinal_position;", sep = ""))[[1]]
      colNMS = colNMS[3:length(colNMS)]

      SUM_CMD = paste("SUM(", colNMS, ") AS ", colNMS, ",", collapse=" ")
      SUM_CMD = substr(SUM_CMD, 1, nchar(SUM_CMD)-1)

      add_DF = dbGetQuery(con, paste("SELECT ", SUM_CMD ," FROM ", SCHEMA,".pas",PAS-1,'_rep',REP-1,";", sep = ""))

      resDF[roW, 6:(5+length(add_DF))] = add_DF

      roW = roW + 1

      }

    }

  }

save(resDF, file = paste0('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/resDF_02510.Rda'))


