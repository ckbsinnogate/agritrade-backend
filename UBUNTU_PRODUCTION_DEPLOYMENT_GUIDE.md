# AgriTrade Production Deployment Guide
# Ubuntu Server Setup for Django API

## RECOMMENDED: Ubuntu 22.04 LTS Server

### System Requirements (Minimum)
- **RAM:** 2GB (4GB recommended)
- **Storage:** 20GB SSD (50GB recommended)
- **CPU:** 2 cores (4 cores recommended)
- **Network:** 1Gbps connection

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    wget \
    unzip \
    supervisor \
    ufw \
    certbot \
    python3-certbot-nginx

# Create application user
sudo adduser agritrade
sudo usermod -aG sudo agritrade

# Switch to application user
su - agritrade
```

### 2. PostgreSQL Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE agritrade_db;
CREATE USER agritrade_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE agritrade_user SET client_encoding TO 'utf8';
ALTER ROLE agritrade_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE agritrade_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE agritrade_db TO agritrade_user;
\q
```

### 3. Application Deployment

```bash
# Clone repository
cd /home/agritrade
git clone https://github.com/ckbsinnogate/agritrade-backend.git
cd agritrade-backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create production environment file
cat > .env.production << EOF
SECRET_KEY=your_very_secure_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://agritrade_user:your_secure_password_here@localhost:5432/agritrade_db
DJANGO_SETTINGS_MODULE=myapiproject.settings_production
OPENAI_API_KEY=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
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-3-haiku:beta
WEATHER_API_KEY=your_weather_api_key
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
EOF

# Run migrations
python manage.py migrate --settings=myapiproject.settings_production

# Collect static files
python manage.py collectstatic --noinput --settings=myapiproject.settings_production

# Create superuser
python manage.py createsuperuser --settings=myapiproject.settings_production
```

### 4. Gunicorn Configuration

```bash
# Create gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
preload_app = True
user = "agritrade"
group = "agritrade"
tmp_upload_dir = None
errorlog = "/home/agritrade/logs/gunicorn_error.log"
accesslog = "/home/agritrade/logs/gunicorn_access.log"
loglevel = "info"
EOF

# Create logs directory
mkdir -p /home/agritrade/logs
```

### 5. Supervisor Configuration

```bash
# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/agritrade.conf << EOF
[program:agritrade]
command=/home/agritrade/agritrade-backend/venv/bin/gunicorn myapiproject.wsgi:application -c /home/agritrade/agritrade-backend/gunicorn.conf.py
directory=/home/agritrade/agritrade-backend
user=agritrade
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/agritrade/logs/agritrade.log
environment=PATH="/home/agritrade/agritrade-backend/venv/bin"
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start agritrade
```

### 6. Nginx Configuration

```bash
# Create nginx site configuration
sudo tee /etc/nginx/sites-available/agritrade << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 50M;

    location /static/ {
        alias /home/agritrade/agritrade-backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/agritrade/agritrade-backend/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/agritrade /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL Certificate (Let's Encrypt)

```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 9. Redis Configuration (for caching)

```bash
# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Test Redis
redis-cli ping
```

### 10. Monitoring and Maintenance

```bash
# Create backup script
cat > /home/agritrade/backup_db.sh << EOF
#!/bin/bash
DATE=\$(date +"%Y%m%d_%H%M%S")
pg_dump -h localhost -U agritrade_user agritrade_db > /home/agritrade/backups/agritrade_\$DATE.sql
find /home/agritrade/backups/ -name "*.sql" -mtime +7 -delete
EOF

chmod +x /home/agritrade/backup_db.sh
mkdir -p /home/agritrade/backups

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /home/agritrade/backup_db.sh
```

## Alternative: Docker Deployment on Ubuntu 22.04

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker agritrade

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Use docker-compose.production.yml for deployment
```

## Cloud Provider Recommendations

1. **DigitalOcean Droplet** (Current choice - good)
   - 4GB RAM, 2 vCPUs, 80GB SSD ($24/month)
   - Ubuntu 22.04 LTS

2. **AWS EC2** (Enterprise grade)
   - t3.medium instance
   - Ubuntu 22.04 LTS AMI

3. **Vultr** (Cost-effective)
   - High Frequency 4GB instance
   - Ubuntu 22.04 LTS

4. **Linode** (Developer-friendly)
   - Shared 4GB instance
   - Ubuntu 22.04 LTS

## Performance Optimizations

```bash
# System optimizations
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.somaxconn=65535' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog=65535' | sudo tee -a /etc/sysctl.conf

# Apply optimizations
sudo sysctl -p
```

## Security Best Practices

1. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **SSH Key Authentication**
   ```bash
   # Disable password authentication
   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
   sudo systemctl restart ssh
   ```

3. **Fail2ban**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

This setup provides a robust, secure, and scalable production environment for your AgriTrade Django API.
