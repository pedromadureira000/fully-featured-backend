# connect ssh
``
chmod 400 ~/.ssh/zap_ass.pem
ssh -i ~/.ssh/zap_ass.pem ubuntu@<ip>
``

# Check system version
``
cat /etc/os-release
``

# Update system packages
``
sudo apt-get update && sudo apt-get -y upgrade
sudo reboot
``

# Install Python 3 build tools
``
sudo apt install python3-pip python3-dev libpq-dev
``

# Install other stuff
``
sudo apt install make
sudo apt install nginx curl neovim
sudo apt install unzip
``

# Confirm GCC version:
``
gcc --version
``

# Install Python 3 (if needed) and venv(whatever version is the one the system is using)
``
sudo apt install python3.11 python3.11-venv
apt install python3.12-venv
``

# Install docker and postgres client
``
sudo apt install docker.io docker-compose postgresql-client-common postgresql-client
``

# Configure git
* Fork the project add the ssh public key to your github account.
_need to do it twice. Once for frontend and another for backend (since deploy key must be unique)_
``
git config --global user.name "PedroS3"
git config --global user.email "ph.websolucoes@gmail.com"
cd ~/.ssh
ssh-keygen -t ed25519 -C "ph.websolucoes@gmail.com"
chmod  400 ~/.ssh/fullyfeatured
chmod  400 ~/.ssh/fullyfeatured.pub
``
* Add public key ssh keys (https://github.com/settings/keys)
``
cat ~/.ssh/fullyfeatured.pub
``

# Add SSH Key to SSH Agent: Start the SSH agent if it's not already running, then add your SSH private key to it
``
eval `ssh-agent -s`
ssh-add ~/.ssh/fullyfeatured
``

# test if it's working
``
ssh -T git@github.com
``

# Clone the project
``
git clone git@github.com:pedromadureira000/fully-featured.git
git clone git@github.com:pedromadureira000/fully-featured-backend.git
``

# more git commands
* git pull => 'here is no tracking information for the current branch.'
`
git remote -v
git remote set-url origin git@github.com:pedromadureira000/fully-featured-backend.git
git remote add origin git@github.com:pedromadureira000/fully-featured-backend.git
git branch --set-upstream-to=origin/main main
`


# Other configs
``
nvim .bashrc
``

# Aliases
``
alias vim='nvim'
alias la='ls -A'
alias du='du -h --max-depth=1'
alias grep='grep --color=auto'
alias ..='cd ..'
alias gc='git commit -m'
alias gC='git checkout'
alias gp='git push'
alias ga='git add'
alias gs='git status'
alias gd='git diff'
alias gl='git log --graph --abbrev-commit'
alias gb='git branch'
alias journal='journalctl -e'
alias used_space='sudo du -h --max-depth=1 | sort -h'
alias gup='cd fully-featured-backend && git pull && source .venv/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput && cd .. && sudo systemctl restart gunicorn && sudo systemctl restart celeryd && echo "Done"'
``

# Run Postgres and Redis container
-----------------------------------------
You must run this in the same folder where the 'docker-compose.yml' file is.

## install compose manually (last time docker-compose command didn't worked)
* To download and install the Compose CLI plugin, adding it to all users, run:
``
DOCKER_CONFIG=${DOCKER_CONFIG:-/usr/local/lib/docker}
sudo mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
``

* Apply executable permissions to the binary:
``
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
``
* test it
``
docker compose version
``
* finally
``
sudo docker compose up -d
``

# Connect to default database and create the database that you will use
``
psql postgres://admin_ph:asdf@localhost:5432/postgres
create database fully_featured;
\q
``

# Initial project settings
``
cd fully-featured-backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp contrib/env-sample .env
vim .env
python3 manage.py migrate
python3 manage.py createsuperuser
``

Create systemd socket for Gunicorn
-----------------------------------------

* Create the file with:

``
sudo nvim /etc/systemd/system/gunicorn.socket
``

* Then copy this to that file

``
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
``

Create systemd service for Gunicorn
-----------------------------------------

* Create the file with:

``
sudo nvim /etc/systemd/system/gunicorn.service
``

* Then copy this to that file and edit the user field and working directory path

``
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fully-featured-backend
ExecStart=/home/ubuntu/fully-featured-backend/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock fully_featured.wsgi:application

[Install]
WantedBy=multi-user.target
``

Start and enable the Gunicorn socket
-----------------------------------------
``
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
``

Check the Gunicorn socket’s logs 
-----------------------------------------

``
sudo journalctl -u gunicorn.socket
``

Test socket activation
-----------------------------------------

It will be dead. The gunicorn.service will not be active yet since the socket has not yet received any connections

``
sudo systemctl status gunicorn  
``

Test the socket activation
-----------------------------------------

It must return a html response

``
curl --unix-socket /run/gunicorn.sock localhost 
``

If you don't receive a html, check the logs. Check your /etc/systemd/system/gunicorn.service file for problems. If you make changes to the /etc/systemd/system/gunicorn.service file, reload the daemon to reread the service definition and restart the Gunicorn process:
-----------------------------------------

``
sudo journalctl -u gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
``

Configure Nginx to Proxy Pass to Gunicorn
-----------------------------------------
* Create the file

``
sudo nvim /etc/nginx/sites-available/fully-featured
``

* Paste the nginx configuration code, and edit the sever name with your server IP.
``
server {
        listen 80;
        # Above is the server IP
        server_name <your server ip or domain>;

        location = /favicon.ico { access_log off; log_not_found off; }

        location / {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
        }

        location /static/ {
            autoindex on;
            alias /home/ubuntu/fully-featured-backend/staticfiles/;
	    }
}
``

Enable the file by linking it to the sites-enabled directory:
-----------------------------------------

``
sudo ln -s /etc/nginx/sites-available/fully-featured /etc/nginx/sites-enabled
``

Test for syntax errors
-----------------------------------------

``
sudo nginx -t
``

Restart nginx
-----------------------------------------

``
sudo systemctl restart nginx
``

collectstatic
-----------------------------------------
``
cd /home/ubuntu/fully-featured-backend
python manage.py collectstatic
sudo systemctl restart gunicorn
``

Nginx serve static file and got 403 forbidden Problem
-----------------------------------------
* add permission (first try)
``
sudo chown -R :www-data /home/ubuntu/fully-featured-backend/staticfiles
``
* add permission (second try)
``
sudo usermod -a -G ubuntu www-data  # (adds the user "nginx" to the "ubuntu" group without removing them from their existing groups)
chmod 710 /home/ubuntu 
``

Restart nginx
-----------------------------------------

``
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl status nginx
``

Solving common errors
----------------------------------------
* Securit group
 - Add port 80 there
* ALLOWED_HOSTS (better set '\*' )
* Nginx Is Displaying a 502 Bad Gateway Error Instead of the Django Application
  - A 502 error indicates that Nginx is unable to successfully proxy the request. A wide range of configuration problems express themselves with a 502 error, so more information is required to troubleshoot properly.
  - The primary place to look for more information is in Nginx’s error logs. Generally, this will tell you what conditions caused problems during the proxying event. Follow the Nginx error logs by typing:
  ``
  sudo tail -F /var/log/nginx/error.log
  ``

frontend make build
----------------------------------------
* make web build and send it with scp
``
./build_apk.sh 54.87.198.44
./build_web.sh 54.87.198.44
scp -i ~/.ssh/zap_ass.pem ~/Projects/fully-featured-backend/flutter_web_app/version.json.zip ubuntu@54.87.198.44:/home/ubuntu/fully-featured-backend/flutter_web_app
``


Run redis
-----------------------------------------
## Manually
``
sudo docker ps -a
sudo docker start 61 # if 61 is the redis id
``
## Daemonizing Redis container
1. `sudo nvim /etc/systemd/system/redis.service`
``
[Unit]
Description=Redis container
Requires=docker.service
After=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker start -a fully-featured_redis_1

[Install]
WantedBy=default.target
``
* _OBS_: fully-featured_redis_1 is the container label. You can check it with `sudo docker ps -a`

2. Reload it
``
sudo systemctl daemon-reload
``

3. Enable and start the Redis service:
``
sudo systemctl enable redis
sudo systemctl start redis
``
4. check it
``
sudo systemctl status redis
``

Run celery
-----------------------------------------
## Just run it manualy
``
celery -A fully_featured worker -l INFO --pool=gevent --concurrency=8 --hostname=worker -E --queues=send_completion_to_user &
``

## Daemonizing Celery with systemd
https://ahmadalsajid.medium.com/daemonizing-celery-beat-with-systemd-97f1203e7b32

1. We will create a /etc/default/celeryd configuration file.
* `sudo nvim /etc/default/celeryd`

``
# The names of the workers. This example create one worker
CELERYD_NODES="worker1"

# The name of the Celery App, should be the same as the python file
# where the Celery tasks are defined
CELERY_APP="fully_featured"

# Log and PID directories
CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
CELERYD_PID_FILE="/var/run/celery/%n.pid"

# Log level
CELERYD_LOG_LEVEL=INFO

# Path to celery binary, that is in your virtual environment
CELERY_BIN=/home/ubuntu/fully-featured-backend/.venv/bin/celery
``

2. Now, create another file for the worker 
* `sudo nvim /etc/systemd/system/celeryd.service` with sudo privilege.
``
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fully-featured-backend
ExecStart=/home/ubuntu/fully-featured-backend/.venv/bin/celery -A fully_featured worker -l INFO --pool=gevent --concurrency=8 --hostname=worker -E --queues=send_completion_to_user
Restart=always

[Install]
WantedBy=multi-user.target
``

3. Now, we will create log and pid directories.
``
sudo mkdir /var/log/celery /var/run/celery
sudo chown ubuntu:ubuntu /var/log/celery /var/run/celery 
``

4. After that, we need to reload systemctl daemon. *Remember that, we should reload this every time we make any change to the service definition file.*
``
sudo systemctl daemon-reload
sudo systemctl restart celeryd
``

5.  To enable the service to start at boot, we will run. And start the service
``
sudo systemctl enable celeryd
sudo systemctl start celeryd
sudo systemctl status celeryd
``

6. To verify that everything is ok, we can check the log files
``
cat /var/log/celery/worker1.log
journalctl -xeu celeryd.service
systemctl status celeryd.service
``

Cronjobs
-----------------------------------------
Cronjob that removes all files from /tmp/temp_transcription_audio every 30 minutes,
1. instrall cron
``
sudo yum install cronie
``
2. `crontab -e`
``
*/30 * * * * find /tmp/temp_transcription_audio/ -type f -mmin +3 -delete
``

Install SSL (22-04)
-----------------------------------------
*OBS: Don't use UFW (You might lost SSH access 💀💀💀)*

* https://saturncloud.io/blog/recovering-ssh-access-to-amazon-ec2-instance-after-accidental-ufw-firewall-activation/
https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-22-04

## Checking stuff
* Check ubuntu version
``
lsb_release -a
``
* check ALLOWED_HOSTS on settings.py
* Check server_name on nginx config file

## Installing Certbot 
* make sure your snapd core is up to date
``
sudo snap install core; sudo snap refresh core
``
* Make sure certbot is in the correct version
``
sudo apt remove certbot
sudo snap install --classic certbot
``

## adding this (not sure if it's neeeded or not)
``
        location ^~ /.well-known/acme-challenge/ {
                allow all;
                alias /var/www/html/.well-known/acme-challenge/;
        }
``

## Point the A register from your domain to ec2 instance IP

## Delete any AAAA register, becouse certbot will try to use it instead of A @ register

## Obtaining an SSL Certificate
* run it (with nginx plugin)
``
sudo certbot --nginx -d pedromadureira.xyz
``

## Verifying Certbot Auto-Renewal
``
sudo systemctl status snap.certbot.renew.service
sudo certbot renew --dry-run
``

Next steps
-----------------------------------------
* update webhook on https://mega-api-painel.app.br/
``
https://pedromadureira.xyz/webhook/<uuid-like-code>
``
