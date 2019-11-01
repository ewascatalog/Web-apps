#!/bin/bash

mysql -e "LOAD DATA LOCAL INFILE 'cpgs.txt' INTO TABLE cpgs LINES TERMINATED BY '\n' IGNORE 1 LINES" --database=cpgs