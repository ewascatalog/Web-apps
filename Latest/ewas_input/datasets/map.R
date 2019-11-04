###################################################################
## Process EWAS                                                  ##
##                                                               ##
## James Staley                                                  ##
## University of Bristol                                         ##
## Email: james.staley@bristol.ac.uk                             ##
###################################################################

###################################################################
##### Set-up #####
###################################################################

##### Clear #####
rm(list=ls())

##### Options #####
options(stringsAsFactors=F)

##### Set working directory #####
setwd(".")

##### Libraries ####
suppressMessages(library(data.table))
suppressMessages(library(dplyr))

###################################################################
##### Methylation annotation #####
###################################################################

cpgs <- fread("./cpgs/cpgs_annotation.txt", header=T, sep="\t", data.table=F)

###################################################################
##### Process #####
###################################################################

##### Studies #####
studies <- read.delim("./input/19-07-03/studies.txt", header=T, sep="\t", colClasses="character")
names(studies) <- c("Author", "Consortium", "PMID", "Date", "Trait", "EFO", "Analysis", "Source", "Outcome", "Exposure", "Covariates", "Outcome_Units", "Exposure_Units", "Methylation_Array", "Tissue", "Further_Details", "N", "N_Cohorts", "Categories", "Age", "N_Males", "N_Females", "N_EUR", "N_EAS", "N_SAS", "N_AFR", "N_AMR", "N_OTH", "Study_ID")
any(grepl("'",studies)); apply(studies,2,function(x){any(grepl("'", x))})
studies[studies==""] <- "-"
write.table(studies, "./output/19-07-03/studies.txt", row.names=F, quote=F, sep="\t")

##### Results #####
results <- fread("./input/19-07-03/results.txt", header=T, sep="\t", data.table=F)
results <- results[,c("cpg", "beta", "se", "p", "details", "study_id")]
names(results) <- c("CpG", "Beta", "SE", "P", "Details", "Study_ID")
results$CpG <- gsub("\xa0", "", results$CpG)
results <- inner_join(cpgs, results, by="CpG")
results <- results[,c("CpG", "Location", "Chr", "Pos", "Gene", "Type", "Beta", "SE", "P", "Details", "Study_ID")]
apply(results,2,function(x){any(grepl("'", x))})
results$Beta <- as.character(round(as.numeric(results$Beta), 8))
results$SE <- as.character(round(as.numeric(results$SE), 8))
results$P <- as.character(signif(as.numeric(results$P), 3))
results <- results[!is.na(results$P),]
results <- results[as.numeric(results$P)>=0 & as.numeric(results$P)<=1,]
results[results==""] <- "-"; results[is.na(results)] <- "-"
write.table(results, "./output/19-07-03/results.txt", row.names=F, quote=F, sep="\t")

##### Overall #####
data <- inner_join(studies, results, by="Study_ID")
data <- data[, c("Author", "Consortium", "PMID", "Date", "Trait", "EFO", "Analysis", "Source", "Outcome", "Exposure", "Covariates", "Outcome_Units", "Exposure_Units", "Methylation_Array", "Tissue", "Further_Details", "N", "N_Cohorts", "Categories", "Age", "N_Males", "N_Females", "N_EUR", "N_EAS", "N_SAS", "N_AFR", "N_AMR", "N_OTH", "CpG", "Location", "Chr", "Pos", "Gene", "Type", "Beta", "SE", "P", "Details")]
data <- data[order(as.numeric(data$PMID)),]
write.table(data, paste0("./output/19-07-03/EWAS_Catalog_19-07-03.txt"), row.names=F, quote=F, sep="\t")
system(paste0("gzip ./output/19-07-03/EWAS_Catalog_19-07-03.txt"))

q("no")
