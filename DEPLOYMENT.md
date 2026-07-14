# Prism Multi-Model Framework Demonstrator - Deployment Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Data
```bash
python generate_simple_data.py
```

### 3. Run Application
```bash
streamlit run app.py
```

**Access:** http://localhost:8501

---

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for Demos)

**Best for:** Quick demos, sharing with stakeholders, free hosting

#### Setup:

1. **Create GitHub Repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial Prism demo setup"
   git remote add origin https://github.com/YOUR_USERNAME/prism-demo.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Click "Create app"
   - Paste GitHub repo URL
   - Select main branch, `app.py` as main file
   - Click Deploy

3. **Access:** https://share.streamlit.io/YOUR_USERNAME/prism-demo

#### Pros:
- Free hosting
- Automatic updates from GitHub
- Built-in SSL
- Shareable public URL

#### Cons:
- Limited compute (1GB RAM)
- Public by default
- Cold starts

---

### Option 2: Docker (Development & Production)

**Best for:** Consistent environments, cloud deployment

#### Create Dockerfile:

Already included in project. Build and run:

```bash
# Build image
docker build -t prism-demo:latest .

# Run container
docker run -p 8501:8501 prism-demo:latest

# Access: http://localhost:8501
```

#### Docker Compose (with volumes):

```yaml
version: '3'
services:
  prism:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
```

Run: `docker-compose up`

---

### Option 3: AWS EC2

**Best for:** Scalable production deployment

#### Setup:

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (minimum)
   - Security Group: Allow ports 80, 443, 8501

2. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.10 python3-pip
   cd /home/ubuntu
   git clone https://github.com/YOUR_USERNAME/prism-demo.git
   cd prism-demo
   pip install -r requirements.txt
   ```

4. **Generate data:**
   ```bash
   python generate_simple_data.py
   ```

5. **Run with systemd (persistent):**

   Create `/etc/systemd/system/prism.service`:
   ```ini
   [Unit]
   Description=Prism Multi-Model Framework Demonstrator
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/prism-demo
   ExecStart=/usr/bin/python3 -m streamlit run app.py \
     --server.port 8501 \
     --server.address 0.0.0.0 \
     --logger.level=info
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable prism
   sudo systemctl start prism
   ```

6. **Setup reverse proxy (Nginx):**

   `/etc/nginx/sites-available/prism`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_buffering off;
       }
   }
   ```

   Enable and reload:
   ```bash
   sudo ln -s /etc/nginx/sites-available/prism /etc/nginx/sites-enabled/
   sudo nginx -s reload
   ```

7. **Setup SSL (Let's Encrypt):**
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

**Access:** https://your-domain.com

---

### Option 4: Heroku (Simple Deployment)

**Best for:** Rapid prototyping, low-cost hosting

#### Setup:

1. **Create Procfile:**
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

2. **Login and deploy:**
   ```bash
   heroku login
   heroku create prism-demo
   git push heroku main
   heroku logs --tail
   ```

**Access:** https://prism-demo.herokuapp.com

---

### Option 5: Google Cloud Run

**Best for:** Serverless, auto-scaling, minimal ops

#### Setup:

1. **Create cloudbuild.yaml:**
   ```yaml
   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/$PROJECT_ID/prism-demo', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'gcr.io/$PROJECT_ID/prism-demo']
   - name: 'gcr.io/cloud-builders/gke-deploy'
     args:
     - run
     - --filename=k8s/
     - --image=gcr.io/$PROJECT_ID/prism-demo
     - --location=us-central1
     - --cluster=prism-cluster
   ```

2. **Deploy:**
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

---

### Option 6: Azure Container Instances

**Best for:** Microsoft-centric environments

#### Setup:

```bash
# Build and push to Azure Container Registry
az acr build --registry prism --image prism-demo:latest .

# Deploy
az container create \
  --resource-group prism \
  --name prism-demo \
  --image prism.azurecr.io/prism-demo:latest \
  --ports 8501 \
  --memory 2
```

---

## Environment Configuration

### Set Environment Variables:

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FFCC00"
backgroundColor = "#000000"
secondaryBackgroundColor = "#F0F0F0"
textColor = "#000000"
font = "sans serif"

[server]
port = 8501
headless = true
runOnSave = false
logger.level = "info"

[client]
showErrorDetails = false
toolbarMode = "viewer"
```

---

## Performance Optimization

### 1. Data Caching
Application uses `@st.cache_resource` for:
- CSV data loading
- Vector search engine
- Graph building

### 2. Streamlit Configuration (config.toml):
```toml
[client]
maxMessageSize = 200

[logger]
level = "warning"

[server]
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
```

### 3. Production Deployment Notes:
- Use `--logger.level=warning` in production
- Enable authentication for sensitive data
- Monitor memory usage (vector models can be large)
- Use connection pooling for databases
- Consider CDN for static assets

---

## Monitoring & Troubleshooting

### Check Streamlit Logs:

```bash
# View recent logs
streamlit logs

# Tail logs
tail -f ~/.streamlit/logs/*.log

# Debug mode
streamlit run app.py --logger.level=debug
```

### Common Issues:

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | `pip install -r requirements.txt` |
| Data files not found | `python generate_simple_data.py` |
| Port already in use | `streamlit run app.py --server.port 8502` |
| Memory issues | Reduce model size or use streaming |
| Slow vector search | Cache embeddings, reduce document size |

### Performance Benchmarks:

| Operation | Time | Notes |
|-----------|------|-------|
| Load data | <1s | Cached after first load |
| Vector search | 200-500ms | First search triggers model download |
| Graph traversal | <100ms | In-memory, fast operations |
| Render dashboard | <2s | Plotly chart rendering |

---

## Security Considerations

### Production Checklist:

- [ ] Add authentication (Streamlit secrets)
- [ ] Use HTTPS/SSL only
- [ ] Sanitize user inputs
- [ ] Rate limit API endpoints
- [ ] Enable audit logging
- [ ] Use environment variables for secrets
- [ ] Remove debug mode in production
- [ ] Implement CORS restrictions
- [ ] Use CDN for static files
- [ ] Regular security updates

### Secrets Management:

Create `.streamlit/secrets.toml`:

```toml
[database]
username = "secret_username"
password = "secret_password"

[api]
key = "secret_api_key"
```

Access in code:
```python
db_username = st.secrets["database"]["username"]
```

---

## Maintenance & Updates

### Regular Tasks:

1. **Weekly:**
   - Review logs for errors
   - Monitor resource usage
   - Check data freshness

2. **Monthly:**
   - Update dependencies: `pip install --upgrade -r requirements.txt`
   - Regenerate synthetic data
   - Performance analysis

3. **Quarterly:**
   - Security audit
   - Load testing
   - Disaster recovery drill

### Automated Updates:

```bash
# Scheduled daily data refresh (crontab)
0 2 * * * cd /path/to/prism-demo && python generate_simple_data.py
```

---

## Scaling Considerations

### For 1000+ Concurrent Users:

1. **Use load balancer:** Nginx, AWS ALB
2. **Scale horizontally:** Multiple instances
3. **Cache aggressively:** Redis for session data
4. **Use CDN:** CloudFront, Cloudflare
5. **Optimize database:** Connection pooling
6. **Monitor metrics:** CloudWatch, DataDog

### Recommended Architecture:

```
                                  Clients
                                    |
                ┌───────────────────┼───────────────────┐
                |                   |                   |
            CDN (CloudFront)      LB (ALB)          Direct
                |                   |
        ┌───────┴──────────┬────────┼────────┬────────────┐
        |                  |        |        |            |
      Cache            App 1    App 2    App 3       Backup
    (CloudFront)       (EC2)    (EC2)    (EC2)       (DR)
```

---

## Support & Troubleshooting

### Get Help:

- 📧 Email: data-platform@example.com
- 💬 Slack: #prism-support
- 📖 Wiki: Internal documentation
- 🐛 Issues: GitHub Issues

### Debug Commands:

```bash
# Test connectivity
curl -v http://localhost:8501

# Check Python version
python --version

# List installed packages
pip list

# Check disk space
df -h

# Monitor resource usage
top

# Check service status
systemctl status prism
```

---

**Last Updated:** 2026-07-12  
**Version:** 1.0.0  
**Status:** Production Ready
