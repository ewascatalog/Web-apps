# EWAS catalog web application

## catalog
Code for the EWAS catalog web application
implemented using the Django framework.

## datasets
Creates data files for responding to user queries.
The files are created by querying the mySQL database.

*(not found in '../ewas')*

## ewas
Configuration files.

## mysql
mySQL database referred to above (**datasets**).

*(in '../ewas', the corresponding 
folder contains scripts for creating this mySQL database)*

## nginx
Docker and Django configuration files for the NGINX web server.

## docker-compose.yml
Docker service definitions for each container:
web application, NGINX web server, mySQL database manager.

## Dockerfile
Docker configuration file.

## manage.py

## requirements.txt
Input to **Dockerfile** listing software dependencies.
