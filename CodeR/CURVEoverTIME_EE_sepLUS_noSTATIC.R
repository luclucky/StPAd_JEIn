
require("RPostgreSQL")
require(data.table)

library(see)
library(vioplot)
library(ggplot2)
library(reshape)
# library(Hmisc)
library(ggforce)
require(tidyr)
require(dplyr)
require(magrittr)
library(ggrepel)

#library(ggpubr)
library(cowplot)
library(gridExtra)

library(scales)
library(reader)

library(plotly)

library(dplyr)

library(extrafont)
# font_import()

#library(ggpattern)

options(scipen=1)

theme_classicGRID = function (base_size = 11, base_family = "", base_line_size = base_size/22, base_rect_size = base_size/22) {theme_bw(base_size = base_size, base_family = base_family, base_line_size = base_line_size, base_rect_size = base_rect_size) %+replace% theme(panel.border = element_blank(), axis.line = element_line(colour = "black", size = rel(1)), legend.key = element_blank(), strip.background = element_rect(fill = "white", colour = "black", size = rel(2)), complete = TRUE, panel.grid.major.y = element_line(), panel.grid.major.x = element_blank(), panel.grid.minor.y = element_blank())}

theme_set(theme_classic())

###

###

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/ES_new.Rda')

str(ES)

###

DF = melt(ES, id.vars = colnames(ES)[1:3])

colnames(DF)
str(DF)
head(DF)
tail(DF)

DF_ID = unite(DF, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)

head(DF_ID)

Conf_level = 0.95

# https://github.com/JoachimGoedhart/Plot-Time-series-with-uncertainty/blob/master/Plot-Time-series-with-uncertainty.R
# https://thenode.biologists.com/visualizing-data-one-more-time/education/
## https://www.cyclismo.org/tutorial/R/confidence.html

DF_ID_statS = as.data.frame(DF_ID 				%>%
				filter(!is.na(value)) 				%>%
				group_by(variable, `unique_id`) 				%>%
				summarise(mean = mean(value, na.rm = TRUE),
						  median = median(value, na.rm = TRUE),
						  min = min(value, na.rm = TRUE),
						  max = max(value, na.rm = TRUE),
						  quant_5 = quantile(value, probs = c(.05), na.rm = TRUE),
						  quant_25 = quantile(value, probs = c(.25), na.rm = TRUE),
						  quant_75 = quantile(value, probs = c(.75), na.rm = TRUE),
						  quant_95 = quantile(value, probs = c(.95), na.rm = TRUE),
						  sd = sd(value, na.rm = TRUE),
						  n = n())				%>%
				mutate(sem = sd / sqrt(n - 1),
						CI_lower = mean + qt((1-Conf_level)/2, n - 1) * sem,
						CI_upper = mean - qt((1-Conf_level)/2, n - 1) * sem))

colnames(DF_ID_statS)
str(DF_ID_statS)
head(DF_ID_statS)
tail(DF_ID_statS)

DF_ID_statS = DF_ID_statS %>% separate(unique_id, c('LS', 'DS', 'AF'))
DF_ID_statS = unite(DF_ID_statS, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)

DF_ID_statS$`LS` = factor(DF_ID_statS$`LS`)
DF_ID_statS$`LS` = factor(DF_ID_statS$`LS`, levels(DF_ID_statS$`LS`)[c(5,3,1,2,4)])
#levels(DF_ID_statS$`LS`) = c('stepwise \u2191', 'ramped \u2197', 'static \u2192', 'ramped \U2198', 'stepwise \U2193')
levels(DF_ID_statS$`LS`) = c('\u2191', '\u2197', '\u2192', '\U2198', '\U2193')

DF_ID_statS$`DS` = factor(DF_ID_statS$`DS`)
DF_ID_statS$`DS` = factor(DF_ID_statS$`DS`, levels(DF_ID_statS$`DS`)[c(4,2,3,1)])
levels(DF_ID_statS$`DS`) = c('no', 'moderate', 'severe', 'intense')

DF_ID_statS$`AF` = factor(DF_ID_statS$`AF`)
DF_ID_statS$`AF` =  factor(DF_ID_statS$`AF`, levels(DF_ID_statS$`AF`)[c(3,2,1)])
levels(DF_ID_statS$`AF`) = c('no', 'low', 'high')

DF_ID_statS = DF_ID_statS[order(DF_ID_statS$`AF`),]

###

DAT = DF_ID_statS[DF_ID_statS$LS %in% c("↗","↘"), ]
DAT = DAT[DAT$DS != "no", ]

levels(DAT$`DS`) =  c('no', 'moderate', 'severe', 'intense')

pLoT =
	ggplot(data = DAT, aes(x = as.numeric(variable)-1, y = mean, group = `unique_id`)) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 1, color = 'black') +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_ribbon(data = DF_ID_statS, aes(ymin = CI_lower, ymax = CI_upper, fill = `AF`), alpha = 0.25, show.legend = FALSE) +
	scale_fill_manual(values = rev(c('yellowgreen','orange','red'))) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS!="static \u2192" & DAT$AF!="no"), ]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS=="static \u2192" & DAT$AF!="no"), ]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS!="static \u2192" & DAT$AF=="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_line(size = 0.5, alpha = 1, linetype = 1, data = DAT[which(DAT$DS=="no"),]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), linetype = 1, color = 'red', data = DAT[which(DAT$DS!="no" & DAT$LS=="static \u2192" & DAT$AF=="no"),]) +
	labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous('Joint Effect\n\n', breaks = c(1, .5, 0, -.5, -1), limits = c(-1, 1), sec.axis = sec_axis(~ . + 10, name = 'Land Use Scenario\n')) +
	scale_x_continuous("\nTime Step", breaks = seq(0,75,25), sec.axis = sec_axis(~ . + 10, name = 'Climate Scenario\n')) +
	theme(axis.text.x = element_text(size = 10),  axis.text.y = element_text(size = 10),  axis.title.x = element_text(size = 12, lineheight = .25),  axis.title.y.right = element_text(size=12, lineheight = .25), axis.title.y = element_text(size = 12, lineheight = .25), axis.title.x.top = element_text(size=12, lineheight = .25),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.title = element_text(size = 10), legend.position = "bottom",  plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())


DAT_75_EE = subset(DAT, variable == "t 75")

Ed =  parse(text=paste("bold(E[d])"))
Ec =  parse(text=paste("bold(E[c])"))
B =  parse(text=paste("Base"))

DAT_R = DF_ID_statS[DF_ID_statS$LS %in% c("↗","→","↘"), ]

DAT_RL = DAT_R[DAT_R$DS == "no", ]
DAT_RM = DAT_R[DAT_R$DS == "no", ]
DAT_RH = DAT_R[DAT_R$DS == "no", ]

DAT_RL$DS = 'moderate'
DAT_RM$DS = 'severe'
DAT_RH$DS = 'intense'

DAT_R = rbind(DAT_RL, DAT_RM, DAT_RH)
DAT_R$`DS` = factor(DAT_R$`DS`, levels = c('moderate', 'severe', 'intense'))

pLoT2 =
	pLoT +
	# geom_line(size = .5, alpha = 1, color = 'black', data = DAT_R) +
	geom_label(data = subset(DAT_R, variable == "t 1" & AF == 'no' & LS %in% c("↗","↘")), label = c('d.','a.','e.','b.','f.','c.'), nudge_x = 5, nudge_y = 0.875, size = 2, label.r = unit(0, "pt"), label.size = 0, color = 'darkgrey') +
	facet_grid(LS ~ DS) +
	theme(strip.text = element_text(size=10), strip.text.y = element_text(angle = 0), strip.background = element_blank(), panel.border = element_rect(colour = NA, fill = NA))

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEE_new_RP.jpg", sep=""), pLoT2, width = 20, height = 15, units = "cm")

#####

DAT = DF_ID_statS[DF_ID_statS$LS %in% c("↑","↓"), ]
DAT = DAT[DAT$DS != "no", ]

levels(DAT$`DS`) = c('no', 'moderate', 'severe', 'intense')

pLoT =
	ggplot(data = DAT, aes(x = as.numeric(variable)-1, y = mean, group = `unique_id`)) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 1, color = 'black') +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_ribbon(data = DF_ID_statS, aes(ymin = CI_lower, ymax = CI_upper, fill = `AF`), alpha = 0.25, show.legend = FALSE) +
	scale_fill_manual(values = rev(c('yellowgreen','orange','red'))) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS!="static \u2192" & DAT$AF!="no"), ]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS=="static \u2192" & DAT$AF!="no"), ]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS!="static \u2192" & DAT$AF=="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_line(size = 0.5, alpha = 1, linetype = 1, data = DAT[which(DAT$DS=="no"),]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), linetype = 1, color = 'red', data = DAT[which(DAT$DS!="no" & DAT$LS=="static \u2192" & DAT$AF=="no"),]) +
	labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous('Joint Effect\n\n', breaks = c(1, .5, 0, -.5, -1), limits = c(-1, 1), sec.axis = sec_axis(~ . + 10, name = 'Land Use Scenario\n')) +
	scale_x_continuous("\nTime Step", breaks = seq(0,75,25), sec.axis = sec_axis(~ . + 10, name = 'Climate Scenario\n')) +
	theme(axis.text.x = element_text(size = 10),  axis.text.y = element_text(size = 10),  axis.title.x = element_text(size = 12, lineheight = .25),  axis.title.y.right = element_text(size=12, lineheight = .25), axis.title.y = element_text(size = 12, lineheight = .25), axis.title.x.top = element_text(size=12, lineheight = .25),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.title = element_text(size = 10), legend.position = "bottom",  plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

Ed =  parse(text=paste("bold(E[d])"))
Ec =  parse(text=paste("bold(E[c])"))
B =  parse(text=paste("Base"))

DAT_R = DF_ID_statS[DF_ID_statS$LS %in% c("↑","→","↓"), ]

DAT_RL = DAT_R[DAT_R$DS == "no", ]
DAT_RM = DAT_R[DAT_R$DS == "no", ]
DAT_RH = DAT_R[DAT_R$DS == "no", ]

DAT_RL$DS = 'moderate'
DAT_RM$DS = 'severe'
DAT_RH$DS = 'intense'

DAT_R = rbind(DAT_RL, DAT_RM, DAT_RH)
DAT_R$`DS` = factor(DAT_R$`DS`, levels = c('moderate', 'severe', 'intense'))

pLoT2 =
	pLoT +
	# geom_line(size = .5, alpha = 1, color = 'black', data = DAT_R) +
	facet_grid(LS ~ DS) +
	geom_label(data = subset(DAT_R, variable == "t 1" & AF == 'no' & LS %in% c("↑","↓")), label = c('d.','a.','e.','b.','f.','c.'), nudge_x = 5, nudge_y = 0.875, size = 2, label.r = unit(0, "pt"), label.size = 0, color = 'darkgrey') +
	theme(strip.text = element_text(size=10), strip.text.y = element_text(angle = 0), strip.background = element_blank(), panel.border = element_rect(colour = NA, fill = NA))

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEE_new_SW.jpg", sep=""), pLoT2, width = 20, height = 15, units = "cm")

#####

DAT = DF_ID_statS[DF_ID_statS$LS %in% c("→"), ]
DAT = DAT[DAT$DS != "no", ]

levels(DAT$`DS`) = c('no', 'moderate', 'severe', 'intense')

pLoT =
	ggplot(data = DAT, aes(x = as.numeric(variable)-1, y = mean, group = `unique_id`)) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 1, color = 'black') +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_ribbon(data = DF_ID_statS, aes(ymin = CI_lower, ymax = CI_upper, fill = `AF`), alpha = 0.25, show.legend = FALSE) +
	scale_fill_manual(values = rev(c('yellowgreen','orange','red'))) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS!="static \u2192" & DAT$AF!="no"), ]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS=="static \u2192" & DAT$AF!="no"), ]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), data = DAT[which(DAT$DS!="no"  & DAT$LS!="static \u2192" & DAT$AF=="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_line(size = 0.5, alpha = 1, linetype = 1, data = DAT[which(DAT$DS=="no"),]) +
	geom_line(size = 0.5, alpha = 1, aes(color = `AF`), linetype = 1, color = 'red', data = DAT[which(DAT$DS!="no" & DAT$LS=="static \u2192" & DAT$AF=="no"),]) +
	labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous('Joint Effect\n\n', breaks = c(1, .5, 0, -.5, -1), limits = c(-1, 1), sec.axis = sec_axis(~ . + 10, name = 'Land Use Scenario\n')) +
	scale_x_continuous("\nTime Step", breaks = seq(0,75,25), sec.axis = sec_axis(~ . + 10, name = 'Climate Scenario\n')) +
	theme(axis.text.x = element_text(size = 10),  axis.text.y = element_text(size = 10),  axis.title.x = element_text(size = 12, lineheight = .25),  axis.title.y.right = element_text(size=12, lineheight = .25), axis.title.y = element_text(size = 12, lineheight = .25), axis.title.x.top = element_text(size=12, lineheight = .25),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.title = element_text(size = 10), legend.position = "bottom",  plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

Ed =  parse(text=paste("bold(E[d])"))
Ec =  parse(text=paste("bold(E[c])"))
B =  parse(text=paste("Base"))

DAT_R = DF_ID_statS[DF_ID_statS$LS %in% c("↑","→","↓"), ]

DAT_RL = DAT_R[DAT_R$DS == "no", ]
DAT_RM = DAT_R[DAT_R$DS == "no", ]
DAT_RH = DAT_R[DAT_R$DS == "no", ]

DAT_RL$DS = 'moderate'
DAT_RM$DS = 'severe'
DAT_RH$DS = 'intense'

DAT_R = rbind(DAT_RL, DAT_RM, DAT_RH)
DAT_R$`DS` = factor(DAT_R$`DS`, levels = c('moderate', 'severe', 'intense'))

pLoT2 =
	pLoT +
	# geom_line(size = .5, alpha = 1, color = 'black', data = DAT_R) +
	facet_grid(LS ~ DS) +
	geom_label(data = subset(DAT_R, variable == "t 1" & AF == 'no' & LS %in% c("→")), label = c('a.','b.','c.'), nudge_x = 5, nudge_y = 0.875, size = 2, label.r = unit(0, "pt"), label.size = 0, color = 'darkgrey') +
	theme(strip.text = element_text(size=10), strip.text.y = element_text(angle = 0), strip.background = element_blank(), panel.border = element_rect(colour = NA, fill = NA))

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEE_new_STA.jpg", sep=""), pLoT2, width = 20, height = 15, units = "cm")
