# Bookstore Management Software

This app is intended to be used by a small bookstore owner to allow them to add, edit, delete, and track their bookstore inventory, mark books as purchased, available, or unavailable, and search through their inventory. 

This app is configured to run with AWS. Follow the instructions below to install your own instance with the same configuration used for this repo.

Prerequisites:
* AWS EC2 Instance with security groups of HTTP (port 80), HTTPS (port 443), custom (port 8000), custom (port 5432)
* AWS Elastic IP Address
* AWS ECR
* AWS IAM roles with AmazonEC2ContainerRegistrPowerUser policy attached
* AWS RDS with PostgreSQL
* Docker

Connect to your EC2 instance:
```
ssh -i <your_private_key_name>.pem ubuntu@<your EC2 Instance Elastic IP Address>
```

Clone github repository:
```
git clone https://github.com/brocklarson/Bookstore_AWS.git
```

Create docker containers and migrations:
```
docker-compose up -d
```
```
docker-compose exec web python manage.py makemigrations --noinput
```
```
docker-compose exec web python manage.py migrate --noinput
```

Finally, launch your AWS EC2 instance using your public IPv4 DNS.
