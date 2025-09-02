import pulumi 
import pulumi_aws as aws 

#---------------
# Key Pair 
#---------------

key_pair = aws.ec2.KeyPair(
    "server_keypair",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDwa+VG4BJ1YT99n6jiwB3JB/FZO3zWM/YQa3K6Y/+syszi+kT6gi5+0frV6PvycXaG69DWNc9kXJkGwWBULmKQfn7miDGNgIDi6RISN/6kXebMr3++AveQHrWRs0Mx4uvOZnc/fEZD3abXetpQemU6JkmGJtDhAFgNk+8TdYzwoc/7QvDW/9qlHZ6XYBLgMlvLIfY2ej2Xf4uPEi574VFmXtp7wAhPaUe26SXI47SWE4CwNZeL52Rjniw6RcFtAHY0NsNJ1PEd97zl1hXtMHKJp9eaGhDvb2fu64ODIFL5uBrW4g6T6CR/I2cqG7oKRVeRFPbctPcR3SS/KmEhoCwn0qYoGluDdHEn0gtfFtwqe6oWGXSi3IN6iwMmK25TtRi1PrOYxVUuHtaApH0cy+FfrYwUxXSlxQ17dNkMD6VylfJwttBa2z+M/GQiIiLAU+PeyoVeK7qt+lbrnRSjYlWIV4+efwJR7c1Dnd1UKvDh3PmwWD/bGxloxGSTXPPsi89YwoTCDxOuKEhCTfLrezmDVyfP6dQOm8e90UYTt/d3DoSRtoAEgajLeWIvh5gK/wLkGThGWDhoYN4qpAuPQkUZovI3c47OXDLG8K1nSSXX3vI3XUEobEtIiU2foz7UImL68HE6uB43NKSNqBfQRKXO/gHCjtODn3K791eLutM6iw== root@roni"
)

#---------------
# VPC
#---------------

vpc = aws.ec2.Vpc(
    'poridhi-dev-ap-southeast-1-finance-prod',
    cidr_block ="10.0.0.0/16",
    tags ={"Name":"poridhi-dev-ap-southeast-1-finance-prod"}
)

pulumi.export("vpc_id", vpc.id)

#---------------
# Internet Gateway
#---------------

igw = aws.ec2.InternetGateway(
    "igw",
    vpc_id=vpc.id,
    tags={"Name":"igw"}
)
pulumi.export("igw_id", igw.id)

#---------------
# Public Subnet
#---------------
public_subnet = aws.ec2.Subnet(
    "public_subnet",
    vpc_id = vpc.id,
    cidr_block = "10.0.1.0/24",
    map_public_ip_on_launch = True,
    availability_zone = "ap-southeast-1a",
    tags={"Name": "public_subnet"}
)

pulumi.export("public_subnet_id", public_subnet.id)

#---------------
# Public Route Table
#---------------
 
public_rt = aws.ec2.RouteTable(
    "public_rt",
    vpc_id = vpc.id,
    routes=[
        {
            "cidr_block" :"0.0.0.0/0",
            "gateway_id" : igw.id
        }
    ],
    tags ={"Name":"public_rt"}
) 
#---------------
# Public Route Table association
#---------------

aws.ec2.RouteTableAssociation(
    "public_rt_association",
    subnet_id = public_subnet.id,
    route_table_id = public_rt.id
)

#---------------
# NAT Gateway
#---------------

nat_eip = aws.ec2.Eip("nat_eip")

nat_gw = aws.ec2.NatGateway(
    "nat_gw",
    allocation_id = nat_eip.id,
    subnet_id = public_subnet.id
)
pulumi.export("nat_gw_id", nat_gw.id)


#---------------
# Private Subnet
#---------------
private_subnet = aws.ec2.Subnet(
    "private_subnet",
    vpc_id = vpc.id,
    cidr_block = "10.0.2.0/24",
    map_public_ip_on_launch = False,
    availability_zone = "ap-southeast-1a",
    tags={"Name": "private_subnet"}
)

pulumi.export("private_subnet_id", private_subnet.id)

#---------------
# Private Route Table
#---------------
 
private_rt = aws.ec2.RouteTable(
    "private_rt",
    vpc_id = vpc.id,
    routes=[
        {
            "cidr_block" :"0.0.0.0/0",
            "gateway_id" : nat_gw.id
        }
    ],
    tags ={"Name":"private_rt"}
) 

#---------------
# Private Route Table association
#---------------

aws.ec2.RouteTableAssociation(
    "private_rt_association",
    subnet_id = private_subnet.id,
    route_table_id = private_rt.id
)


#---------------
# Public Security Group
#---------------

public_sg = aws.ec2.SecurityGroup(
    "public_sg",
    vpc_id = vpc.id,
    description ="Allow ssh, http, https from anywhere.",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress =[
        aws.ec2.SecurityGroupEgressArgs(
            protocol ="-1",
            from_port=0,
            to_port=0,
            cidr_blocks = ["0.0.0.0/0"]
        )
    ],
    tags={"Name":"public_sg"}
)

pulumi.export("public_sg_id", public_sg.id)

#---------------
# Private Security Group
#---------------

private_sg = aws.ec2.SecurityGroup(
    "private_sg",
    vpc_id = vpc.id,
    description ="Allow ssh only from Public SG.",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            security_groups=[public_sg.id]
        )
    ],
    egress =[
        aws.ec2.SecurityGroupEgressArgs(
            protocol ="-1",
            from_port=0,
            to_port=0,
            cidr_blocks = ["0.0.0.0/0"]
        )
    ],
    tags={"Name":"private_sg"}
)

pulumi.export("private_sg_id", private_sg.id)



#---------------
# Bastion Server
#---------------

bastion_server = aws.ec2.Instance(
    "bastion_server",
    ami ="ami-0b8607d2721c94a77",
    instance_type = "t2.micro",
    subnet_id = public_subnet.id,
    vpc_security_group_ids =[public_sg.id],
    associate_public_ip_address = True,
    key_name = key_pair.key_name,
    tags={"Name": "bastion_server"}
)
pulumi.export("bastion_server_id", bastion_server.id)

#---------------
# DB Server
#---------------

db_server = aws.ec2.Instance(
    "db_server",
    ami ="ami-0b8607d2721c94a77",
    instance_type = "t2.micro",
    subnet_id = private_subnet.id,
    vpc_security_group_ids =[private_sg.id],
    associate_public_ip_address = False,
    key_name = key_pair.key_name,
    tags={"Name": "db_server"}
)
pulumi.export("db_server_id", db_server.id)


pulumi.export("bastion_server_ip", bastion_server.public_ip)
pulumi.export("db_server_ip", db_server.private_ip)