# EWAS catalog web application *allowing data upload*

Compared to the query-only version, this version supports user login
and file upload.

## catalog
Code for the EWAS catalog web application
implemented using the Django framework.

## ewas
Configuration files.

## mysql
mySQL database referred to above (**datasets**).

## nginx
Docker and Django configuration files for the NGINX web server.

## Dockerfile
Docker configuration file.

## manage.py

## requirements.txt
Input to **Dockerfile** listing software dependencies.

__*The items below are not found in the query-only version of the web application.*__

## datasets
Creates data files for responding to user queries.
The files are created by querying the mySQL database.

## docker-compose.yml
Docker service definitions for each container:
web application, NGINX web server, mySQL database manager.
