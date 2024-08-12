# FastAPI Deployment on AWS EC2

This guide provides step-by-step instructions for deploying a FastAPI application on an AWS EC2 instance.

## Prerequisites
- An AWS account with necessary permissions.
- A FastAPI application ready for deployment.
- Basic understanding of EC2, SSH, and Linux commands.

## Deployment Steps

### 1. Launch an EC2 Instance
1. Log in to your AWS Management Console.
2. Navigate to the EC2 service.
3. Click "Launch Instance".
4. Choose an appropriate Amazon Machine Image (AMI), such as Amazon Linux 2 or Ubuntu.
5. Select an instance type based on your application's requirements.
6. Configure network settings, security groups (allow inbound traffic for HTTP/HTTPS), and storage.
7. Create or select a key pair for SSH access.
8. Review and launch the instance.

### 2. Install Dependencies
After connecting to your EC2 instance via SSH, run the following commands:

Update the package manager:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip -y
sudo apt install nginx
sudo apt install python3-venv
mkdir -p /var/www/html/projectname
cd /var/www/html/projectname
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd /var/www/html/projectname
```
## 3.Run Your FastAPI Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
## 4. Setup FastAPI as a System Service
```bash
sudo nano /etc/systemd/system/fastapi.service
```
### Add the following content:
```bash
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/html/projectname
ExecStart=/var/www/html/projectname/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```
### Reload systemd and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start fastapi.service
sudo systemctl enable fastapi.service
```
### Check the status file :
```bash
sudo systemctl status fastapi.service
```
### 5.Now status the nginx file and apache file











