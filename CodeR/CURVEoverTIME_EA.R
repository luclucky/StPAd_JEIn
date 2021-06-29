
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

library(ggpubr)
library(cowplot)
library(gridExtra)

library(scales)

library(plotly)

library(dplyr)

library(extrafont)
# font_import()

library(ggallin)

options(scipen=1)

theme_classicGRID = function (base_size = 11, base_family = "", base_line_size = base_size/22, base_rect_size = base_size/22) {theme_bw(base_size = base_size, base_family = base_family, base_line_size = base_line_size, base_rect_size = base_rect_size) %+replace% theme(panel.border = element_blank(), axis.line = element_line(colour = "black", size = rel(1)), legend.key = element_blank(), strip.background = element_rect(fill = "white", colour = "black", size = rel(2)), complete = TRUE, panel.grid.major.y = element_line(), panel.grid.major.x = element_blank(), panel.grid.minor.y = element_blank())}

theme_set(theme_classic())

###

###

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/EA_eA.Rda')

str(EA)

EA[,4:78] = round(EA[,4:78], 2)


EA[,4:78][EA[,4:78] <= 1.01 & EA[,4:78] >= 0.99] = 1

###

DF = melt(EA, id.vars = colnames(EA)[1:3])

###

DF = DF[which(DF$LS!='lc' & DF$DS!='dn'),]

colnames(DF)
str(DF)
head(DF)
tail(DF)

DF$`LS` = factor(DF$`LS`)
DF$`LS` = factor(DF$`LS`, levels(DF$`LS`)[c(2,4,3,1)])
levels(DF$`LS`) = c('ramped \u2191', 'stepwise \u2191', 'stepwise \U2193', 'ramped \U2193')

DF$`DS` = factor(DF$`DS`)
DF$`DS` = factor(DF$`DS`, levels(DF$`DS`)[c(2,3,1)])
levels(DF$`DS`) = c('low', 'medium', 'high')

DF$`AF` = factor(DF$`AF`)
levels(DF$`AF`) = c('high', 'low', 'no')

DF_ID = unite(DF, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)

pLoT =
	ggplot(data = DF_ID, aes(x = as.numeric(variable)-1, y = value-1, group = unique_id))  +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), data = DF_ID[which(DF_ID$DS!="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_point(shape = ".", aes(color = `AF`, fill= `AF` )) +
	scale_fill_manual(values = c('yellowgreen','orange','red')) +
	#labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous('Interaction', breaks = c(-0.2,0,0.2), labels = c(0.8,1,1.2), limits = c(-0.2,0.2), sec.axis = sec_axis(~ . + 10, name = 'Adaptation')) +
	#scale_y_continuous(expression(atop((1+E[p(SA)]) / (1+E[s(SA)])), ''), breaks = c(-0.2,0,0.2), labels = c(0.8,1,1.2), limits = c(-0.2,0.2), sec.axis = sec_axis(~ . + 10, name = 'Adaptation')) +
	#scale_y_continuous(expression(atop((1+E[p(SA)]) / (1+E[s(SA)])), ''), breaks = c(-0.25,-0.125,0,0.125,0.25), labels = c(0.75,0.875,1,1.125,1.25), limits = c(-0.3,0.3), sec.axis = sec_axis(~ . + 10, name = 'Adaptation \n'), trans=ssqrt_trans) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 3) +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_vline(xintercept = 50, size = 0.25, linetype = 3, color = 'grey') +
	scale_x_continuous("Time Step", breaks = seq(0,75,25), limits = c(0,77.5), sec.axis = sec_axis(~ . + 10, name = 'Climatic event Scenario')) +
	theme(axis.text.x = element_text(size = 8), axis.text.y = element_text(size = 8), axis.title.x = element_text(size = 12), axis.title.y = element_text(size = 12),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.position = "none", plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

levels(DF$`LS`) = c('ramped \u2191', 'stepwise \u2191', 'stepwise \U2193', 'ramped \U2193')

levels(DF_ID$`LS`) = c('\u2197', '\u2191', '\U2193', '\U2198')

DF_ID[DF_ID$`LS` == '\u2197' & DF_ID$value == 1, ]$value = DF_ID[DF_ID$`LS` == '\u2197' & DF_ID$value == 1, ]$value + 0.0002

DF_ID[DF_ID$`LS` == '\u2191' & DF_ID$value == 1, ]$value = DF_ID[DF_ID$`LS` == '\u2191' & DF_ID$value == 1, ]$value + 0.0001

DF_ID[DF_ID$`LS` == '\u2193' & DF_ID$value == 1, ]$value = DF_ID[DF_ID$`LS` == '\u2193' & DF_ID$value == 1, ]$value - 0.0001

DF_ID[DF_ID$`LS` == '\u2198' & DF_ID$value == 1, ]$value = DF_ID[DF_ID$`LS` == '\u2198' & DF_ID$value == 1, ]$value - 0.0002

pLoT2 =
	pLoT +
    #stat_smooth(method="lm", se = FALSE, colour = 'darkgrey', size = 0.25, lwd = 0.25) +
	facet_grid(AF ~ DS) +
	geom_text_repel(data = subset(DF_ID, variable == "t 75"), aes(label = `LS`), box.padding = .1, min.segment.length = Inf, nudge_x = 3.75, nudge_y = 0, direction = "y", size = 2.5) +
	theme(strip.text = element_text(size=8), strip.background = element_blank(), panel.border = element_rect(colour = "grey90", fill = NA))

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEA.jpg", sep=""), pLoT2, width = 20, height = 13.333, units = "cm")

##


###

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/EA_iA.Rda')

str(EA)

###

DF = melt(EA, id.vars = colnames(EA)[1:3])

###

DF = DF[which(DF$DS!='dn'),]

DF$`LS` = factor(DF$`LS`)
DF$`LS` = factor(DF$`LS`, levels(DF$`LS`)[c(3,5,1,4,2)])
levels(DF$`LS`) = c('ramped \u2197', 'stepwise \u2191', 'consistent', 'stepwise \U2193', 'ramped \U2198')

DF$`DS` = factor(DF$`DS`)
DF$`DS` = factor(DF$`DS`, levels(DF$`DS`)[c(2,3,1)])
levels(DF$`DS`) = c('low', 'medium', 'high')

DF$`AF` = factor(DF$`AF`)
levels(DF$`AF`) = c('high', 'low', 'no')

DF$value = round(DF$value, 2)

DF$value[DF$value <= 1.01 & DF$value >= 0.99] = 1

DF_ID = unite(DF, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)

pLoT =
	ggplot(data = DF_ID, aes(x = as.numeric(variable)-1, y = value-1, group = unique_id))  +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), data = DF_ID[which(DF_ID$DS!="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_point(shape = ".", aes(color = `AF`, fill= `AF` )) +
	scale_fill_manual(values = c('yellowgreen','orange','red')) +
	#labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous(expression(atop((1+E[p(SA)]) / (1+E[s(SA)])), ''), breaks = c(-0.5,-0.25,0,0.25,0.5), labels = c(0.5,0.75,1,1.25,1.5), limits = c(-0.5,0.5), sec.axis = sec_axis(~ . + 10, name = 'Adaptation \n')) +
	#scale_y_continuous(expression(atop((1+E[p(SA)]) / (1+E[s(SA)])), ''), breaks = c(-0.5,-0.25,0,0.25,0.5), labels = c(0.5,0.75,1,1.25,1.5), limits = c(-0.5,0.5),, sec.axis = sec_axis(~ . + 10, name = 'Adaptation \n'), trans=ssqrt_trans) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 3) +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_vline(xintercept = 50, size = 0.25, linetype = 3, color = 'grey') +
	scale_x_continuous("\n Time Step", breaks = seq(0,75,25), limits = c(0,77.5), sec.axis = sec_axis(~ . + 10, name = 'Climatic event Scenario \n')) +
	theme(axis.text.x = element_text(size = 8), axis.text.y = element_text(size = 8), axis.title.x = element_text(size = 12), axis.title.y = element_text(size = 12),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.position = "none", plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

levels(DF_ID$`LS`) = c('\u2197', '\u2191', '\u2192', '\U2193', '\U2198')

DF_ID = DF_ID[order(DF_ID$`LS`),]

DF_ID[DF_ID$`LS` == '\u2197', ]$value = DF_ID[DF_ID$`LS` == '\u2197', ]$value + 0.0002

DF_ID[DF_ID$`LS` == '\u2191', ]$value = DF_ID[DF_ID$`LS` == '\u2191', ]$value + 0.0001

DF_ID[DF_ID$`LS` == '\u2193', ]$value = DF_ID[DF_ID$`LS` == '\u2193', ]$value - 0.0001

DF_ID[DF_ID$`LS` == '\u2198', ]$value = DF_ID[DF_ID$`LS` == '\u2198', ]$value - 0.0002

pLoT2 =
	pLoT +
    #stat_smooth(method="lm", se = FALSE, colour = 'darkgrey', size = 0.25, lwd = 0.25) +
	facet_grid(AF ~ DS) +
	geom_text_repel(data = subset(DF_ID, variable == "t 75"), aes(label = `LS`), box.padding = .1, min.segment.length = Inf, nudge_x = 3.75, nudge_y = 0.0075, direction = "y", size = 2.5, force=0.05) +
	theme(strip.text = element_text(size=8), strip.background = element_blank())

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEA_iA.jpg", sep=""), pLoT2, width = 20, height = 13.333, units = "cm")