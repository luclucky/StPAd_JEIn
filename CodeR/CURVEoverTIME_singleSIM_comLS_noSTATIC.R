
require("RPostgreSQL")
require(data.table)

library(see)
library(vioplot)
library(ggplot2)
library(reshape)
# library(Hmisc)
library(ggforce)
require(tidyr)
require(ggplot2)
require(dplyr)
require(magrittr)
library(ggrepel)

#library(ggpubr)
library(cowplot)
library(gridExtra)

library(scales)

library(plotly)

library(dplyr)

library(extrafont)
# font_import()

options(scipen=1)

theme_classicGRID = function (base_size = 11, base_family = "", base_line_size = base_size/22, base_rect_size = base_size/22) {theme_bw(base_size = base_size, base_family = base_family, base_line_size = base_line_size, base_rect_size = base_rect_size) %+replace% theme(panel.border = element_blank(), axis.line = element_line(colour = "black", size = rel(1)), legend.key = element_blank(), strip.background = element_rect(fill = "white", colour = "black", size = rel(2)), complete = TRUE, panel.grid.major.y = element_line(), panel.grid.major.x = element_blank(), panel.grid.minor.y = element_blank())}

theme_set(theme_classic())

###

drv = dbDriver("PostgreSQL")

con = dbConnect(drv, dbname = "DB_PhD_03", host = "139.14.20.252", port = 5432, user = "streib_lucas", password = "1gis!gis1")

DS = c('Dl', 'Dm', 'Dh')

S = DS[1]
Dl = dbGetQuery(con, paste("SELECT * FROM ds.", S,";", sep = ""))

S = DS[2]
Dm = dbGetQuery(con, paste("SELECT * FROM ds.", S," ORDER BY rep;", sep = ""))

Dm = Dm[1:50,]
Dm[,1] = seq(0,49)


S = DS[3]
Dh = dbGetQuery(con, paste("SELECT * FROM ds.", S,";", sep = ""))

###

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/resDF_02510_2.Rda')

str(resDF)

resDF[is.na(resDF)] = 0
resDF$`AF` = factor(resDF$`AF`)
levels(resDF$`AF`) = c('high', 'low', 'no')

head(resDF)

LS = c('lc', 'lrd', 'lri', 'lsd', 'lsi')
DS = c('dl', 'dm', 'dh')

PASs = 10
REPs = 10

T = seq(1, 75)

for (D in DS){

	if (D == 'dl'){
		EE = Dl
	}
	if (D == 'dm'){
		EE = Dm
	}
	if (D == 'dh'){
		EE = Dh
	}

	for (P in c(1:PASs)){

		for (R in c(1:REPs)){

			resDF_RUN = resDF[which(resDF$DS==D & resDF$PAS==P-1 & resDF$REP==R-1),]
			resDF_RUN = resDF_RUN[,c(-4,-5)]

			DF = melt(resDF_RUN)

			DF$`LS` = factor(DF$`LS`)
			DF$`LS` = factor(DF$`LS`, levels(DF$`LS`)[c(3,5,1,4,2)])
			levels(DF$`LS`) = c('\u2197', '\u2191', '\u2192', '\U2193', '\U2198')

			E = as.numeric(EE[which(EE$rep==R-1),])[2:76]

			E[E == 0] = NA

			Es = tibble(T, E)

			pL =
				ggplot(DF, aes(x = as.numeric(variable), y = value)) +
				geom_line(data = DF[which(DF$LS=='\U2198'),], size = 0.5, aes(color = `AF`)) +
				geom_point(data = DF[which(DF$LS=='\U2198'),], size = 0.25, aes(color = `AF`)) +
				labs(color = "Adaptation", fill = "Adaptation") +
				scale_color_manual(values = c('yellowgreen','orange','red')) +
				geom_linerange(data= Es, aes(x = T, y = E, ymax = 7500, ymin = 7500-E*75), size = 0.25, color = 'darkgrey') +
				geom_point(data= Es, aes(x = T, y = 7500-E*75), size = 0.25) +
				scale_x_continuous("Time", breaks = seq(0,75,25)) +
				scale_y_continuous(expression(italic(N)), breaks = c(0, 2500, 5000, 7500), limits = c(0, 7500), sec.axis = sec_axis(~ . * 1/75, name = 'Event Mortality', breaks = c(0, 50, 100), labels = c('100', '50', '0'))) +
				geom_vline(xintercept = 25, size = 0.25, linetype = 3, color = 'grey') +
				geom_vline(xintercept = 50, size = 0.25, linetype = 3, color = 'grey') +
				theme(axis.text.x = element_text(size = 10), axis.text.y =element_text(size = 10), axis.title.x = element_text(size = 12), axis.title.y = element_text(size = 12),  axis.ticks.x = element_line(size=1), axis.ticks.y = element_line(size=1), legend.justification = "bottom", plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5) +
			  guides(color = guide_legend(label.position = "left"))

			pL = pL +
				theme(legend.position="bottom")

			pL_r = pL +
				geom_line(data = DF[which(DF$LS=='\u2197'),], size = 0.5, aes(color = `AF`), lty = 1) +
				geom_point(data = DF[which(DF$LS=='\u2197'),], size = 0.25, aes(color = `AF`))

			pL_r = pL_r +
				geom_text_repel(data = DF[which(DF$LS %in% c('\u2197','\U2198') & DF$variable == "t 75"),], aes(label = `LS`), box.padding = .1, min.segment.length = Inf, nudge_x = 2, nudge_y = 0.0075, direction = "y", size = 3.75, force=0.05)

			ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/Simulations_nS/ramp_",D,P-1,R-1,".jpg", sep=""), pL_r, width = 30, height = 20, units = "cm")

			pL_s = pL +
				geom_line(data = DF[which(DF$LS=='\u2191'),], size = 0.5, aes(color = `AF`), lty = 1) +
				geom_point(data = DF[which(DF$LS=='\u2191'),], size = 0.25, aes(color = `AF`)) +
				geom_line(data = DF[which(DF$LS=='\U2193'),], size = 0.5, aes(color = `AF`), lty = 1) +
				geom_point(data = DF[which(DF$LS=='\U2193'),], size = 0.25, aes(color = `AF`))

			pL_s = pL_s +
				geom_text_repel(data = DF[which(DF$LS %in% c('\u2191', '\u2192', '\U2193') & DF$variable == "t 75"),], aes(label = `LS`), box.padding = .1, min.segment.length = Inf, nudge_x = 2, nudge_y = 0.0075, direction = "y", size = 3.75, force=0.05)

			ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/Simulations/step_",D,P-1,R-1,".jpg", sep=""), pL_s, width = 30, height = 20, units = "cm")

		}
	}
}
