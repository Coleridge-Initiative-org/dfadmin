#!/usr/bin/env bash

# Stop current service
sudo supervisorctl stop dfadmin && \

# Upgrade pip and install new requirements
env/bin/pip install --upgrade pip && \
env/bin/pip install --upgrade -r requirements.txt && \

# Check
env/bin/python manage.py check && \

# Migrate database
env/bin/python manage.py migrate && \

# Collect statics
env/bin/python manage.py collectstatic -c --no-input && \

# Start service again
sudo supervisorctl start dfadmin

ps aux | grep dfadmin
