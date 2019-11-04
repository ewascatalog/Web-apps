drop database if exists `EWAS_Catalog`;
create  database EWAS_Catalog;
grant select on EWAS_Catalog.* to 'ewas'@'%';
