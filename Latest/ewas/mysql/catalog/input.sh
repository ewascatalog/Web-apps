#!/bin/bash

mysql EWAS_Catalog < table.sql
cd "./19-07-03/"
mysql EWAS_Catalog -e "LOAD DATA LOCAL INFILE 'studies.txt' INTO TABLE studies LINES TERMINATED BY '\n' IGNORE 1 LINES"
mysql EWAS_Catalog -e "LOAD DATA LOCAL INFILE 'results.txt' INTO TABLE results LINES TERMINATED BY '\n' IGNORE 1 LINES"
mysqldump EWAS_Catalog studies results > database.sql
