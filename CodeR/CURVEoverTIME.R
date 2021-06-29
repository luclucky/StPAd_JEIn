
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

options(scipen=1)

theme_classicGRID = function (base_size = 11, base_family = "", base_line_size = base_size/22, base_rect_size = base_size/22) {theme_bw(base_size = base_size, base_family = base_family, base_line_size = base_line_size, base_rect_size = base_rect_size) %+replace% theme(panel.border = element_blank(), axis.line = element_line(colour = "black", size = rel(1)), legend.key = element_blank(), strip.background = element_rect(fill = "white", colour = "black", size = rel(2)), complete = TRUE, panel.grid.major.y = element_line(), panel.grid.major.x = element_blank(), panel.grid.minor.y = element_blank())}

theme_set(theme_classic())

###

###

load('/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_DATA/resDF_0255.Rda')

str(resDF)

resDF[is.na(resDF)] = 0

head(resDF)
tail(resDF)

DFtot = melt(resDF, id.vars = colnames(resDF)[1:5])

###

DF = DFtot

colnames(DF)
str(DF)
head(DF)
tail(DF)

DF_ID = unite(DF, unique_id, c(`LS`, `DS`, `AF`), sep =  " ", remove = FALSE)

head(DF_ID)

DF_ID = DF_ID[,c(1,7,8)]
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
DF_ID_statS$`LS` = factor(DF_ID_statS$`LS`, levels(DF_ID_statS$`LS`)[c(3,5,1,2,4)])
levels(DF_ID_statS$`LS`) = c('ramped \u2197', 'stepwise \u2191', 'consistent', 'stepwise \U2193', 'ramped \U2198')

DF_ID_statS$`DS` = factor(DF_ID_statS$`DS`)
DF_ID_statS$`DS` = factor(DF_ID_statS$`DS`, levels(DF_ID_statS$`DS`)[c(4,2,3,1)])
levels(DF_ID_statS$`DS`) = c('no', 'low', 'medium', 'high')

DF_ID_statS$`AF` = factor(DF_ID_statS$`AF`)
levels(DF_ID_statS$`AF`) = c('high', 'low', 'no')

pLoT =
	ggplot(data = DF_ID_statS, aes(x = as.numeric(variable)-1, y = mean, group = `unique_id`)) +
	geom_line(size = 0.25, alpha = 1, data = DF_ID_statS[which(DF_ID_statS$DS=="no"),]) +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), data = DF_ID_statS[which(DF_ID_statS$DS!="no"), ]) +
	geom_ribbon(data = DF_ID_statS, aes(ymin = CI_lower, ymax = CI_upper, fill = `AF`), alpha = 0.25, show.legend = FALSE) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	scale_fill_manual(values = c('yellowgreen','orange','red')) +
	labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	scale_y_continuous("Meta-population size \n", breaks = c(0, 2500, 5000, 7500), limits = c(0, 7500), sec.axis = sec_axis(~ . + 10, name = 'Land use Scenario \n')) +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	scale_x_continuous("\n Time Step", breaks = seq(0,200,50), sec.axis = sec_axis(~ . + 10, name = 'Climatic event Scenario \n')) +
	theme(axis.text.x = element_text(size = 8), axis.text.y = element_text(size = 8), axis.title.x = element_text(size = 12), axis.title.y = element_text(size = 12),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.text = element_text(size = 8), legend.title = element_text(size = 12), legend.position = "bottom", legend.direction = "vertical", plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

pLoT =
	pLoT +
    #stat_smooth(method="lm", se = FALSE, colour = 'darkgrey', size = 0.25, lwd = 0.25) +
	facet_grid(LS ~ DS) +
	theme(strip.text = element_text(size=8), strip.background = element_blank())

ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/Grid.jpg", sep=""), pLoT, width = 20, height = 20, units = "cm")
