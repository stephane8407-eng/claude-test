# SPV Treasure Map - Deployment Guide

Complete guide for deploying the SPV Treasure Map application to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Requirements](#server-requirements)
- [Initial Setup](#initial-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment](#deployment)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Monitoring](#monitoring)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Prerequisites

### Required Tools

- Docker (v24.0+)
- Docker Compose (v2.20+)
- Git
- SSH access to production server
- Domain name with DNS configured

### Required Accounts

- Docker Hub account (for image hosting)
- Sentry account (for error tracking)
- Domain registrar access (for DNS configuration)
- Server/cloud provider account

## Server Requirements

### Minimum Specifications

- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS (recommended) or similar Linux distribution
- **Network**: Public IP address with open ports 80, 443

### Recommended Specifications (Production)

- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: Load balancer with multiple instances

### Firewall Configuration

```bash
# Allow SSH (change port if using non-standard)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

## Initial Setup

### 1. Server Preparation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin -y

# Install required tools
sudo apt-get install -y git curl wget postgresql-client
```

### 2. Create Deployment User

```bash
# Create dedicated deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Set up SSH key authentication
sudo mkdir -p /home/deploy/.ssh
sudo cp ~/.ssh/authorized_keys /home/deploy/.ssh/
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

### 3. Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/spv-treasure-map
sudo chown deploy:deploy /opt/spv-treasure-map

# Switch to deploy user
sudo su - deploy

# Clone repository
cd /opt/spv-treasure-map
git clone https://github.com/your-org/spv-treasure-map.git .
```

## Environment Configuration

### 1. Create Production Environment File

```bash
cd /opt/spv-treasure-map/backend
cp .env.production.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with production values:

```bash
nano .env
```

**Critical settings to update:**

```bash
# Environment
ENVIRONMENT=production

# Database (use strong password!)
DATABASE_URL=postgresql://spv_admin:STRONG_PASSWORD_HERE@postgres:5432/spv_treasure_map

# Redis (use password!)
REDIS_URL=redis://:REDIS_PASSWORD_HERE@redis:6379/0

# Security (generate strong keys!)
JWT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
CSRF_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")

# CORS (your production domain)
CORS_ORIGINS=https://spvtreasurehunt.com

# API Keys
ANTHROPIC_API_KEY=your_production_anthropic_key
GOOGLE_API_KEY=your_google_api_key  # optional
GOOGLE_CSE_ID=your_google_cse_id    # optional

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
SENTRY_ENABLED=true

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### 3. Generate Secrets

```bash
# Generate JWT secret (64 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate CSRF secret (64 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate PostgreSQL password (32 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Redis password (32 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Update docker-compose.prod.yml

Create a `.env` file in the project root for Docker Compose:

```bash
cd /opt/spv-treasure-map
nano .env
```

Add Docker-specific variables:

```bash
POSTGRES_PASSWORD=your_postgres_password
REDIS_PASSWORD=your_redis_password
JWT_SECRET_KEY=your_jwt_secret
CSRF_SECRET_KEY=your_csrf_secret
CORS_ORIGINS=https://spvtreasurehunt.com
SENTRY_DSN=your_sentry_dsn
ANTHROPIC_API_KEY=your_anthropic_key
```

## Deployment

### Option 1: Manual Deployment

```bash
cd /opt/spv-treasure-map

# Run deployment script
bash scripts/production/deploy.sh
```

The deployment script will:
1. Run pre-deployment checks
2. Create database backup
3. Build Docker images
4. Deploy services with zero downtime
5. Run health checks
6. Complete post-deployment tasks

### Option 2: CI/CD Deployment

Push to `main` branch to trigger automatic deployment:

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

GitHub Actions will automatically:
1. Run tests
2. Build and push Docker images
3. Deploy to production server
4. Verify deployment health

### First-Time Deployment

For the first deployment, you'll need to:

1. **Initialize the database**:

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.db.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database initialized')
"
```

2. **Create initial admin user**:

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth import hash_password

db = SessionLocal()
admin = User(
    email='admin@spvtreasurehunt.com',
    hashed_password=hash_password('CHANGE_THIS_PASSWORD'),
    role_id=1,  # Admin role
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

## SSL/HTTPS Setup

### 1. Configure DNS

Point your domain to your server's IP:

```
A Record: spvtreasurehunt.com -> YOUR_SERVER_IP
A Record: www.spvtreasurehunt.com -> YOUR_SERVER_IP
```

### 2. Generate SSL Certificate

```bash
cd /opt/spv-treasure-map

# Start nginx temporarily
docker-compose -f docker-compose.prod.yml up -d nginx

# Generate certificate
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d spvtreasurehunt.com \
  -d www.spvtreasurehunt.com

# Restart nginx with SSL
docker-compose -f docker-compose.prod.yml restart nginx
```

### 3. Verify SSL

Test your SSL configuration:
- https://www.ssllabs.com/ssltest/
- https://securityheaders.com/

### 4. Auto-renewal

The certbot container automatically renews certificates. Verify it's running:

```bash
docker-compose -f docker-compose.prod.yml ps certbot
```

## Monitoring

### 1. Health Checks

```bash
# Run health check script
bash scripts/production/health_check.sh

# Check specific service
curl https://spvtreasurehunt.com/api/health
curl https://spvtreasurehunt.com/api/health/db
```

### 2. View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f postgres

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 3. Monitor Resources

```bash
# Container resource usage
docker stats

# Disk space
df -h

# Memory usage
free -h

# System load
top
```

### 4. Set Up External Monitoring

- **Uptime**: Use UptimeRobot or Pingdom
- **Errors**: Configure Sentry alerts
- **Performance**: Use New Relic or Datadog
- **Logs**: Set up log aggregation (ELK stack, Papertrail)

## Backup & Recovery

### Automated Backups

Backups are created automatically before each deployment. You can also run manual backups:

```bash
# Create backup
bash backend/scripts/backup_database.sh

# List backups
ls -lh backend/backups/

# Backups are automatically rotated (kept for 7 days)
```

### Manual Backup

```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump \
  -U spv_admin spv_treasure_map > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup volumes
docker run --rm -v spv_postgres_data_prod:/data \
  -v $(pwd):/backup ubuntu tar czf /backup/postgres_data.tar.gz /data
```

### Restore from Backup

```bash
# Using restore script
bash backend/scripts/restore_database.sh backend/backups/spv_treasure_map_YYYYMMDD_HHMMSS.sql.gz

# Manual restore
gunzip -c backup.sql.gz | docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U spv_admin -d spv_treasure_map
```

### Offsite Backup

Set up automated offsite backups:

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM, upload to S3
0 2 * * * cd /opt/spv-treasure-map && \
  bash backend/scripts/backup_database.sh && \
  aws s3 cp backend/backups/ s3://your-bucket/backups/ --recursive --exclude "*" --include "spv_treasure_map_$(date +%Y%m%d)*.sql.gz"
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check container status
docker-compose -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### Database Connection Issues

```bash
# Test database connection
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U spv_admin -d spv_treasure_map -c "SELECT version();"

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

### SSL Certificate Issues

```bash
# Check certificate
openssl x509 -in nginx/ssl/live/spvtreasurehunt.com/cert.pem -text -noout

# Renew certificate manually
docker-compose -f docker-compose.prod.yml run --rm certbot renew

# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Check slow queries
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U spv_admin -d spv_treasure_map -c \
  "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Clear Redis cache
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHDB
```

### Rolling Back

```bash
# Automatic rollback
bash scripts/production/rollback.sh

# Or manual rollback
docker-compose -f docker-compose.prod.yml down
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml up -d --build
```

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check system resources
- Review Sentry alerts

**Weekly:**
- Review performance metrics
- Check disk space
- Review backup success

**Monthly:**
- Update dependencies
- Rotate secrets (JWT, API keys)
- Review security logs
- Test backup restoration

### Updating Dependencies

```bash
# Update Python packages
cd /opt/spv-treasure-map/backend
pip list --outdated

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling

**Vertical Scaling (increase resources):**

```bash
# Update docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

**Horizontal Scaling (add more instances):**

```bash
# Scale backend service
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Update nginx upstream
# Add more backend servers to nginx.conf
```

### Security Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull

# Rebuild with latest base images
docker-compose -f docker-compose.prod.yml build --no-cache --pull
docker-compose -f docker-compose.prod.yml up -d
```

## Production Checklist

Before going live:

- [ ] All environment variables configured
- [ ] Strong passwords and secrets generated
- [ ] Database initialized with schema
- [ ] SSL certificate installed and valid
- [ ] DNS configured correctly
- [ ] Firewall rules configured
- [ ] Backups tested and working
- [ ] Monitoring and alerts set up
- [ ] Error tracking (Sentry) configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] Team trained on deployment procedures
- [ ] Rollback procedure tested
- [ ] Disaster recovery plan documented

## Support

For deployment issues:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs`
2. Run health check: `bash scripts/production/health_check.sh`
3. Review this documentation
4. Check GitHub Issues
5. Contact DevOps team

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
