# EWAS catalog web applications

There are two different versions of the application:

## 1 ewas

This version is for the general public only for query.

For some reason, only this version provides scripts for creating the mySQL database.

## 2 ewas_input

This version is for privileged users to login and upload data. 

For some reason, this version 
provides previously generated mySQL database files but not the scripts for creating them
(as in the query-only version above).

Provides scripts for performing SQL queries and exporting the results 
to text files that are used by the web application for responding to user queries.

Provides Docker service definitions for each web application container:
web application, NGINX web server, mySQL database manager.
It is unclear why service definitions are not included in
the query-only version above.

