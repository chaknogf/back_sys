# Usar la imagen base oficial de MariaDB
FROM mariadb:latest

# Establecer variables de entorno para la configuración de MariaDB
ENV MYSQL_ROOT_PASSWORD=prometeus
ENV MYSQL_DATABASE=babylont

# Exponer el puerto 3306 para acceso externo
EXPOSE 3306
