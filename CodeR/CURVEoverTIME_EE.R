
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
levels(DF_ID_statS$`DS`) = c('no', 'low', 'medium', 'high')

DF_ID_statS$`AF` = factor(DF_ID_statS$`AF`)
DF_ID_statS$`AF` =  factor(DF_ID_statS$`AF`, levels(DF_ID_statS$`AF`)[c(3,2,1)])
levels(DF_ID_statS$`AF`) = c('no', 'low', 'high')

DF_ID_statS = DF_ID_statS[order(DF_ID_statS$`AF`),]

pLoT =
	ggplot(data = DF_ID_statS, aes(x = as.numeric(variable)-1, y = mean, group = `unique_id`)) +
	geom_hline(yintercept = 0, size = 0.25, linetype = 3, color = 'grey') +
	geom_vline(xintercept = 37.5, size = 0.25, linetype = 3, color = 'grey') +
	#geom_ribbon(data = DF_ID_statS, aes(ymin = CI_lower, ymax = CI_upper, fill = `AF`), alpha = 0.25, show.legend = FALSE) +
	scale_fill_manual(values = rev(c('yellowgreen','orange','red'))) +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), data = DF_ID_statS[which(DF_ID_statS$DS!="no"  & DF_ID_statS$LS!="static \u2192" & DF_ID_statS$AF!="no"), ]) +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), data = DF_ID_statS[which(DF_ID_statS$DS!="no"  & DF_ID_statS$LS=="static \u2192" & DF_ID_statS$AF!="no"), ]) +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), data = DF_ID_statS[which(DF_ID_statS$DS!="no"  & DF_ID_statS$LS!="static \u2192" & DF_ID_statS$AF=="no"), ]) +
	scale_color_manual(values = c('yellowgreen','orange','red')) +
	geom_line(size = 0.25, alpha = 1, linetype = 1, data = DF_ID_statS[which(DF_ID_statS$DS=="no"),]) +
	geom_line(size = 0.25, alpha = 1, aes(color = `AF`), linetype = 1, color = 'red', data = DF_ID_statS[which(DF_ID_statS$DS!="no" & DF_ID_statS$LS=="static \u2192" & DF_ID_statS$AF=="no"),]) +
	labs(color = "Adaptation", fill = "Adaptation") +
	panel_border(colour = "black", linetype = 1, remove = FALSE) +
	#scale_y_reverse(expression(atop(E[s(SA)]), ''), breaks = c(-1, 0, 1), limits = c(1, -1), sec.axis = sec_axis(~ . + 10, name = 'Land use Scenario')) +
	scale_y_continuous('Joint Effect\n\n', breaks = c(1, 0, -1), limits = c(1, -1), sec.axis = sec_axis(~ . + 10, name = 'Climatic Event Scenario\n'), trans = "reverse") +
	scale_x_continuous("\nTime", breaks = seq(0,50,50), sec.axis = sec_axis(~ . + 10, name = 'Land Use Scenario\n')) +
	theme(axis.text.x = element_text(size = 10),  axis.text.y = element_text(size = 10),  axis.title.x = element_text(size = 12, lineheight = .25),  axis.title.y.right = element_text(size=12, lineheight = .25), axis.title.y = element_text(size = 12, lineheight = .25), axis.title.x.top = element_text(size=12, lineheight = .25),  axis.ticks.x = element_line(size=0.5), axis.ticks.y = element_line(size=0.5), axis.text.x.top = element_blank(), axis.ticks.x.top = element_blank(), axis.text.y.right = element_blank(), axis.ticks.y.right = element_blank(), axis.line.x.top = element_blank(), axis.line.y.right = element_blank(), legend.title = element_text(size = 10), legend.position = "bottom",  plot.margin = unit(c(0.125, 0.125, 0.125, 0.125), "in"), aspect.ratio = 1/1.5, panel.border = element_blank())

Ed =  parse(text=paste("bold(E[d])"))
Ec =  parse(text=paste("bold(E[c])"))
B =  parse(text=paste("Base"))

pLoT2 =
	pLoT +
    #stat_smooth(method="lm", se = FALSE, colour = 'darkgrey', size = 0.25, lwd = 0.25) +
	#geom_rect(data = subset(DF_ID_statS, LS %in% c("static \u2192") & DS %in% c("no")), fill = NA, colour = "red", xmin = -Inf,xmax = Inf, ymin = -Inf, ymax = Inf, size = 1.25) +
	facet_grid(DS ~ LS) +
	#geom_text(label = B, data = subset(DF_ID_statS, DS == "no" & LS == "static \u2192" & variable == 't 1'), x=67.5, y=0.75, size=3.75, color='red') +
	#geom_text(label = Ed, data = subset(DF_ID_statS, DS != "no" & LS == "static \u2192" & variable == 't 1'), x=67.5, y=0.75, size=3.75) +
	#geom_text(label = Ec, data = subset(DF_ID_statS, DS == "no" & LS != "static \u2192" & variable == 't 1'), x=67.5, y=0.75, size=3.75) +
	#geom_rect(data = subset(DF_ID_statS, LS == "static \u2192" & variable == 't 1'), xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = Inf, fill=NA, color = 'black', linetype = 1) +
	#geom_rect(data = subset(DF_ID_statS, DS == "no" & variable == 't 1'), xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = Inf, fill=NA, color = 'black', linetype = 1) +
	theme(strip.text = element_text(size=10), strip.background = element_blank(), panel.border = element_rect(colour = NA, fill = NA))


ggsave(filename=paste("/home/lucas/Desktop/PhD/STRESSOR/Documents/PUB_3rd/R_GRAPHs/GridEE_new123.jpg", sep=""), pLoT2, width = 20, height = 15, units = "cm")
