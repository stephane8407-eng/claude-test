# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for automated testing and deployment.

## Workflows

### 1. Test Suite (`test.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches
- Pushes to `main` or `develop` branches

**Jobs:**
- **Lint**: Code quality checks (Black, flake8, mypy)
- **Security**: Security vulnerability scanning (safety, Bandit)
- **Test**: Run all test suites (Week 1-8 tests)
- **Docker**: Build and test Docker image
- **Summary**: Aggregate results

**Services:**
- PostgreSQL with PostGIS
- Redis

### 2. Deploy to Production (`deploy.yml`)

**Triggers:**
- Push to `main` branch
- Manual trigger via workflow_dispatch

**Jobs:**
- **Pre-deploy**: Validation checks
- **Build**: Build and push Docker images
- **Deploy**: Deploy to production server
- **Post-deploy**: Notifications and deployment records
- **Rollback**: Automatic rollback on failure (manual trigger only)

## Required Secrets

Configure these secrets in your GitHub repository settings:

### Docker Hub
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or access token

### Production Server
- `PRODUCTION_SERVER`: Production server hostname/IP
- `PRODUCTION_USER`: SSH user for deployment
- `SSH_PRIVATE_KEY`: SSH private key for authentication

### Optional (for notifications)
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `DISCORD_WEBHOOK_URL`: Discord webhook for notifications

## Setup Instructions

### 1. Configure GitHub Secrets

```bash
# Go to your repository settings
Settings > Secrets and variables > Actions > New repository secret
```

Add all required secrets listed above.

### 2. Set Up Production Server

On your production server:

```bash
# Clone repository
sudo mkdir -p /opt/spv-treasure-map
sudo chown ${USER}:${USER} /opt/spv-treasure-map
cd /opt/spv-treasure-map
git clone <your-repo-url> .

# Add deployment user's SSH key to authorized_keys
mkdir -p ~/.ssh
echo "<public-key>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Configure Docker Hub

```bash
# Create Docker Hub repository
docker login
docker tag spv-treasure-map:latest <username>/spv-treasure-map:latest
docker push <username>/spv-treasure-map:latest
```

### 4. Test Workflows Locally

Use [act](https://github.com/nektos/act) to test workflows locally:

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run test workflow
act pull_request -W .github/workflows/test.yml

# Run deploy workflow (with secrets)
act push -W .github/workflows/deploy.yml -s DOCKER_USERNAME=<user> -s DOCKER_PASSWORD=<pass>
```

## Workflow Customization

### Changing Deployment Conditions

Edit `deploy.yml`:

```yaml
on:
  push:
    branches: [ main, production ]  # Add more branches
    tags: [ 'v*' ]  # Trigger on version tags
```

### Adding Notifications

Add a notification step to `post-deploy`:

```yaml
- name: Slack notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Enabling Codecov

Uncomment the codecov steps in `test.yml`:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./backend/coverage.xml
```

### Adding Staging Environment

Create a new workflow `deploy-staging.yml`:

```yaml
on:
  push:
    branches: [ develop ]

jobs:
  deploy-staging:
    # Similar to production but with staging server
```

## Troubleshooting

### Tests Failing

1. Check test logs in GitHub Actions
2. Run tests locally: `python scripts/week*_test_*.py`
3. Verify database connection and migrations

### Deployment Failing

1. Check SSH connection: `ssh user@server`
2. Verify secrets are configured correctly
3. Check production server logs
4. Verify Docker images were built successfully

### Docker Build Failing

1. Check Dockerfile syntax
2. Verify all dependencies in requirements.txt
3. Check Docker build logs in Actions

### Health Checks Failing

1. Check service logs: `docker-compose logs backend`
2. Verify database is accessible
3. Check Redis connection
4. Verify environment variables

## Manual Deployment

To manually trigger deployment:

1. Go to Actions tab in GitHub
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Select branch (usually `main`)
5. Click "Run workflow"

## Rollback Procedure

### Automatic Rollback

If deployment health checks fail, the workflow will automatically attempt rollback (if `workflow_dispatch` triggered).

### Manual Rollback

```bash
# SSH to production server
ssh user@production-server

# Run rollback script
cd /opt/spv-treasure-map
bash scripts/production/rollback.sh
```

## Best Practices

1. **Never commit secrets**: Use GitHub Secrets for sensitive data
2. **Test before deploying**: All PRs must pass tests
3. **Use staging environment**: Test in staging before production
4. **Monitor deployments**: Set up notifications and monitoring
5. **Backup before deploy**: Automatic backups are created
6. **Review changes**: Code review all PRs before merging
7. **Tag releases**: Use semantic versioning tags (v1.0.0)

## Monitoring

### View Workflow Runs

```
Repository > Actions > Select workflow > View runs
```

### Check Deployment Status

```
Repository > Environments > production > View deployments
```

### View Logs

```
Actions > Select run > Select job > View logs
```

## Security Considerations

1. **Rotate secrets regularly**: Update all secrets every 90 days
2. **Limit SSH access**: Use dedicated deployment user with minimal permissions
3. **Scan for vulnerabilities**: Security job runs on every PR
4. **Review dependencies**: Check for outdated/vulnerable packages
5. **Use environment protection**: Require approval for production deploys

## Support

For issues with CI/CD workflows:
1. Check workflow logs in GitHub Actions
2. Review this documentation
3. Check production server logs
4. Contact DevOps team
