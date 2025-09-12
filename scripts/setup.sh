#!/bin/bash
exec > >(tee /var/log/setup.log) 2>&1


apt-get update
apt-get upgrade -y
apt-get install -y netcat-openbsd mysql-client


curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

mkdir -p /usr/local/bin
cd /tmp/scripts
cp check-mysql.sh /usr/local/bin/
chmod +x /usr/local/bin/check-mysql.sh
max_attempts=30 
attempt=0

while [ -z "$DB_PRIVATE_IP" ]; do
    if [ $attempt -ge $max_attempts ]; then
        echo "Timeout waiting for DB_PRIVATE_IP to be set"
        exit 1
    fi
    echo "Waiting for DB_PRIVATE_IP environment variable..."
    attempt=$((attempt + 1))
    sleep 10
    source /etc/environment
done

echo "DB_PRIVATE_IP is set to: $DB_PRIVATE_IP"
echo "Waiting for MySQL server to be ready..."
sleep 120

echo "Creating MySQL Connectivity Check Service"

cat > /etc/systemd/system/mysql-check.service << 'EOL'
[Unit]
Description=MySQL Connectivity Check Service
After=network.target
Wants=network.target

[Service]
Type=simple
EnvironmentFile=/etc/environment
ExecStart=/usr/local/bin/check-mysql.sh
Restart=on-failure
RestartSec=30
StandardOutput=append:/var/log/mysql-check.log
StandardError=append:/var/log/mysql-check.log

[Install]
WantedBy=multi-user.target
EOL


systemctl daemon-reload
systemctl enable mysql-check
systemctl start mysql-check

echo "MySQL check service has been started. You can check the status with: systemctl status mysql-check"
