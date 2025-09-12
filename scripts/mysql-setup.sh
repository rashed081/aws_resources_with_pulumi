#!/bin/bash
exec > >(tee /var/log/mysql-setup.log) 2>&1

apt update
apt upgrade -y
apt-get install -y mysql-server
sed -i 's/bind-address.*=.*/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
mysql -e "CREATE DATABASE app_db;"
mysql -e "CREATE USER 'appdb'@'%' IDENTIFIED BY 'appuser';"
mysql -e "GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'%';"
mysql -e "FLUSH PRIVILEGES;"

# Restart MySQL
systemctl restart mysql
