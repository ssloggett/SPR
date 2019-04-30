##############################################
## Set working directory and load libraries ##
##############################################
setwd('~/google drive/swets_maze/self paced reading')
library(plyr)
library(dplyr)
library(ggplot2)

###############################
## Define experiment factors ##
###############################
swets.factors = data.frame(condition = rep(c(1:3), times=2),
                           cond = paste(c(1:3), rep(c('d', 's'), each=3), sep='-'),
                           ambig = rep(c('ambig', 'low', 'high'), times=2),
                           qCond = rep(c('deep', 'surface'), each=3))
swets.factors$ambig = factor(swets.factors$ambig, levels = c('ambig', 'high', 'low'))
swets.factors$qCond = factor(swets.factors$qCond, levels = c('deep', 'surface'))

##################
## ggplot theme ##
##################
my.theme = theme(text = element_text(size = 14, colour = 'black', face = 'bold'),
                 axis.text = element_text(size = 10, colour = 'black', face = 'italic'),
                 axis.line = element_line(colour ='black'),
                 legend.text = element_text(size = 10, colour = 'black', face = 'italic'),
                 legend.key = element_rect(fill=NA, colour=NA),
                 strip.background = element_rect(fill = NA, colour = NA),
                 panel.background = element_rect(fill = NA),
                 panel.grid = element_blank(),
                 panel.spacing.x = unit(.5, 'cm'),
                 panel.border = element_rect(fill = NA, colour = NA),
                 plot.title = element_text(hjust = 0.5))

########################
## Read in data files ##
########################
deep.data = data.frame()
for(file in list.files(paste(getwd(),'deep','swets_deep_results',sep='/'))){
  if(!file%in%c('Icon\r', '')){
    if(nrow(deep.data)==0){deep.data = read.table(paste(getwd(),'deep','swets_deep_results',file,sep='/'), header=T, stringsAsFactors=F, fill=T)}
    else{
      if(file.info(paste(getwd(),'deep','swets_deep_results',file,sep='/'))$size>0){
        deep.data = rbind(deep.data, read.table(paste(getwd(),'deep','swets_deep_results',file,sep='/'), header=T, stringsAsFactors=F, fill=T))
      } 
    }
  }
}

surface.data = data.frame()
for(file in list.files(paste(getwd(),'surface','swets_surface_results',sep='/'))){
  if(file!='Icon\r'){
    if(nrow(surface.data)==0){surface.data = read.table(paste(getwd(),'surface','swets_surface_results',file,sep='/'), header=T, stringsAsFactors=F)}
    else{
      if(file.info(paste(getwd(),'surface','swets_surface_results',file,sep='/'))$size>0){
        surface.data = rbind(surface.data, read.table(paste(getwd(),'surface','swets_surface_results',file,sep='/'), header=T, stringsAsFactors=F))
      }
    }
  }
}

###################################
## Combine deep and surface data ##
###################################
deep.data$qCond = "d"
surface.data$qCond = "s"
data = rbind(deep.data, surface.data)
data$subj = paste(data$subj, data$qCond, sep='-')
data$cond = paste(data$condition, data$qCond, sep='-')

#################################################
###### ANALYSIS OF SELF-PACED READING DATA ######
#################################################
swets.data = subset(data, condition%in%c(1:3))

##################################################
## center critical region on reflexive position ##
##################################################
swets.items = unique(subset(swets.data, stimulustype!='Question', select = c('condition', 'item', 'word', 'position')))
swets.items$itemCond=paste(swets.items$item, swets.items$condition, sep='-')
swets.items$reflPosition = 0
for(item in unique(swets.items$itemCond)){
  swets.items$reflPosition[which(swets.items$itemCond==item)] = 
    swets.items$position[which(swets.items$itemCond==item)] -
    swets.items$position[which(swets.items$itemCond==item & swets.items$word%in%c('herself','himself'))]
}

#########################################
## Integrate critical region into data ##
#########################################
swets.data = merge(swets.data, swets.items, c('condition', 'item', 'word', 'position'))
swets.data$position = swets.data$reflPosition
swets.regions = data.frame(position=c(-7:4), region = c('The', 'maid', 'of', 'the', 'princess', 'who', 'scratched', 'herself', 'in', 'public', 'was', 'humiliated'))
swets.regions$region = factor(swets.regions$region, levels = c('The', 'maid', 'of', 'the', 'princess', 'who', 'scratched', 'herself', 'in', 'public', 'was', 'humiliated'))
swets.n = length(unique(swets.data$subj))/2

###############################
## Question by-subject means ##
###############################
swets.subj.qCond = ddply(swets.data, .(subj, qCond, position), summarize, rt=mean(rt,na.rm=1))
swets.qCond = ddply(swets.subj.qCond, .(qCond, position), summarize, sd=sd(rt, na.rm=1), rt=mean(rt,na.rm=1))
swets.qCond$se = swets.qCond$sd/sqrt(swets.n)
swets.qCond$qCondition = ifelse(swets.qCond$qCond == 's', 'surface', 'deep')
swets.qCond = merge(swets.qCond, swets.regions, 'position')

####################################
## Plot question by-subject means ##
####################################
ggplot(subset(swets.qCond, position%in%c(-7:4)), aes(y=rt, x=region, linetype = qCondition, group=qCondition)) +
  geom_line(size=1.1, position = position_dodge(width=0.1)) +
  geom_point(position=position_dodge(width=0.1)) +
  geom_errorbar(aes(ymin=rt-se, ymax=rt+se), width=0.1, size=.65, position=position_dodge(0.1)) +
  theme(legend.key.width = unit(1, 'cm'), 
        legend.position='bottom', 
        legend.direction="horizontal", 
        legend.box.spacing=unit(-.5, 'cm')) +
  my.theme + labs(y='Reading Time (ms)', x='', linetype='')

#########################################
## Ambiguity·Question by-subject means ##
#########################################
swets.subj.means = ddply(swets.data, .(subj, cond, position), summarize, rt=mean(rt,na.rm=1))
swets.means = ddply(swets.subj.means, .(cond, position), summarize, sd=sd(rt, na.rm=1), rt=mean(rt, na.rm=1))
swets.means$se = swets.means$sd/sqrt(swets.n)
swets.means = merge(swets.means, swets.factors, 'cond')
swets.means = merge(swets.means, swets.regions, 'position')

##############################################
## Plot ambiguity·question by-subject means ##
##############################################
ggplot(subset(swets.means, position%in%c(-4:4)), aes(y=rt, x=region, linetype = ambig, group=ambig)) +
  geom_line(size=1.1, position = position_dodge(width=0.1)) +
  geom_point(position=position_dodge(width=0.1)) +
  geom_errorbar(aes(ymin=rt-se, ymax=rt+se), width=0.1, size=.65, position=position_dodge(0.1)) +
  facet_grid(qCond~., scales='free') + 
  theme(legend.key.width = unit(1, 'cm'), 
        legend.position='bottom', 
        legend.direction="horizontal", 
        legend.box.spacing=unit(-.5, 'cm')) +
  my.theme + labs(y='Reading Time (ms)', x='', linetype='')

#######################################
###### ANALYSIS OF QUESTION DATA ######
#######################################
quest.data = subset(data, !is.na(correct) & condition%in%c(1:3))
quest.data$response = quest.data$correct
quest.data$correct[which(quest.data$cond=='1-d')] = 1

###################################
## Caclulate by-subject accuracy ##
###################################
# NB: ambiguous "correct" = "low attachment"
quest.subj.acc.means = ddply(quest.data, .(subj, cond), summarize, correct=mean(response,na.rm=1))
quest.acc.means = ddply(quest.subj.acc.means, .(cond), summarize, sd=sd(correct, na.rm=1), correct=mean(correct, na.rm=1))
quest.acc.means$se = quest.acc.means$sd/sqrt(swets.n)
quest.acc.means = merge(quest.acc.means, swets.factors, 'cond')

###################################
## Caclulate by-subject rt means ##
###################################
quest.subj.means = ddply(subset(quest.data, correct==1), .(subj, cond), summarize, rt=mean(rt,na.rm=1))
quest.means = ddply(quest.subj.means, .(cond), summarize, sd=sd(rt, na.rm=1), rt=mean(rt, na.rm=1))
quest.means$se = quest.means$sd/sqrt(swets.n)
quest.means = merge(quest.means, swets.factors, 'cond')

###########################
## Plot by-subject means ##
###########################
# Question accuracy plot
qAcc.plot = ggplot(quest.acc.means, aes(y=correct, x = qCond, fill = ambig)) +
  geom_bar(stat='identity', position=position_dodge(width=0.9), color='white') + 
  geom_errorbar(aes(ymin=correct-se, ymax=correct+se), width=0.1, position=position_dodge(width=0.9)) +
  scale_fill_manual(values = c( '#401F68', '#881c1c', '#003c6c')) + 
  labs(y='% Correct', x='', fill='') + theme(legend.position = 'none') + my.theme

# Question RT plot
qRT.plot = ggplot(quest.means, aes(y=rt, x = qCond, fill = ambig)) +
  geom_bar(stat='identity', position=position_dodge(width=0.9), color='white') + 
  geom_errorbar(aes(ymin=rt-se, ymax=rt+se), width=0.1, position=position_dodge(width=0.9)) +
  scale_fill_manual(values = c('#401F68', '#881c1c', '#003c6c')) + 
  labs(y='Reaction Time (ms)', x='', fill='') + my.theme + theme(legend.box.spacing=unit(0, 'cm'))

grid.arrange(qAcc.plot, qRT.plot, ncol=2, widths = c(1.3, 1.6125))
