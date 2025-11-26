# Nginx Configuration for SPV Treasure Map

This directory contains nginx configuration files for production deployment with SSL/HTTPS support.

## Directory Structure

```
nginx/
├── nginx.conf              # Main nginx configuration
├── conf.d/
│   └── spv-treasure-map.conf  # Site-specific configuration
├── ssl/                    # SSL certificates (created by Let's Encrypt)
└── README.md              # This file
```

## SSL Certificate Setup (Let's Encrypt)

### Initial Certificate Generation

1. **Start nginx without SSL first** (for ACME challenge):

```bash
# Temporarily use HTTP-only config or comment out SSL directives
docker-compose -f docker-compose.prod.yml up -d nginx
```

2. **Generate SSL certificate**:

```bash
# Replace with your actual domain
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d spvtreasurehunt.com \
  -d www.spvtreasurehunt.com
```

3. **Restart nginx with SSL enabled**:

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

### Automatic Certificate Renewal

The certbot container automatically renews certificates every 12 hours. No manual action required.

### Manual Certificate Renewal

If needed, you can manually renew:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

## Configuration Details

### Rate Limiting

- **API requests**: 100 requests/minute per IP (burst: 20)
- **Login attempts**: 5 requests/minute per IP (burst: 3)
- **Registration**: 3 requests/hour per IP (burst: 1)
- **Connections**: 10 concurrent connections per IP

### Security Headers

- `Strict-Transport-Security`: HSTS enabled (1 year)
- `X-Frame-Options`: Prevent clickjacking
- `X-Content-Type-Options`: Prevent MIME sniffing
- `X-XSS-Protection`: XSS filter enabled
- `Content-Security-Policy`: Restrict resource loading
- `Referrer-Policy`: Control referrer information

### SSL Configuration

- **Protocols**: TLS 1.2, TLS 1.3 only
- **Ciphers**: Modern, secure cipher suites
- **OCSP Stapling**: Enabled for faster certificate validation
- **Session Cache**: 10MB shared cache

### Gzip Compression

Enabled for:
- Text files (HTML, CSS, JavaScript, JSON)
- XML and RSS feeds
- Fonts
- SVG images

## Testing Configuration

### Test nginx configuration syntax:

```bash
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### Reload nginx without downtime:

```bash
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Monitoring

### View nginx logs:

```bash
# Access logs
docker-compose -f docker-compose.prod.yml logs -f nginx

# View log files directly
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/spv_access.log
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/spv_error.log
```

## Security Best Practices

1. **Keep nginx updated**: Regularly update to latest stable version
2. **Monitor logs**: Set up log aggregation and alerting
3. **Rate limiting**: Adjust limits based on traffic patterns
4. **SSL Labs**: Test SSL configuration at https://www.ssllabs.com/ssltest/
5. **Security headers**: Verify headers at https://securityheaders.com/

## Customization

### Changing Domain

Update in `conf.d/spv-treasure-map.conf`:
- `server_name` directives
- SSL certificate paths

### Adjusting Rate Limits

Edit in `nginx.conf`:
- `limit_req_zone` definitions
- Adjust rate and burst parameters

### Adding More Backends

Add to `nginx.conf`:

```nginx
upstream backend_api {
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

## Troubleshooting

### 502 Bad Gateway

- Check if backend container is running
- Verify backend health check: `curl http://localhost:8000/api/health`
- Check nginx error logs

### SSL Certificate Issues

- Verify certificate files exist in `/etc/nginx/ssl/`
- Check certificate expiry: `openssl x509 -in cert.pem -noout -dates`
- Ensure DNS is properly configured

### Rate Limiting Too Strict

- Increase rate in `limit_req_zone`
- Increase burst parameter in location blocks
- Check nginx error logs for "limiting requests" messages

## Production Checklist

- [ ] Domain DNS configured correctly
- [ ] SSL certificates generated and valid
- [ ] Rate limits configured appropriately
- [ ] Security headers tested
- [ ] Log rotation configured
- [ ] Monitoring and alerting set up
- [ ] Backup configuration files
- [ ] Test SSL configuration (SSLLabs)
- [ ] Test security headers (SecurityHeaders.com)
- [ ] Load testing completed
