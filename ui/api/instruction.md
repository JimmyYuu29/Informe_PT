# API Deployment Instructions for Ubuntu Server

**Version:** 2.0
**Author:** Yihao Yu
**Last Updated:** 2026-01-03

---

## Overview

This document provides step-by-step instructions for deploying the Document Generation Platform API on an Ubuntu server. The API is built with FastAPI and serves both the REST API endpoints and the web UI.

---

## Prerequisites

- Ubuntu 20.04 LTS or later
- Python 3.10 or later
- sudo/root access
- Git installed

---

## Step 1: System Preparation

### Update system packages

```bash
sudo apt update && sudo apt upgrade -y
```

### Install Python and required system dependencies

```bash
sudo apt install -y python3 python3-pip python3-venv git curl
```

### Verify Python version

```bash
python3 --version  # Should be 3.10+
```

---

## Step 2: Clone the Repository

```bash
cd /opt
sudo git clone https://github.com/JimmyYuu29/Informe_PT.git
sudo chown -R $USER:$USER /opt/Informe_PT
cd /opt/Informe_PT
```

---

## Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 5: Verify Installation

### Test the application locally

```bash
cd /opt/Informe_PT
python -c "from modules.plugin_loader import list_plugins; print(list_plugins())"
```

Expected output: `['pt_review']`

---

## Step 6: Configure the API Server

### Option A: Run with Uvicorn (Development/Testing)

```bash
cd /opt/Informe_PT
source venv/bin/activate
uvicorn ui.api.backend.main:app --host 0.0.0.0 --port 8000
```

Access the API at: `http://your-server-ip:8000`

### Option B: Run with Gunicorn + Uvicorn Workers (Production)

```bash
pip install gunicorn
gunicorn ui.api.backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Step 7: Create Systemd Service (Production)

### Create service file

```bash
sudo nano /etc/systemd/system/informe-pt.service
```

### Add the following content:

```ini
[Unit]
Description=Informe PT Document Generation API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/Informe_PT
Environment="PATH=/opt/Informe_PT/venv/bin"
ExecStart=/opt/Informe_PT/venv/bin/gunicorn ui.api.backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Set proper permissions

```bash
sudo chown -R www-data:www-data /opt/Informe_PT
```

### Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable informe-pt
sudo systemctl start informe-pt
sudo systemctl status informe-pt
```

---

## Step 8: Configure Nginx as Reverse Proxy (Recommended)

### Install Nginx

```bash
sudo apt install -y nginx
```

### Create Nginx configuration

```bash
sudo nano /etc/nginx/sites-available/informe-pt
```

### Add the following content:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Static files caching
    location /static {
        proxy_pass http://127.0.0.1:8000/static;
        proxy_cache_valid 200 1d;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Increase body size for file uploads
    client_max_body_size 50M;
}
```

### Enable the site

```bash
sudo ln -s /etc/nginx/sites-available/informe-pt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 9: Configure Firewall (UFW)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable
sudo ufw status
```

---

## Step 10: SSL Certificate (Optional but Recommended)

### Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL certificate

```bash
sudo certbot --nginx -d your-domain.com
```

### Auto-renewal is enabled by default. Test it with:

```bash
sudo certbot renew --dry-run
```

---

## API Endpoints

Once deployed, the following endpoints are available:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI interface |
| `/health` | GET | Health check |
| `/plugins` | GET | List available plugins |
| `/plugins/{id}/schema` | GET | Get plugin schema |
| `/plugins/{id}/validate` | POST | Validate input data |
| `/plugins/{id}/generate` | POST | Generate document |
| `/download/{filename}` | GET | Download generated document |

---

## Troubleshooting

### Check service logs

```bash
sudo journalctl -u informe-pt -f
```

### Check Nginx logs

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Restart services

```bash
sudo systemctl restart informe-pt
sudo systemctl restart nginx
```

### Permission issues

```bash
sudo chown -R www-data:www-data /opt/Informe_PT
sudo chmod -R 755 /opt/Informe_PT
```

---

## Updating the Application

```bash
cd /opt/Informe_PT
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
sudo systemctl restart informe-pt
```

---

## Environment Variables (Optional)

You can configure the application using environment variables:

```bash
export INFORME_PT_DEBUG=false
export INFORME_PT_WORKERS=4
export INFORME_PT_HOST=0.0.0.0
export INFORME_PT_PORT=8000
```

Or add them to the systemd service file in the `[Service]` section:

```ini
Environment="INFORME_PT_DEBUG=false"
Environment="INFORME_PT_WORKERS=4"
```

---

## Security Considerations

1. **Always use HTTPS in production** - Configure SSL with Certbot
2. **Limit access** - Use firewall rules to restrict access
3. **Keep system updated** - Regularly update Ubuntu and Python packages
4. **Monitor logs** - Set up log monitoring for suspicious activity
5. **Backup data** - Regular backups of configuration and generated documents

---

## Support

For issues and feature requests, please contact:

**Yihao Yu**
Consultor en Innovacion e Inteligencia Artificial
Forvis Mazars - Auditoria & Assurance - Sustainability
Email: yihao.yu@mazars.es
