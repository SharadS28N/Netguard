# NetGuard Nepal - Deployment Guide

Complete guide for deploying the Evil Twin Detection Platform to production.

## Deployment Platforms

### Option 1: Vercel (Recommended)

Vercel is the recommended platform for Next.js applications.

#### Prerequisites

- Vercel account (https://vercel.com)
- GitHub repository
- Git installed locally

#### Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

#### Step 2: Import Project to Vercel

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Select GitHub repository
4. Configure:
   - **Framework**: Next.js
   - **Root Directory**: ./
   - **Build Command**: `npm run build`
   - **Output Directory**: .next

#### Step 3: Set Environment Variables

In Vercel dashboard:

```
NEXT_PUBLIC_API_URL=https://your-app.vercel.app
NEXT_PUBLIC_DEFAULT_THEME=dark
```

#### Step 4: Deploy

Click "Deploy" and wait for deployment to complete.

**Production URL**: https://your-app.vercel.app

---

### Option 2: Netlify

Alternative deployment platform.

#### Prerequisites

- Netlify account (https://netlify.com)
- GitHub repository

#### Step 1: Connect Repository

1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Select GitHub repository

#### Step 2: Build Settings

- **Build command**: `npm run build && npm run export` (if static)
- **Publish directory**: `.next`

#### Step 3: Deploy

Netlify auto-deploys on every push to main branch.

---

### Option 3: Docker (Self-Hosted)

Deploy using Docker containers.

#### Create Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/.next ./.next
EXPOSE 3000
CMD ["npm", "start"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'
services:
  netguard:
    build: .
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      NEXT_PUBLIC_API_URL: https://your-domain.com
    restart: always
```

#### Deploy

```bash
docker-compose up -d
```

---

### Option 4: AWS (EC2/ECS)

Deploy to AWS infrastructure.

#### Prerequisites

- AWS account
- EC2 instance running Node.js 18+
- Security groups configured

#### Step 1: Connect via SSH

```bash
ssh -i your-key.pem ec2-user@your-instance.com
```

#### Step 2: Clone Repository

```bash
git clone your-repo-url
cd netguard-nepal
```

#### Step 3: Install & Build

```bash
npm install
npm run build
```

#### Step 4: Install PM2 (Process Manager)

```bash
npm install -g pm2
pm2 start npm --name "netguard" -- start
pm2 save
pm2 startup
```

#### Step 5: Configure Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:3000/api;
    }
}
```

#### Step 6: Enable HTTPS (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Environment Variables

### Required for Production

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-domain.com
NODE_ENV=production

# Theme (optional)
NEXT_PUBLIC_DEFAULT_THEME=dark

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=your_id
```

### Optional for MongoDB Integration

```bash
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/netguard
DB_NAME=netguard
LOGS_COLLECTION=detection_logs
```

### Optional for Advanced Features

```bash
# Webhook endpoint for threat alerts
WEBHOOK_URL=https://your-webhook-service.com/threats

# API rate limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW_MS=3600000

# Log retention
LOG_RETENTION_DAYS=90
```

---

## Performance Optimization

### 1. Build Optimization

```bash
npm run build

# Analyze bundle size
npm install -g next-bundle-analyzer
npm run analyze
```

### 2. Image Optimization

- Use Next.js Image component
- Serve images via CDN
- Lazy load images

### 3. Database Optimization

For MongoDB:
```javascript
// Create indexes
db.detection_logs.createIndex({ "timestamp": -1 })
db.detection_logs.createIndex({ "threat_level": 1 })
db.detection_logs.createIndex({ "scan_id": 1 })
```

### 4. Caching Strategy

```javascript
// Cache detection results (1 hour)
export const revalidate = 3600
```

### 5. CDN Configuration

- Serve static assets from CDN
- Cache CSS/JS with long TTL
- Cache API responses with short TTL

---

## Security Checklist

- [ ] Environment variables not in version control
- [ ] HTTPS enabled (SSL/TLS certificate)
- [ ] API rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] CORS properly configured
- [ ] Security headers set (CSP, HSTS, etc.)
- [ ] Database credentials secured
- [ ] Regular security updates
- [ ] DDoS protection enabled
- [ ] WAF (Web Application Firewall) configured

### Security Headers

```nginx
# Add to Nginx configuration
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

---

## Monitoring & Logging

### Application Monitoring

```bash
# Install monitoring
npm install @vercel/analytics

# Set up error tracking
npm install sentry-nextjs
```

### Log Aggregation

```javascript
// Send logs to external service
import * as Sentry from "@sentry/nextjs"

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
})
```

### Health Check

```bash
# Test production deployment
curl https://your-domain.com/api/health

# Expected response
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: npm run build
      
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npx vercel --prod --token=$VERCEL_TOKEN
```

---

## Rollback Procedure

### Vercel

1. Go to Vercel dashboard
2. Navigate to Deployments
3. Click on previous deployment
4. Click "Promote to Production"

### Manual Rollback

```bash
git revert <commit-hash>
git push origin main
# Wait for CI/CD to redeploy
```

---

## Troubleshooting

### Issue: High Memory Usage

```bash
# Monitor memory
node --max-old-space-size=4096 server.js

# Or in Dockerfile
ENV NODE_OPTIONS="--max-old-space-size=4096"
```

### Issue: Slow API Response

1. Enable caching
2. Optimize database queries
3. Add rate limiting
4. Scale to multiple instances

### Issue: 502 Bad Gateway

```bash
# Check logs
pm2 logs netguard

# Restart service
pm2 restart netguard
```

### Issue: CORS Errors

```javascript
// app/api/detect/route.ts
import { headers } from 'next/headers'

export async function POST(request) {
  const headers = new Headers()
  headers.set('Access-Control-Allow-Origin', '*')
  headers.set('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
  return new Response(JSON.stringify(data), { headers })
}
```

---

## Backup & Recovery

### Database Backup

```bash
# MongoDB backup
mongodump --uri="mongodb+srv://..." --archive > backup.archive

# Restore
mongorestore --archive < backup.archive
```

### Application Backup

```bash
# Daily backup to S3
aws s3 sync ./.next s3://your-bucket/backups/$(date +%Y-%m-%d)
```

---

## Scaling

### Horizontal Scaling

```yaml
# Docker Compose with multiple instances
services:
  netguard-1:
    build: .
    ports: ["3001:3000"]
  netguard-2:
    build: .
    ports: ["3002:3000"]
  nginx:
    image: nginx
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Load Balancing

```nginx
upstream netguard {
    server localhost:3001;
    server localhost:3002;
    server localhost:3003;
}

server {
    listen 80;
    location / {
        proxy_pass http://netguard;
    }
}
```

---

## Cost Optimization

### Vercel
- Free tier: 100GB/month bandwidth
- Pro: $20/month (1TB bandwidth)
- Enterprise: Custom pricing

### AWS EC2
- t3.medium: ~$30/month
- Auto-scaling: Pay for used instances

### MongoDB
- Free tier: 512MB storage
- M0 cluster: Free (limited)
- M2+ paid clusters

---

## Maintenance

### Regular Updates

```bash
# Check for outdated packages
npm outdated

# Update packages
npm update

# Update Next.js
npm install next@latest react@latest
```

### Security Updates

```bash
# Check for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificate valid
- [ ] Database backups scheduled
- [ ] Monitoring and alerts enabled
- [ ] Log aggregation configured
- [ ] Performance metrics tracked
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Error tracking enabled
- [ ] Rollback procedure tested
- [ ] Incident response plan created
- [ ] Load testing completed

---

## Support

For deployment issues:
1. Check logs: `pm2 logs netguard`
2. Test endpoints: `curl https://your-domain.com/api/detect`
3. Verify environment variables
4. Check SSL certificate validity
5. Review monitoring and alerts
