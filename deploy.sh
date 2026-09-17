#!/bin/bash
# TagStorm AI - VPS Deployment Script (fixed pip)
set -e

echo "=== TagStorm AI Deployment ==="

# Install system deps
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv > /dev/null 2>&1

# Create directories
sudo mkdir -p /var/www/hashtag-tool
sudo mkdir -p /var/www/hashtag-tool-sales

# Copy app files
sudo cp /tmp/hashtag-tool/app.py /var/www/hashtag-tool/
sudo cp /tmp/hashtag-tool/index.html /var/www/hashtag-tool/
sudo cp /tmp/hashtag-tool/sales.html /var/www/hashtag-tool-sales/index.html
sudo cp /tmp/hashtag-tool/requirements.txt /var/www/hashtag-tool/

# Set permissions
sudo chown -R ubuntu:ubuntu /var/www/hashtag-tool
sudo chown -R ubuntu:ubuntu /var/www/hashtag-tool-sales

# Create virtual environment and install deps
cd /var/www/hashtag-tool
python3 -m venv venv
./venv/bin/pip install -q flask gunicorn

# Setup systemd service
sudo tee /etc/systemd/system/tagstorm.service > /dev/null <<'EOF'
[Unit]
Description=TagStorm AI - Hashtag Generator Flask App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/hashtag-tool
Environment="PATH=/var/www/hashtag-tool/venv/bin"
ExecStart=/var/www/hashtag-tool/venv/bin/python /var/www/hashtag-tool/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Restart service
sudo systemctl daemon-reload
sudo systemctl enable tagstorm
sudo systemctl restart tagstorm

# Setup nginx
sudo tee /etc/nginx/sites-available/hashtag-tool > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/hashtag-tool /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=== Deployment Complete ==="
echo "Tool URL:  http://137.23.47.199"
echo "Sales URL: http://137.23.47.199/sales"
