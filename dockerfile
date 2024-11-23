# Usar la imagen base oficial de MariaDB
FROM mariadb:latest

# Establecer variables de entorno para la configuración de MariaDB
ENV MYSQL_ROOT_PASSWORD=prometeus
ENV MYSQL_DATABASE=babylont

# Exponer el puerto 3306 para acceso externo
EXPOSE 3306
# Usa la imagen oficial de MySQL como base
FROM mysql:latest

# Establece las variables de entorno para la configuración inicial de MySQL
ENV MYSQL_ROOT_PASSWORD=turbo
ENV MYSQL_DATABASE=pluton
ENV MYSQL_USER=admin_user
ENV MYSQL_PASSWORD=turbo

# Expón el puerto 3309 para accesos remotos
EXPOSE 3309



# Inicia MySQL
CMD ["mysqld"]
