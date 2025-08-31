#!/bin/bash
# AgriTrade Quick Setup Script for Ubuntu 22.04 LTS
# Run as root: sudo bash ubuntu_quick_setup.sh

set -e

echo "=== AgriTrade Production Setup for Ubuntu 22.04 LTS ==="
echo "This script will set up a complete production environment"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
apt install -y \
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
    python3-certbot-nginx \
    htop \
    vim \
    tmux

# Create application user
echo "👤 Creating application user..."
if ! id "agritrade" &>/dev/null; then
    adduser --disabled-password --gecos "" agritrade
    usermod -aG sudo agritrade
    echo "agritrade:$(openssl rand -base64 32)" | chpasswd
fi

# Set up PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32)

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE agritrade_db;
CREATE USER agritrade_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE agritrade_user SET client_encoding TO 'utf8';
ALTER ROLE agritrade_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE agritrade_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE agritrade_db TO agritrade_user;
\q
EOF

# Set up Redis
echo "🔴 Setting up Redis..."
systemctl start redis-server
systemctl enable redis-server

# Configure firewall
echo "🔥 Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
echo "y" | ufw enable

# Create application directory structure
echo "📁 Creating application directories..."
sudo -u agritrade mkdir -p /home/agritrade/{logs,backups}

# Clone repository
echo "📥 Cloning AgriTrade repository..."
sudo -u agritrade git clone https://github.com/ckbsinnogate/agritrade-backend.git /home/agritrade/agritrade-backend

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd /home/agritrade/agritrade-backend
sudo -u agritrade python3.10 -m venv venv
sudo -u agritrade /home/agritrade/agritrade-backend/venv/bin/pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
sudo -u agritrade /home/agritrade/agritrade-backend/venv/bin/pip install -r requirements.txt
sudo -u agritrade /home/agritrade/agritrade-backend/venv/bin/pip install gunicorn

# Generate Django secret key
SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')

# Create production environment file
echo "⚙️ Creating production configuration..."
sudo -u agritrade tee /home/agritrade/agritrade-backend/.env.production << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://agritrade_user:$DB_PASSWORD@localhost:5432/agritrade_db
DJANGO_SETTINGS_MODULE=myapiproject.settings_production
OPENAI_API_KEY=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
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-3-haiku:beta
WEATHER_API_KEY=
CORS_ALLOWED_ORIGINS=http://localhost:3000
EOF

# Create gunicorn configuration
sudo -u agritrade tee /home/agritrade/agritrade-backend/gunicorn.conf.py << 'EOF'
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
errorlog = "/home/agritrade/logs/gunicorn_error.log"
accesslog = "/home/agritrade/logs/gunicorn_access.log"
loglevel = "info"
EOF

# Run Django setup
echo "🔧 Running Django setup..."
cd /home/agritrade/agritrade-backend
sudo -u agritrade /home/agritrade/agritrade-backend/venv/bin/python manage.py migrate --settings=myapiproject.settings_production
sudo -u agritrade /home/agritrade/agritrade-backend/venv/bin/python manage.py collectstatic --noinput --settings=myapiproject.settings_production

# Set up Supervisor
echo "👮 Setting up Supervisor..."
tee /etc/supervisor/conf.d/agritrade.conf << 'EOF'
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

supervisorctl reread
supervisorctl update

# Set up Nginx
echo "🌐 Setting up Nginx..."
tee /etc/nginx/sites-available/agritrade << 'EOF'
server {
    listen 80 default_server;
    server_name _;

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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
EOF

# Enable nginx site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/agritrade /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
systemctl enable nginx

# Start services
echo "🚀 Starting services..."
supervisorctl start agritrade
systemctl restart nginx

# Create backup script
echo "💾 Setting up backup script..."
sudo -u agritrade tee /home/agritrade/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +"%Y%m%d_%H%M%S")
pg_dump -h localhost -U agritrade_user agritrade_db > /home/agritrade/backups/agritrade_$DATE.sql
find /home/agritrade/backups/ -name "*.sql" -mtime +7 -delete
EOF

chmod +x /home/agritrade/backup_db.sh

# Set up cron job for backups
echo "⏰ Setting up automated backups..."
(crontab -u agritrade -l 2>/dev/null; echo "0 2 * * * /home/agritrade/backup_db.sh") | crontab -u agritrade -

# Final system optimizations
echo "⚡ Applying system optimizations..."
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'net.core.somaxconn=65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog=65535' >> /etc/sysctl.conf
sysctl -p

echo ""
echo "🎉 AgriTrade production setup completed successfully!"
echo ""
echo "📊 Setup Summary:"
echo "- Database: PostgreSQL (agritrade_db)"
echo "- Database User: agritrade_user"
echo "- Database Password: $DB_PASSWORD"
echo "- Django Secret Key: $SECRET_KEY"
echo "- Application User: agritrade"
echo "- Web Server: Nginx (port 80)"
echo "- Application Server: Gunicorn (port 8000)"
echo "- Process Manager: Supervisor"
echo ""
echo "📝 Important Files:"
echo "- App Directory: /home/agritrade/agritrade-backend"
echo "- Environment File: /home/agritrade/agritrade-backend/.env.production"
echo "- Logs: /home/agritrade/logs/"
echo "- Backups: /home/agritrade/backups/"
echo ""
echo "🔧 Next Steps:"
echo "1. Update ALLOWED_HOSTS in .env.production with your domain"
echo "2. Get SSL certificate: sudo certbot --nginx -d yourdomain.com"
echo "3. Create Django superuser: sudo -u agritrade /home/agritrade/agritrade-backend/venv/bin/python /home/agritrade/agritrade-backend/manage.py createsuperuser --settings=myapiproject.settings_production"
echo ""
echo "🌐 Your API is now available at: http://$(curl -s ifconfig.me)/api/health/"
echo ""
echo "⚠️  Save this information securely!"
echo "Database Password: $DB_PASSWORD"
echo "Django Secret Key: $SECRET_KEY"
