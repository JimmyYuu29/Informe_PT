# Analisi del Progetto e Guida al Deployment

## Enterprise Document Generation Platform - Analisi Tecnica e Guida Operativa

**Versione:** 2.4
**Data:** Gennaio 2026
**Autore:** Sistema di Documentazione Automatica

---

## Indice

1. [Analisi dell'Architettura del Progetto](#1-analisi-dellarchitettura-del-progetto)
2. [Requisiti del Server](#2-requisiti-del-server)
3. [Schema 1: Deployment Standard (Consigliato)](#3-schema-1-deployment-standard-consigliato)
4. [Schema 2: Deployment con Docker](#4-schema-2-deployment-con-docker)
5. [Configurazione Nginx](#5-configurazione-nginx)
6. [Gestione con Systemd](#6-gestione-con-systemd)
7. [Monitoraggio e Manutenzione](#7-monitoraggio-e-manutenzione)
8. [Analisi delle Prestazioni e Limiti](#8-analisi-delle-prestazioni-e-limiti)
9. [Risoluzione dei Problemi](#9-risoluzione-dei-problemi)

---

## 1. Analisi dell'Architettura del Progetto

### 1.1 Struttura del Progetto

```
Informe_PT/
├── config/
│   └── yamls/
│       └── pt_review/          # Plugin di configurazione YAML
│           ├── manifest.yaml   # Metadati del plugin
│           ├── config.yaml     # Configurazione runtime
│           ├── fields.yaml     # Definizione campi input
│           ├── derived.yaml    # Campi calcolati
│           └── ...
├── modules/                    # Moduli core Python
│   ├── plugin_loader.py        # Caricamento plugin
│   ├── generate.py             # Generazione documenti
│   ├── context_builder.py      # Costruzione contesto
│   └── renderer_docx.py        # Rendering DOCX
├── templates/                  # Template DOCX
├── ui/
│   ├── api/
│   │   ├── backend/
│   │   │   └── main.py         # FastAPI backend
│   │   └── ui/
│   │       ├── index.html      # Frontend HTML
│   │       ├── app.js          # JavaScript applicazione
│   │       └── styles.css      # Stili CSS
│   └── streamlit_app/
│       ├── app.py              # Applicazione Streamlit
│       ├── form_renderer.py    # Renderer form
│       └── state_store.py      # Gestione stato
├── requirements.txt            # Dipendenze Python
└── output/                     # Directory output generati
```

### 1.2 Componenti Principali

| Componente | Tecnologia | Porta Default | Descrizione |
|------------|------------|---------------|-------------|
| **API Backend** | FastAPI + Uvicorn | 8000 | REST API per generazione documenti |
| **API Frontend** | HTML/JS/CSS | (servito da FastAPI) | Interfaccia web per API |
| **Streamlit App** | Streamlit | 8501 | Interfaccia web alternativa |

### 1.3 Flusso di Dati

```
[Utente] → [Nginx] → [FastAPI :8000] → [Generatore DOCX]
                  ↘
                   [Streamlit :8501] → [Generatore DOCX]
```

---

## 2. Requisiti del Server

### 2.1 Requisiti Hardware Minimi

| Risorsa | Minimo | Consigliato |
|---------|--------|-------------|
| **CPU** | 2 core | 4 core |
| **RAM** | 2 GB | 4 GB |
| **Disco** | 10 GB | 20 GB SSD |
| **Rete** | 10 Mbps | 100 Mbps |

### 2.2 Requisiti Software

- **Sistema Operativo:** Ubuntu 20.04 LTS o superiore
- **Python:** 3.10 o superiore
- **Nginx:** 1.18 o superiore
- **Git:** 2.25 o superiore

### 2.3 Porte da Aprire

| Porta | Servizio | Accesso |
|-------|----------|---------|
| 22 | SSH | Solo amministratori |
| 80 | HTTP | Pubblico |
| 443 | HTTPS | Pubblico |
| 8000 | FastAPI | Solo localhost |
| 8501 | Streamlit | Solo localhost |

---

## 3. Schema 1: Deployment Standard (Consigliato)

Questo schema utilizza un deployment diretto senza containerizzazione, ideale per server dedicati.

### Passo 1: Preparazione del Server

#### 1.1 Aggiornamento del Sistema

Apri un terminale SSH e connettiti al tuo server. Esegui i seguenti comandi per aggiornare il sistema:

```bash
# Aggiorna la lista dei pacchetti disponibili
sudo apt update

# Aggiorna tutti i pacchetti installati
sudo apt upgrade -y

# Installa i pacchetti necessari
sudo apt install -y python3.10 python3.10-venv python3-pip nginx git curl
```

**Spiegazione:**
- `apt update`: Scarica la lista aggiornata dei pacchetti
- `apt upgrade -y`: Aggiorna i pacchetti esistenti (-y conferma automaticamente)
- I pacchetti installati includono Python 3.10, ambiente virtuale, pip, nginx e git

#### 1.2 Verifica delle Versioni

```bash
# Verifica la versione di Python
python3 --version
# Output atteso: Python 3.10.x o superiore

# Verifica la versione di Nginx
nginx -v
# Output atteso: nginx version: nginx/1.18.x o superiore

# Verifica la versione di Git
git --version
# Output atteso: git version 2.25.x o superiore
```

### Passo 2: Clonazione del Repository

#### 2.1 Creazione della Directory di Lavoro

```bash
# Crea una directory per le applicazioni web
sudo mkdir -p /var/www

# Imposta i permessi per l'utente corrente
sudo chown -R $USER:$USER /var/www

# Spostati nella directory
cd /var/www
```

**Spiegazione:**
- `/var/www` è la directory standard per le applicazioni web su Linux
- `chown` cambia il proprietario della directory al tuo utente

#### 2.2 Clonazione del Repository da GitHub

```bash
# Clona il repository (sostituisci con il tuo URL)
git clone https://github.com/JimmyYuu29/Informe_PT.git

# Spostati nella directory del progetto
cd Informe_PT

# Verifica che i file siano stati scaricati
ls -la
```

**Spiegazione:**
- `git clone` scarica una copia completa del repository
- Il repository verrà creato in `/var/www/Informe_PT`

### Passo 3: Configurazione dell'Ambiente Python

#### 3.1 Creazione dell'Ambiente Virtuale

```bash
# Assicurati di essere nella directory del progetto
cd /var/www/Informe_PT

# Crea un ambiente virtuale Python
python3 -m venv venv

# Attiva l'ambiente virtuale
source venv/bin/activate
```

**Spiegazione:**
- Un ambiente virtuale isola le dipendenze del progetto dal sistema
- `source venv/bin/activate` attiva l'ambiente (vedrai `(venv)` nel prompt)

#### 3.2 Installazione delle Dipendenze

```bash
# Aggiorna pip all'ultima versione
pip install --upgrade pip

# Installa le dipendenze del progetto
pip install -r requirements.txt
```

**Spiegazione:**
- `requirements.txt` contiene la lista di tutte le librerie necessarie
- Questo comando le installa automaticamente nell'ambiente virtuale

#### 3.3 Verifica dell'Installazione

```bash
# Verifica che FastAPI sia installato
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Verifica che Streamlit sia installato
python -c "import streamlit; print(f'Streamlit {streamlit.__version__}')"
```

### Passo 4: Configurazione delle Directory

#### 4.1 Creazione delle Directory Necessarie

```bash
# Crea la directory per i file generati
mkdir -p /var/www/Informe_PT/output

# Imposta i permessi corretti
chmod 755 /var/www/Informe_PT/output

# Crea la directory per i log
sudo mkdir -p /var/log/informe_pt
sudo chown $USER:$USER /var/log/informe_pt
```

**Spiegazione:**
- La directory `output` conterrà i documenti DOCX generati
- I log aiuteranno a diagnosticare eventuali problemi

### Passo 5: Test Manuale delle Applicazioni

Prima di configurare i servizi, verifica che tutto funzioni:

#### 5.1 Test dell'API FastAPI

```bash
# Attiva l'ambiente virtuale (se non già attivo)
source /var/www/Informe_PT/venv/bin/activate

# Avvia l'API in modalità test
cd /var/www/Informe_PT
python -m uvicorn ui.api.backend.main:app --host 127.0.0.1 --port 8000
```

Apri un altro terminale e testa:

```bash
# Testa l'endpoint di health check
curl http://127.0.0.1:8000/health
# Output atteso: {"status":"healthy","version":"1.0.0",...}
```

Premi `Ctrl+C` per fermare l'applicazione.

#### 5.2 Test di Streamlit

```bash
# Avvia Streamlit in modalità test
cd /var/www/Informe_PT
streamlit run ui/streamlit_app/app.py --server.port 8501 --server.address 127.0.0.1
```

Apri un browser e vai a `http://[IP_SERVER]:8501` per verificare.

Premi `Ctrl+C` per fermare l'applicazione.

---

## 4. Schema 2: Deployment con Docker

Questo schema utilizza Docker per una maggiore portabilità e isolamento.

### Passo 1: Installazione di Docker

```bash
# Rimuovi versioni precedenti di Docker
sudo apt remove docker docker-engine docker.io containerd runc

# Installa i prerequisiti
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Aggiungi la chiave GPG di Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Aggiungi il repository Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installa Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Aggiungi l'utente corrente al gruppo docker
sudo usermod -aG docker $USER
newgrp docker

# Verifica l'installazione
docker --version
docker compose version
```

### Passo 2: Creazione del Dockerfile

Crea un file `Dockerfile` nella root del progetto:

```bash
cat > /var/www/Informe_PT/Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea directory output
RUN mkdir -p output && chmod 755 output

# Esponi le porte
EXPOSE 8000 8501

# Il comando sarà specificato nel docker-compose.yml
CMD ["python", "-m", "uvicorn", "ui.api.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### Passo 3: Creazione del docker-compose.yml

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

### Passo 4: Avvio dei Container

```bash
# Costruisci le immagini Docker
cd /var/www/Informe_PT
docker compose build

# Avvia i servizi in background
docker compose up -d

# Verifica che i container siano in esecuzione
docker compose ps

# Visualizza i log
docker compose logs -f
```

### Passo 5: Comandi Utili per Docker

```bash
# Ferma i servizi
docker compose down

# Riavvia i servizi
docker compose restart

# Ricostruisci dopo modifiche
docker compose build --no-cache
docker compose up -d

# Visualizza log di un servizio specifico
docker compose logs api
docker compose logs streamlit
```

---

## 5. Configurazione Nginx

Nginx fungerà da reverse proxy per entrambi i servizi, gestendo SSL e bilanciamento del carico.

### 5.1 Creazione della Configurazione Nginx

```bash
# Crea il file di configurazione per il sito
sudo nano /etc/nginx/sites-available/informe_pt
```

Inserisci il seguente contenuto:

```nginx
# Configurazione per Document Generation Platform
# Supporta sia API (FastAPI) che Streamlit

# Upstream per FastAPI
upstream fastapi_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# Upstream per Streamlit
upstream streamlit_backend {
    server 127.0.0.1:8501;
    keepalive 32;
}

# Server HTTP (reindirizza a HTTPS)
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;

    # Per certificato Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Reindirizza tutto il traffico HTTP a HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# Server HTTPS principale
server {
    listen 443 ssl http2;
    server_name tu-dominio.com www.tu-dominio.com;

    # Certificati SSL (da configurare con Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    # Configurazioni SSL moderne
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

    # Headers di sicurezza
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/informe_pt_access.log;
    error_log /var/log/nginx/informe_pt_error.log;

    # Dimensione massima upload
    client_max_body_size 50M;

    # Root per API (interfaccia principale)
    location / {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        # Timeout per generazione documenti
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Streamlit disponibile su /streamlit/
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

    # WebSocket per Streamlit
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

### 5.2 Attivazione della Configurazione

```bash
# Crea un link simbolico per abilitare il sito
sudo ln -s /etc/nginx/sites-available/informe_pt /etc/nginx/sites-enabled/

# Rimuovi la configurazione di default (opzionale)
sudo rm /etc/nginx/sites-enabled/default

# Testa la configurazione
sudo nginx -t
# Output atteso: nginx: configuration file /etc/nginx/nginx.conf test is successful

# Ricarica Nginx
sudo systemctl reload nginx
```

### 5.3 Configurazione SSL con Let's Encrypt

```bash
# Installa Certbot
sudo apt install -y certbot python3-certbot-nginx

# Crea la directory per la verifica
sudo mkdir -p /var/www/certbot

# Ottieni il certificato SSL
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Il certificato si rinnoverà automaticamente
# Verifica il timer di rinnovo
sudo systemctl status certbot.timer
```

### 5.4 Configurazione Senza SSL (Solo per Test Locali)

Se stai testando in locale senza SSL, usa questa configurazione semplificata:

```bash
# Crea configurazione semplificata
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

## 6. Gestione con Systemd

Systemd gestirà l'avvio automatico e il monitoraggio dei servizi.

### 6.1 Servizio per FastAPI

```bash
# Crea il file di servizio
sudo nano /etc/systemd/system/informe-pt-api.service
```

Inserisci:

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

# Sicurezza
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### 6.2 Servizio per Streamlit

```bash
# Crea il file di servizio
sudo nano /etc/systemd/system/informe-pt-streamlit.service
```

Inserisci:

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

# Sicurezza
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### 6.3 Configurazione dei Permessi

```bash
# Imposta il proprietario dei file
sudo chown -R www-data:www-data /var/www/Informe_PT

# Assicurati che l'ambiente virtuale sia accessibile
sudo chmod -R 755 /var/www/Informe_PT/venv

# Crea la directory dei log se non esiste
sudo mkdir -p /var/log/informe_pt
sudo chown www-data:www-data /var/log/informe_pt
```

### 6.4 Attivazione dei Servizi

```bash
# Ricarica la configurazione di systemd
sudo systemctl daemon-reload

# Abilita i servizi all'avvio
sudo systemctl enable informe-pt-api.service
sudo systemctl enable informe-pt-streamlit.service

# Avvia i servizi
sudo systemctl start informe-pt-api.service
sudo systemctl start informe-pt-streamlit.service

# Verifica lo stato
sudo systemctl status informe-pt-api.service
sudo systemctl status informe-pt-streamlit.service
```

### 6.5 Comandi Utili per la Gestione

```bash
# Ferma un servizio
sudo systemctl stop informe-pt-api.service

# Riavvia un servizio
sudo systemctl restart informe-pt-api.service

# Visualizza i log in tempo reale
sudo journalctl -u informe-pt-api.service -f

# Visualizza gli ultimi 100 log
sudo journalctl -u informe-pt-api.service -n 100

# Ricarica dopo modifiche ai file di servizio
sudo systemctl daemon-reload
sudo systemctl restart informe-pt-api.service
```

---

## 7. Monitoraggio e Manutenzione

### 7.1 Script di Health Check

```bash
# Crea lo script di monitoraggio
sudo nano /usr/local/bin/informe_pt_health_check.sh
```

```bash
#!/bin/bash

# Health check script per Informe PT
LOG_FILE="/var/log/informe_pt/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Controlla API
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)
if [ "$API_STATUS" != "200" ]; then
    echo "[$DATE] API DOWN - Status: $API_STATUS" >> $LOG_FILE
    sudo systemctl restart informe-pt-api.service
    echo "[$DATE] API restarted" >> $LOG_FILE
else
    echo "[$DATE] API OK" >> $LOG_FILE
fi

# Controlla Streamlit
STREAMLIT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8501)
if [ "$STREAMLIT_STATUS" != "200" ]; then
    echo "[$DATE] Streamlit DOWN - Status: $STREAMLIT_STATUS" >> $LOG_FILE
    sudo systemctl restart informe-pt-streamlit.service
    echo "[$DATE] Streamlit restarted" >> $LOG_FILE
else
    echo "[$DATE] Streamlit OK" >> $LOG_FILE
fi
```

```bash
# Rendi eseguibile lo script
sudo chmod +x /usr/local/bin/informe_pt_health_check.sh

# Aggiungi al crontab (ogni 5 minuti)
sudo crontab -e
# Aggiungi la riga:
# */5 * * * * /usr/local/bin/informe_pt_health_check.sh
```

### 7.2 Rotazione dei Log

```bash
# Crea configurazione logrotate
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

### 7.3 Aggiornamento del Progetto

```bash
# Script per aggiornamento sicuro
# Crea: /usr/local/bin/update_informe_pt.sh

#!/bin/bash
cd /var/www/Informe_PT

# Ferma i servizi
sudo systemctl stop informe-pt-api.service
sudo systemctl stop informe-pt-streamlit.service

# Backup
sudo tar -czf /var/backups/informe_pt_$(date +%Y%m%d).tar.gz /var/www/Informe_PT

# Pull dal repository
git pull origin main

# Attiva ambiente virtuale e aggiorna dipendenze
source venv/bin/activate
pip install -r requirements.txt

# Riavvia i servizi
sudo systemctl start informe-pt-api.service
sudo systemctl start informe-pt-streamlit.service

echo "Aggiornamento completato!"
```

---

## 8. Analisi delle Prestazioni e Limiti

### 8.1 Limiti di Concorrenza

| Configurazione | Utenti Simultanei | RAM Stimata | CPU Stimata |
|----------------|-------------------|-------------|-------------|
| **Minima** (2 worker) | 10-20 | 1 GB | 50% |
| **Standard** (4 worker) | 30-50 | 2 GB | 70% |
| **Ottimale** (8 worker) | 80-100 | 4 GB | 85% |

### 8.2 Fattori che Influenzano le Prestazioni

1. **Generazione Documenti**: Ogni generazione richiede ~500MB di RAM e ~2-5 secondi
2. **Template Complessi**: Template con molte tabelle aumentano il tempo di 50-100%
3. **File Upload**: L'upload di JSON grandi può impattare la memoria
4. **WebSocket Streamlit**: Ogni sessione mantiene una connessione attiva

### 8.3 Configurazione Ottimale per Carico

#### Server con 4GB RAM (30-50 utenti):

```ini
# /etc/systemd/system/informe-pt-api.service
ExecStart=... --workers 4

# /etc/nginx/nginx.conf
worker_processes 4;
worker_connections 1024;
```

#### Server con 8GB RAM (80-100 utenti):

```ini
# /etc/systemd/system/informe-pt-api.service
ExecStart=... --workers 8

# /etc/nginx/nginx.conf
worker_processes 8;
worker_connections 2048;
```

### 8.4 Raccomandazioni per l'Alta Disponibilità

Per carichi superiori a 100 utenti simultanei:

1. **Load Balancer**: Distribuisci il carico su più server
2. **CDN**: Usa Cloudflare o simili per contenuti statici
3. **Cache**: Implementa Redis per il caching delle sessioni
4. **Database**: Considera PostgreSQL per persistenza dati

---

## 9. Risoluzione dei Problemi

### 9.1 L'API non risponde

```bash
# Verifica lo stato del servizio
sudo systemctl status informe-pt-api.service

# Controlla i log
sudo journalctl -u informe-pt-api.service -n 50

# Verifica la porta
sudo netstat -tulpn | grep 8000

# Testa manualmente
curl -v http://127.0.0.1:8000/health
```

### 9.2 Streamlit non carica

```bash
# Verifica WebSocket
curl -I http://127.0.0.1:8501

# Controlla la configurazione Nginx
sudo nginx -t

# Ricarica Nginx
sudo systemctl reload nginx
```

### 9.3 Errori di Permessi

```bash
# Correggi i permessi
sudo chown -R www-data:www-data /var/www/Informe_PT
sudo chmod -R 755 /var/www/Informe_PT
sudo chmod -R 775 /var/www/Informe_PT/output
```

### 9.4 Problemi di Memoria

```bash
# Controlla l'uso della memoria
free -h
htop

# Riduci i worker se necessario
# Modifica il file di servizio e riavvia
```

### 9.5 Certificato SSL Scaduto

```bash
# Rinnova manualmente
sudo certbot renew

# Verifica lo stato
sudo certbot certificates
```

---

## Appendice A: Checklist di Deployment

- [ ] Sistema aggiornato (`apt update && apt upgrade`)
- [ ] Python 3.10+ installato
- [ ] Nginx installato
- [ ] Git installato
- [ ] Repository clonato in `/var/www/Informe_PT`
- [ ] Ambiente virtuale creato e dipendenze installate
- [ ] Directory output creata con permessi corretti
- [ ] Servizi systemd configurati e abilitati
- [ ] Nginx configurato come reverse proxy
- [ ] SSL configurato (se necessario)
- [ ] Health check configurato
- [ ] Log rotation configurata
- [ ] Firewall configurato

---

## Appendice B: Variabili d'Ambiente

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| `INFORME_PT_DEBUG` | `false` | Modalità debug |
| `INFORME_PT_WORKERS` | `4` | Numero di worker Uvicorn |
| `INFORME_PT_HOST` | `127.0.0.1` | Host di binding |
| `INFORME_PT_PORT` | `8000` | Porta di ascolto |

---

**Fine del documento**

Per domande o supporto, contattare il team di sviluppo.
