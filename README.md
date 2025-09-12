# AWS Resources with Pulumi

This project provisions AWS infrastructure (EC2, MySQL, Node.js) using Pulumi.

## Prerequisites

* AWS CLI configured
* Pulumi installed
* SSH access to EC2 instances

## Setup & Deployment

Clone the repository and navigate to the Pulumi project:

```
git clone git@github.com:rashed081/aws_resources_with_pulumi.git
cd aws_resources_with_pulumi/pulumi_project
```

Configure AWS CLI:

```
aws configure  # Set AWS Access Key, Secret Key, region (ap-southeast-1), output format(json)
```

Create an EC2 key pair for SSH access and set permissions:

```
cd ~/.ssh/
aws ec2 create-key-pair --key-name MyKeyPair --output text --query 'KeyMaterial' > MyKeyPair.id_rsa
chmod 400 MyKeyPair.id_rsa

cd aws_resources_with_pulumi/pulumi_project
ssh-keygen -y -f ~/.ssh/MyKeyPair.id_rsa > MyKeyPair.pub
```

Deploy all resources with Pulumi:

```
pulumi up
```

## Access & Logs

SSH into servers:

```
ssh bastion-server   # bastion server
ssh db-server       # MySQL server
```

Check cloud-init logs for instance setup:

```
sudo cat /var/log/cloud-init-output.log
```

Check MySQL service status, configuration, and logs:

```
sudo systemctl status mysql
sudo cat /etc/mysql/mysql.conf.d/mysqld.cnf
sudo cat /var/log/mysql-check.log
sudo systemctl status mysql-check
```

## Cleanup

Destroy all provisioned resources:

```
pulumi destroy
```
