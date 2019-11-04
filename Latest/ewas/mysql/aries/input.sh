#!/bin/bash

mysql EWAS_Catalog < table.sql
cd "./catalog/"
mysql EWAS_Catalog -e "LOAD DATA LOCAL INFILE 'aries_ewas_fom1_sub_studies.txt' INTO TABLE aries_studies LINES TERMINATED BY '\n' IGNORE 1 LINES"
mysql EWAS_Catalog -e "LOAD DATA LOCAL INFILE 'aries_ewas_fom1_sub_results.txt' INTO TABLE aries_results LINES TERMINATED BY '\n' IGNORE 1 LINES"
mysqldump EWAS_Catalog aries_studies aries_results > database.sql
