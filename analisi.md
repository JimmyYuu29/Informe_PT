# 项目分析与部署指南

## 企业文档生成平台 - 技术分析与操作指南

**版本:** 2.4
**日期:** 2026年1月
**作者:** 自动文档系统

---

## 目录

1. [项目架构分析](#1-项目架构分析)
2. [服务器要求](#2-服务器要求)
3. [方案一：标准部署（推荐）](#3-方案一标准部署推荐)
4. [方案二：Docker 部署](#4-方案二docker-部署)
5. [Nginx 配置](#5-nginx-配置)
6. [Systemd 管理](#6-systemd-管理)
7. [监控与维护](#7-监控与维护)
8. [性能分析与限制](#8-性能分析与限制)
9. [故障排除](#9-故障排除)

---

## 1. 项目架构分析

### 1.1 项目结构

```
Informe_PT/
├── config/
│   └── yamls/
│       └── pt_review/          # YAML 配置插件
│           ├── manifest.yaml   # 插件元数据
│           ├── config.yaml     # 运行时配置
│           ├── fields.yaml     # 输入字段定义
│           ├── derived.yaml    # 计算字段
│           └── ...
├── modules/                    # Python 核心模块
│   ├── plugin_loader.py        # 插件加载器
│   ├── generate.py             # 文档生成
│   ├── context_builder.py      # 上下文构建
│   └── renderer_docx.py        # DOCX 渲染
├── templates/                  # DOCX 模板
├── ui/
│   ├── api/
│   │   ├── backend/
│   │   │   └── main.py         # FastAPI 后端
│   │   └── ui/
│   │       ├── index.html      # 前端 HTML
│   │       ├── app.js          # JavaScript 应用
│   │       └── styles.css      # CSS 样式
│   └── streamlit_app/
│       ├── app.py              # Streamlit 应用
│       ├── form_renderer.py    # 表单渲染器
│       └── state_store.py      # 状态管理
├── requirements.txt            # Python 依赖
└── output/                     # 生成文件输出目录
```

### 1.2 主要组件

| 组件 | 技术 | 默认端口 | 说明 |
|------|------|----------|------|
| **API 后端** | FastAPI + Uvicorn | 8000 | 文档生成 REST API |
| **API 前端** | HTML/JS/CSS | (由 FastAPI 提供) | API Web 界面 |
| **Streamlit 应用** | Streamlit | 8501 | 备选 Web 界面 |

### 1.3 数据流

```
[用户] → [Nginx] → [FastAPI :8000] → [DOCX 生成器]
                  ↘
                   [Streamlit :8501] → [DOCX 生成器]
```

---

## 2. 服务器要求

### 2.1 最低硬件要求

| 资源 | 最低 | 推荐 |
|------|------|------|
| **CPU** | 2 核 | 4 核 |
| **内存** | 2 GB | 4 GB |
| **磁盘** | 10 GB | 20 GB SSD |
| **网络** | 10 Mbps | 100 Mbps |

### 2.2 软件要求

- **操作系统:** Ubuntu 20.04 LTS 或更高版本
- **Python:** 3.10 或更高版本
- **Nginx:** 1.18 或更高版本
- **Git:** 2.25 或更高版本

### 2.3 需要开放的端口

| 端口 | 服务 | 访问权限 |
|------|------|----------|
| 22 | SSH | 仅管理员 |
| 80 | HTTP | 公开 |
| 443 | HTTPS | 公开 |
| 8000 | FastAPI | 仅本地 |
| 8501 | Streamlit | 仅本地 |

---

## 3. 方案一：标准部署（推荐）

本方案采用无容器化的直接部署方式，适用于专用服务器。

### 步骤 1：准备服务器

#### 1.1 系统更新

打开 SSH 终端连接到服务器，执行以下命令更新系统：

```bash
# 更新可用软件包列表
sudo apt update

# 更新所有已安装的软件包
sudo apt upgrade -y

# 安装必要的软件包
sudo apt install -y python3.10 python3.10-venv python3-pip nginx git curl
```

**说明：**
- `apt update`：下载更新的软件包列表
- `apt upgrade -y`：更新现有软件包（-y 自动确认）
- 安装的软件包包括 Python 3.10、虚拟环境、pip、nginx 和 git

#### 1.2 版本验证

```bash
# 验证 Python 版本
python3 --version
# 预期输出：Python 3.10.x 或更高

# 验证 Nginx 版本
nginx -v
# 预期输出：nginx version: nginx/1.18.x 或更高

# 验证 Git 版本
git --version
# 预期输出：git version 2.25.x 或更高
```

### 步骤 2：克隆代码库

#### 2.1 创建工作目录

```bash
# 创建 Web 应用目录
sudo mkdir -p /var/www

# 设置当前用户权限
sudo chown -R $USER:$USER /var/www

# 进入目录
cd /var/www
```

**说明：**
- `/var/www` 是 Linux 上 Web 应用的标准目录
- `chown` 将目录所有者更改为当前用户

#### 2.2 从 GitHub 克隆代码库

```bash
# 克隆代码库（替换为您的 URL）
git clone https://github.com/JimmyYuu29/Informe_PT.git

# 进入项目目录
cd Informe_PT

# 验证文件已下载
ls -la
```

**说明：**
- `git clone` 下载代码库的完整副本
- 代码库将创建在 `/var/www/Informe_PT`

### 步骤 3：配置 Python 环境

#### 3.1 创建虚拟环境

```bash
# 确保在项目目录中
cd /var/www/Informe_PT

# 创建 Python 虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

**说明：**
- 虚拟环境将项目依赖与系统隔离
- `source venv/bin/activate` 激活环境（提示符中会显示 `(venv)`）

#### 3.2 安装依赖

```bash
# 更新 pip 到最新版本
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

**说明：**
- `requirements.txt` 包含所有必需库的列表
- 此命令会自动在虚拟环境中安装它们

#### 3.3 验证安装

```bash
# 验证 FastAPI 已安装
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# 验证 Streamlit 已安装
python -c "import streamlit; print(f'Streamlit {streamlit.__version__}')"
```

### 步骤 4：配置目录

#### 4.1 创建必要的目录

```bash
# 创建生成文件目录
mkdir -p /var/www/Informe_PT/output

# 设置正确的权限
chmod 755 /var/www/Informe_PT/output

# 创建日志目录
sudo mkdir -p /var/log/informe_pt
sudo chown $USER:$USER /var/log/informe_pt
```

**说明：**
- `output` 目录将存放生成的 DOCX 文档
- 日志有助于诊断潜在问题

### 步骤 5：手动测试应用

在配置服务之前，验证一切正常：

#### 5.1 测试 FastAPI API

```bash
# 激活虚拟环境（如果尚未激活）
source /var/www/Informe_PT/venv/bin/activate

# 以测试模式启动 API
cd /var/www/Informe_PT
python -m uvicorn ui.api.backend.main:app --host 127.0.0.1 --port 8000
```

打开另一个终端进行测试：

```bash
# 测试健康检查端点
curl http://127.0.0.1:8000/health
# 预期输出：{"status":"healthy","version":"1.0.0",...}
```

按 `Ctrl+C` 停止应用。

#### 5.2 测试 Streamlit

```bash
# 以测试模式启动 Streamlit
cd /var/www/Informe_PT
streamlit run ui/streamlit_app/app.py --server.port 8501 --server.address 127.0.0.1
```

打开浏览器访问 `http://[服务器IP]:8501` 进行验证。

按 `Ctrl+C` 停止应用。

---

## 4. 方案二：Docker 部署

本方案使用 Docker 实现更好的可移植性和隔离性。

### 步骤 1：安装 Docker

```bash
# 移除旧版本 Docker
sudo apt remove docker docker-engine docker.io containerd runc

# 安装先决条件
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# 添加 Docker GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker compose version
```

### 步骤 2：创建 Dockerfile

在项目根目录创建 `Dockerfile` 文件：

```bash
cat > /var/www/Informe_PT/Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建 output 目录
RUN mkdir -p output && chmod 755 output

# 暴露端口
EXPOSE 8000 8501

# 命令将在 docker-compose.yml 中指定
CMD ["python", "-m", "uvicorn", "ui.api.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### 步骤 3：创建 docker-compose.yml

```bash
cat > /var/www/Informe_PT/docker-compose.yml << 'EOF'
version: '3.8'

services:
  api:
    build: .
    container_name: informe_pt_api
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
      - ./templates:/app/templates:ro
      - ./config:/app/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  streamlit:
    build: .
    container_name: informe_pt_streamlit
    command: streamlit run ui/streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    volumes:
      - ./output:/app/output
      - ./templates:/app/templates:ro
      - ./config:/app/config:ro
    restart: unless-stopped
    depends_on:
      - api
EOF
```

### 步骤 4：启动容器

```bash
# 构建 Docker 镜像
cd /var/www/Informe_PT
docker compose build

# 后台启动服务
docker compose up -d

# 验证容器正在运行
docker compose ps

# 查看日志
docker compose logs -f
```

### 步骤 5：Docker 常用命令

```bash
# 停止服务
docker compose down

# 重启服务
docker compose restart

# 修改后重新构建
docker compose build --no-cache
docker compose up -d

# 查看特定服务的日志
docker compose logs api
docker compose logs streamlit
```

---

## 5. Nginx 配置

Nginx 将作为两个服务的反向代理，处理 SSL 和负载均衡。

### 5.1 创建 Nginx 配置

```bash
# 创建站点配置文件
sudo nano /etc/nginx/sites-available/informe_pt
```

输入以下内容：

```nginx
# 文档生成平台配置
# 支持 API (FastAPI) 和 Streamlit

# FastAPI 上游
upstream fastapi_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# Streamlit 上游
upstream streamlit_backend {
    server 127.0.0.1:8501;
    keepalive 32;
}

# HTTP 服务器（重定向到 HTTPS）
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Let's Encrypt 证书验证
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # 将所有 HTTP 流量重定向到 HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# 主 HTTPS 服务器
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL 证书（使用 Let's Encrypt 配置）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 现代 SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 日志
    access_log /var/log/nginx/informe_pt_access.log;
    error_log /var/log/nginx/informe_pt_error.log;

    # 最大上传大小
    client_max_body_size 50M;

    # API 根路径（主界面）
    location / {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # 文档生成超时
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Streamlit 可通过 /streamlit/ 访问
    location /streamlit/ {
        rewrite ^/streamlit/(.*)$ /$1 break;
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_read_timeout 86400s;
    }

    # Streamlit WebSocket
    location /streamlit/_stcore/stream {
        rewrite ^/streamlit/(.*)$ /$1 break;
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
}
```

### 5.2 激活配置

```bash
# 创建符号链接启用站点
sudo ln -s /etc/nginx/sites-available/informe_pt /etc/nginx/sites-enabled/

# 移除默认配置（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t
# 预期输出：nginx: configuration file /etc/nginx/nginx.conf test is successful

# 重新加载 Nginx
sudo systemctl reload nginx
```

### 5.3 使用 Let's Encrypt 配置 SSL

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 创建验证目录
sudo mkdir -p /var/www/certbot

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 证书会自动续期
# 验证续期定时器
sudo systemctl status certbot.timer
```

### 5.4 无 SSL 配置（仅用于本地测试）

如果在本地测试不需要 SSL，使用此简化配置：

```bash
# 创建简化配置
sudo nano /etc/nginx/sites-available/informe_pt_local
```

```nginx
server {
    listen 80;
    server_name localhost;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    location /streamlit/ {
        rewrite ^/streamlit/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;
    }
}
```

---

## 6. Systemd 管理

Systemd 将管理服务的自动启动和监控。

### 6.1 FastAPI 服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/informe-pt-api.service
```

输入：

```ini
[Unit]
Description=Informe PT - FastAPI Backend
Documentation=https://github.com/JimmyYuu29/Informe_PT
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/Informe_PT
Environment="PATH=/var/www/Informe_PT/venv/bin"
ExecStart=/var/www/Informe_PT/venv/bin/python -m uvicorn ui.api.backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5
StandardOutput=append:/var/log/informe_pt/api.log
StandardError=append:/var/log/informe_pt/api_error.log

# 安全性
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### 6.2 Streamlit 服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/informe-pt-streamlit.service
```

输入：

```ini
[Unit]
Description=Informe PT - Streamlit Frontend
Documentation=https://github.com/JimmyYuu29/Informe_PT
After=network.target informe-pt-api.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/Informe_PT
Environment="PATH=/var/www/Informe_PT/venv/bin"
ExecStart=/var/www/Informe_PT/venv/bin/streamlit run ui/streamlit_app/app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always
RestartSec=5
StandardOutput=append:/var/log/informe_pt/streamlit.log
StandardError=append:/var/log/informe_pt/streamlit_error.log

# 安全性
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### 6.3 配置权限

```bash
# 设置文件所有者
sudo chown -R www-data:www-data /var/www/Informe_PT

# 确保虚拟环境可访问
sudo chmod -R 755 /var/www/Informe_PT/venv

# 创建日志目录（如果不存在）
sudo mkdir -p /var/log/informe_pt
sudo chown www-data:www-data /var/log/informe_pt
```

### 6.4 激活服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable informe-pt-api.service
sudo systemctl enable informe-pt-streamlit.service

# 启动服务
sudo systemctl start informe-pt-api.service
sudo systemctl start informe-pt-streamlit.service

# 验证状态
sudo systemctl status informe-pt-api.service
sudo systemctl status informe-pt-streamlit.service
```

### 6.5 管理常用命令

```bash
# 停止服务
sudo systemctl stop informe-pt-api.service

# 重启服务
sudo systemctl restart informe-pt-api.service

# 实时查看日志
sudo journalctl -u informe-pt-api.service -f

# 查看最近 100 条日志
sudo journalctl -u informe-pt-api.service -n 100

# 修改服务文件后重新加载
sudo systemctl daemon-reload
sudo systemctl restart informe-pt-api.service
```

---

## 7. 监控与维护

### 7.1 健康检查脚本

```bash
# 创建监控脚本
sudo nano /usr/local/bin/informe_pt_health_check.sh
```

```bash
#!/bin/bash

# Informe PT 健康检查脚本
LOG_FILE="/var/log/informe_pt/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查 API
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)
if [ "$API_STATUS" != "200" ]; then
    echo "[$DATE] API 异常 - 状态: $API_STATUS" >> $LOG_FILE
    sudo systemctl restart informe-pt-api.service
    echo "[$DATE] API 已重启" >> $LOG_FILE
else
    echo "[$DATE] API 正常" >> $LOG_FILE
fi

# 检查 Streamlit
STREAMLIT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8501)
if [ "$STREAMLIT_STATUS" != "200" ]; then
    echo "[$DATE] Streamlit 异常 - 状态: $STREAMLIT_STATUS" >> $LOG_FILE
    sudo systemctl restart informe-pt-streamlit.service
    echo "[$DATE] Streamlit 已重启" >> $LOG_FILE
else
    echo "[$DATE] Streamlit 正常" >> $LOG_FILE
fi
```

```bash
# 使脚本可执行
sudo chmod +x /usr/local/bin/informe_pt_health_check.sh

# 添加到 crontab（每 5 分钟）
sudo crontab -e
# 添加以下行：
# */5 * * * * /usr/local/bin/informe_pt_health_check.sh
```

### 7.2 日志轮转

```bash
# 创建 logrotate 配置
sudo nano /etc/logrotate.d/informe_pt
```

```
/var/log/informe_pt/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
```

### 7.3 项目更新

```bash
# 安全更新脚本
# 创建: /usr/local/bin/update_informe_pt.sh

#!/bin/bash
cd /var/www/Informe_PT

# 停止服务
sudo systemctl stop informe-pt-api.service
sudo systemctl stop informe-pt-streamlit.service

# 备份
sudo tar -czf /var/backups/informe_pt_$(date +%Y%m%d).tar.gz /var/www/Informe_PT

# 从仓库拉取
git pull origin main

# 激活虚拟环境并更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start informe-pt-api.service
sudo systemctl start informe-pt-streamlit.service

echo "更新完成！"
```

---

## 8. 性能分析与限制

### 8.1 并发限制

| 配置 | 并发用户 | 预估内存 | 预估 CPU |
|------|----------|----------|----------|
| **最小** (2 worker) | 10-20 | 1 GB | 50% |
| **标准** (4 worker) | 30-50 | 2 GB | 70% |
| **最优** (8 worker) | 80-100 | 4 GB | 85% |

### 8.2 影响性能的因素

1. **文档生成**：每次生成需要约 500MB 内存和 2-5 秒
2. **复杂模板**：包含多表格的模板会增加 50-100% 的时间
3. **文件上传**：大型 JSON 上传可能影响内存
4. **WebSocket Streamlit**：每个会话保持一个活动连接

### 8.3 负载优化配置

#### 4GB 内存服务器（30-50 用户）：

```ini
# /etc/systemd/system/informe-pt-api.service
ExecStart=... --workers 4

# /etc/nginx/nginx.conf
worker_processes 4;
worker_connections 1024;
```

#### 8GB 内存服务器（80-100 用户）：

```ini
# /etc/systemd/system/informe-pt-api.service
ExecStart=... --workers 8

# /etc/nginx/nginx.conf
worker_processes 8;
worker_connections 2048;
```

### 8.4 高可用性建议

对于超过 100 并发用户的负载：

1. **负载均衡器**：将负载分配到多台服务器
2. **CDN**：使用 Cloudflare 或类似服务处理静态内容
3. **缓存**：实现 Redis 进行会话缓存
4. **数据库**：考虑使用 PostgreSQL 进行数据持久化

---

## 9. 故障排除

### 9.1 API 无响应

```bash
# 验证服务状态
sudo systemctl status informe-pt-api.service

# 检查日志
sudo journalctl -u informe-pt-api.service -n 50

# 验证端口
sudo netstat -tulpn | grep 8000

# 手动测试
curl -v http://127.0.0.1:8000/health
```

### 9.2 Streamlit 无法加载

```bash
# 验证 WebSocket
curl -I http://127.0.0.1:8501

# 检查 Nginx 配置
sudo nginx -t

# 重新加载 Nginx
sudo systemctl reload nginx
```

### 9.3 权限错误

```bash
# 修复权限
sudo chown -R www-data:www-data /var/www/Informe_PT
sudo chmod -R 755 /var/www/Informe_PT
sudo chmod -R 775 /var/www/Informe_PT/output
```

### 9.4 内存问题

```bash
# 检查内存使用
free -h
htop

# 如有必要减少 worker 数量
# 修改服务文件并重启
```

### 9.5 SSL 证书过期

```bash
# 手动续期
sudo certbot renew

# 验证状态
sudo certbot certificates
```

---

## 附录 A：部署清单

- [ ] 系统已更新（`apt update && apt upgrade`）
- [ ] Python 3.10+ 已安装
- [ ] Nginx 已安装
- [ ] Git 已安装
- [ ] 代码库已克隆到 `/var/www/Informe_PT`
- [ ] 虚拟环境已创建并安装依赖
- [ ] output 目录已创建且权限正确
- [ ] systemd 服务已配置并启用
- [ ] Nginx 已配置为反向代理
- [ ] SSL 已配置（如需要）
- [ ] 健康检查已配置
- [ ] 日志轮转已配置
- [ ] 防火墙已配置

---

## 附录 B：环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `INFORME_PT_DEBUG` | `false` | 调试模式 |
| `INFORME_PT_WORKERS` | `4` | Uvicorn worker 数量 |
| `INFORME_PT_HOST` | `127.0.0.1` | 绑定主机 |
| `INFORME_PT_PORT` | `8000` | 监听端口 |

---

**文档结束**

如有问题或需要支持，请联系开发团队。
