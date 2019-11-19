#!/bin/sh

set -a
. ../../../../settings.env
set +a


# Make new directory
mkdir -p ./input/$(date +"%y-%m-%d")
mkdir -p ./output/$(date +"%y-%m-%d")

# Export study information
docker exec -i ewascataloginput_db mysql -uroot -p${INPUT_DATABASE_ROOT_PASSWORD} ${INPUT_DATABASE_NAME} -e "select study.author, study.consortium, study.pmid, study.publication_date, study.trait, study.efo, study.analysis, study.source, analysis.outcome, analysis.exposure, analysis.covariates, analysis.outcome_unit, analysis.exposure_unit, analysis.array, analysis.tissue, analysis.further_details, participants.* from study join analysis on study.id=analysis.id join participants on study.id=participants.id;" > ./input/$(date +"%y-%m-%d")/studies.txt

# Export results
docker exec -i ewascataloginput_db mysql -uroot -p${INPUT_DATABASE_ROOT_PASSWORD} ${INPUT_DATABASE_NAME} -e "select * from results;" > ./input/$(date +"%y-%m-%d")/results.txt
