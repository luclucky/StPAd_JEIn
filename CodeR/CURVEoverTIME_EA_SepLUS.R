
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

library(ggallin)

options(scipen=1)

theme_classicGRID = function (base_size = 11, base_family = "", base_line_size = base_size/22, base_rect_size = base_size/22) {theme_bw(base_size = base_size, base_family = base_family, base_line_size = base_line_size, base_rect_size = base_rect_size) %+replace% theme(panel.border = element_blank(), axis.line = element_line(colour = "black", size = rel(1)), legend.key = element_blank(), strip.background = element_rect(fill = "white", colour = "black", size = rel(2)), complete = TRUE, panel.grid.major.y = element_line(), panel.grid.major.x = element_blank(), panel.grid.minor.y = element_blank())}

theme_set(theme_classic())

###

###

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/EA_eA_new.Rda')

str(EA)

# EA[,4:78] = round(EA[,4:78], 2)
#
# EA[,4:78][EA[,4:78] <= 1.01 & EA[,4:78] >= 0.99] = 1

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

levels(DF$`LS`) = c('\u2197', '\u2191', '\U2193', '\U2198')

DF$`DS` = factor(DF$`DS`)
DF$`DS` = factor(DF$`DS`, levels(DF$`DS`)[c(2,3,1)])
levels(DF$`DS`) =  c('moderate', 'severe', 'intense')

DF$`AF` = factor(DF$`AF`)
levels(DF$`AF`) = c('high', 'low', 'no')

DF_ID = unite(DF, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)
DAT = DF_ID[DF_ID$LS %in% c("↗","→","↘"), ]

pLoT =
	ggplot(data = DAT, aes(x = as.numeric(variable)-1, y = value-1, group = unique_id))  +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_point(shape = ".", aes(color = `AF`, fill= `AF` )) +
	scale_fill_manual(values = c('yellowgreen','orange','red')) +
	#labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous('Interaction\n\n', breaks = c(-0.2,-0.1,0,0.1,0.2), labels = c(0.8,0.9,1,1.1,1.2), limits = c(-0.2,0.2), sec.axis = sec_axis(~ . + 10, name = 'Adaptation\n')) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 1) +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_vline(xintercept = 50, size = 0.25, linetype = 3, color = 'grey') +
	scale_x_continuous("\nTime Step", breaks = seq(25,75,25), limits = c(17.5,77.5), sec.axis = sec_axis(~ . + 10, name = 'Climate Scenario\n')) +
	theme(axis.text.x = element_text(size = 10), axis.text.y = element_text(size = 10), axis.title.x = element_text(size = 12, lineheight = .25), axis.title.x.top = element_text(size = 12, lineheight = .25), axis.title.y = element_text(size = 12, lineheight = .25), axis.title.y.right = element_text(size = 12, lineheight = .25),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.position = "none", plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

DAT_75 = subset(DAT, variable == "t 75")


pLoT2 =
	pLoT +
	facet_grid(AF ~ DS) +
	geom_label(data = subset(DAT, variable == "t 25" & LS == "↗"), label = c('c.','a.','b.','f.','d.','e.','i.','g.','h.') , nudge_x = -2.5, nudge_y = 0.175, size = 2, label.r = unit(0, "pt"), label.size = 0, color = 'darkgrey') +
	geom_text_repel(data = subset(DAT, variable == "t 75"), aes(label = `LS`), box.padding = -.1, min.segment.length = Inf, nudge_x = 3.75, nudge_y = 0, direction = "y", size = 3.75, max.overlaps = 10) +
	theme(strip.text = element_text(size=10), strip.background = element_blank(), panel.border = element_rect(colour = NA, fill = NA))

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEA_new_RP.jpg", sep=""), pLoT2, width = 20, height = 20, units = "cm")

###

DF_ID = unite(DF, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)
DAT = DF_ID[DF_ID$LS %in% c("↑","→","↓"), ]

pLoT =
	ggplot(data = DAT, aes(x = as.numeric(variable)-1, y = value-1, group = unique_id))  +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_point(shape = ".", aes(color = `AF`, fill= `AF` )) +
	scale_fill_manual(values = c('yellowgreen','orange','red')) +
	#labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous('Interaction\n\n', breaks = c(-0.2,-0.1,0,0.1,0.2), labels = c(0.8,0.9,1,1.1,1.2), limits = c(-0.2,0.2), sec.axis = sec_axis(~ . + 10, name = 'Adaptation\n')) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 1) +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_vline(xintercept = 50, size = 0.25, linetype = 3, color = 'grey') +
	scale_x_continuous("\nTime Step", breaks = seq(25,75,25), limits = c(17.5,77.5), sec.axis = sec_axis(~ . + 10, name = 'Climate Scenario\n')) +
	theme(axis.text.x = element_text(size = 10), axis.text.y = element_text(size = 10), axis.title.x = element_text(size = 12, lineheight = .25), axis.title.x.top = element_text(size = 12, lineheight = .25), axis.title.y = element_text(size = 12, lineheight = .25), axis.title.y.right = element_text(size = 12, lineheight = .25),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.position = "none", plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

pLoT2 =
	pLoT +
	facet_grid(AF ~ DS) +
	geom_label(data = subset(DAT, variable == "t 25" & LS == "↑"), label = c('c.','a.','b.','f.','d.','e.','i.','g.','h.'), nudge_x = -2.5, nudge_y = 0.175, size = 2, label.r = unit(0, "pt"), label.size = 0, color = 'darkgrey') +
	geom_text_repel(data = subset(DAT, variable == "t 75"), aes(label = `LS`), box.padding = -.1, min.segment.length = Inf, nudge_x = 3.75, nudge_y = 0, direction = "y", size = 3.75, max.overlaps = 10) +
	theme(strip.text = element_text(size=10), strip.background = element_blank(), panel.border = element_rect(colour = NA, fill = NA))

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEA_new_SW.jpg", sep=""), pLoT2, width = 20, height = 20, units = "cm")