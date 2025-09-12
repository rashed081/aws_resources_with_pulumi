# Instructions to run this code

## Prerequisites

* Linux (Ubuntu recommended)
* AWS account and programmatic credentials
* `aws` CLI configured (`aws configure`) — set region to `ap-southeast-1`
* Pulumi installed and logged in
* Python 3.8+ and `python3 -m venv` available
* An SSH key-pair name you control

---

## Files & Scripts

**Where files live**

* `script/mysql-setup.sh` 
  * `setup.sh` — run on Node.js instance (cloned from your repo)
  * `mysql-check.sh` — connectivity check copied to `/usr/local/bin/check-mysql.sh`
* `__main__.py` — Pulumi stack that provisions infra and injects user-data



## Quick checklist — things you must edit before deploy

1. **Git repo URL** in `__main__.py` → `generate_nodejs_user_data()` (`git clone <YOUR_REPO_URL>`)
2. **AMI** in Pulumi EC2 instances (AMI ID in code is an example, replace with a current Ubuntu AMI for your region)
3. **Key pair name** (`key_name`) — must match the key you create/upload to AWS (example: `db-cluster`)
4. **MySQL user password** — do not keep `app_user` password empty or insecure; change it in `mysql-setup.sh`.
5. **Security group CIDR blocks** — avoid `0.0.0.0/0` for SSH in production; restrict to your IP.

---

## How to create an SSH key pair (example)

```bash
cd ~/.ssh
aws ec2 create-key-pair --key-name db-cluster --output text --query 'KeyMaterial' > db-cluster.id_rsa
chmod 400 db-cluster.id_rsa
```

---

## Pulumi setup & deploy (minimal)

```bash
# create project dir
mkdir service-infra && cd service-infra
python3 -m venv .venv
source .venv/bin/activate
pip install pulumi pulumi-aws
pulumi new aws-python  # follow prompts
# copy the supplied __main__.py into the project
pulumi up --yes
```

Notes:

* `__main__.py` reads `script/mysql-setup.sh` from a local path (`/root/code/script/mysql-setup.sh` in the example). Ensure Pulumi process can read that file or update the path.
* The Node.js instance user-data receives the DB private IP at creation time via `pulumi.Output.all(db.private_ip).apply(...)`.

---

## Post-deploy checks (SSH into nodes)

Check SSH config (Pulumi writes `~/.ssh/config`):

```bash
cat ~/.ssh/config
ssh nodejs-server      # connects to public Node.js instance
ssh db-server          # connects to DB via ProxyJump nodejs-server (per config)
```

View cloud-init/user-data logs (both instances):

```bash
sudo cat /var/log/cloud-init-output.log
```

MySQL status (DB server):

```bash
sudo systemctl status mysql
sudo cat /etc/mysql/mysql.conf.d/mysqld.cnf   # verify bind-address
```

mysql-check service (Node.js server):

```bash
sudo systemctl status mysql-check
sudo journalctl -u mysql-check -b --no-pager
sudo cat /var/log/mysql-check.log
```

Connectivity test from Node.js host:

```bash
# quick nc test
nc -zv $DB_PRIVATE_IP 3306
# or use mysql client (if installed)
mysql -h $DB_PRIVATE_IP -u app_user -p app_db
```

---

## Troubleshooting quick wins

* If `mysql-check` fails:

  * Confirm `/etc/environment` contains `DB_PRIVATE_IP` (set by user-data).
  * `sudo journalctl -u mysql-check -f` and inspect `/var/log/mysql-check.log`.
  * Ensure security group allows TCP 3306 from Node.js subnet.
  * Confirm MySQL is listening on `0.0.0.0` on the DB instance: `ss -tnlp | grep mysqld`.

* If Pulumi fails to read `mysql-setup.sh`:

  * Ensure path in `__main__.py` points to an accessible file at Pulumi run time.

* If instances can’t reach the internet from private subnet:

  * Verify NAT Gateway is created and private subnet route table points to the NAT Gateway.

---

## Optional: sample Node.js systemd service (example)

Drop this on the app server as `/etc/systemd/system/nodejs-app.service` and update `ExecStart`:

```ini
[Unit]
Description=Node.js App
After=network.target

[Service]
EnvironmentFile=/etc/environment
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/node /opt/myapp/index.js
Restart=on-failure
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Then enable/start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nodejs-app
```

---

---

## Useful commands summary

```bash
aws configure
pulumi up --yes
ssh nodejs-server
ssh db-server
sudo systemctl status mysql
sudo systemctl status mysql-check
sudo cat /var/log/cloud-init-output.log
sudo journalctl -u mysql-check
```
