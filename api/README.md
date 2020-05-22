# Yet an other markdown converter

> Some notes how to setup the flask socketio webserver on your own

## Prerequisites

Create a `config.json` file in the `/api` folder

```json
{
  "SECRET_KEY": "YOUR_SECRET_KEY_HERE",
  "GITHUB_USER": "YOUR_GITHUB_USERNAME_HERE",
  "GITHUB_PASSWORD": "YOUR_GITHUB_PASSWORD_HERE"
}
```

## Build Setup

```bash
# install build dependencies
sudo apt install virtualenv python3.8 python3.8-dev

# create a virtualenv
virtualenv -p /usr/bin/python3.8 venv

# activate virtualenv
. venv/bin/activate

# install dependencies
pip3 install -r requirements.txt

# serve at 127.0.0.1:5000
gunicorn --worker-class eventlet --bind 127.0.0.1:5000 wsgi:app --access-logfile - --error-logfile - --log-level debug
```

## Systemd Setup

Create a file `/etc/systemd/system/reedomeapi.service` with following content

```bash
[Unit]
Description=Gunicorn instance to serve reedomeapi
After=network.target

[Service]
User=<USER>
Group=www-data
WorkingDirectory=/home/<USER>/git/markdown-webapp/api
Environment="PATH=/home/<USER>/git/markdown-webapp/api/venv/bin"
ExecStart=/home/<USER>/git/markdown-webapp/api/venv/bin/gunicorn --worker-class eventlet --bind 127.0.0.1:5000 wsgi:app --workers 1 --threads 2 --access-logfile /var/log/reedomeapi/access.log --error-logfile /var/log/reedomeapi/error.log --log-level INFO
Restart=on-failure
RestartSec=2s

[Install]
WantedBy=multi-user.target
```

Start the service and enable the service

```bash
sudo systemctl start reedomeapi
sudo systemctl enable reedomeapi
```

## Setup Nginx with SSL

Install dependencies from Ubuntu repository

```bash
sudo apt install nginx-full certbot python-certbot-nginx
```

Setup nginx config file in `/etc/nginx/sites-enabled/api_example_com`

```cfg
server {
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $http_host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Port $server_port;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
