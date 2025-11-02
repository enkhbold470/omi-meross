# Deployment Guide

Complete guide for deploying Satomi to production environments.

## Prerequisites

Before deploying, ensure you have:

1. **OpenAI API Key**: Get one from https://platform.openai.com/api-keys
2. **Node.js**: Version 18.17 or later
3. **pnpm**: Version 8 or later
4. **Git**: For version control and deployment

## Environment Configuration

### Required Environment Variables

Create a `.env.local` file (for local development) or configure environment variables in your hosting platform:

```bash
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

### Optional Environment Variables

```bash
# Node environment
NODE_ENV=production

# Next.js configuration
NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

## Local Development

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd satomi

# Install dependencies
pnpm install

# Create environment file
cp .env.example .env.local
# Edit .env.local and add your OPENAI_API_KEY

# Run development server
pnpm dev
```

Access the application at `http://localhost:3000`

### Development Commands

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Start production server locally
pnpm start

# Run linter
pnpm lint

# Type checking
pnpm tsc --noEmit
```

## Deployment Options

### Option 1: Vercel (Recommended)

Vercel is the easiest and recommended deployment option for Next.js applications.

#### Deploy via Vercel CLI

```bash
# Install Vercel CLI
pnpm add -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

#### Deploy via Vercel Dashboard

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to https://vercel.com/new
3. Import your repository
4. Configure environment variables:
   - Add `OPENAI_API_KEY`
5. Click "Deploy"

#### Configure Vercel

Create `vercel.json`:

```json
{
  "buildCommand": "pnpm build",
  "devCommand": "pnpm dev",
  "installCommand": "pnpm install",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

### Option 2: Netlify

Deploy using Netlify with edge functions.

#### Setup

1. Create `netlify.toml`:

```toml
[build]
  command = "pnpm build"
  publish = ".next"

[build.environment]
  NODE_VERSION = "18"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

2. Push to GitHub
3. Connect repository in Netlify dashboard
4. Add `OPENAI_API_KEY` to environment variables
5. Deploy

### Option 3: Docker

Deploy using Docker containers.

#### Create Dockerfile

```dockerfile
FROM node:18-alpine AS base

# Install pnpm
RUN npm install -g pnpm

FROM base AS dependencies
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS build
WORKDIR /app
COPY . .
COPY --from=dependencies /app/node_modules ./node_modules
RUN pnpm build

FROM base AS deploy
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=build /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

#### Update next.config.ts

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
};

export default nextConfig;
```

#### Build and Run

```bash
# Build Docker image
docker build -t satomi .

# Run container
docker run -p 3000:3000 \
  -e OPENAI_API_KEY=your-api-key \
  satomi
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### Option 4: AWS (Lambda + API Gateway)

Deploy as serverless functions on AWS.

#### Using Serverless Framework

1. Install Serverless:
```bash
pnpm add -g serverless
```

2. Create `serverless.yml`:

```yaml
service: satomi

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}

functions:
  app:
    handler: .next/standalone/server.handler
    events:
      - http: ANY /
      - http: ANY /{proxy+}

plugins:
  - serverless-nextjs-plugin
```

3. Deploy:
```bash
serverless deploy
```

### Option 5: Self-Hosted (VPS/Dedicated Server)

Deploy on your own server using PM2.

#### Setup

```bash
# On your server
git clone <your-repo-url>
cd satomi

# Install pnpm
npm install -g pnpm

# Install dependencies
pnpm install

# Build
pnpm build

# Install PM2
npm install -g pm2

# Start with PM2
pm2 start pnpm --name satomi -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

#### Nginx Configuration

Create `/etc/nginx/sites-available/satomi`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/satomi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Post-Deployment Checklist

### 1. Verify Environment Variables

Ensure `OPENAI_API_KEY` is set correctly:

```bash
# Test API endpoint
curl -X POST https://yourdomain.com/api/japanese-concept \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ikigai?"}'
```

### 2. Test All Endpoints

- `/api/japanese-concept`
- `/api/process-content`
- `/api/validate-file`

### 3. Check Logs

Monitor application logs for errors:

```bash
# Vercel
vercel logs

# PM2
pm2 logs satomi

# Docker
docker logs <container-id>
```

### 4. Monitor Performance

- Response times
- Error rates
- OpenAI API usage

### 5. Setup SSL/TLS

Ensure HTTPS is enabled:
- Vercel/Netlify: Automatic
- Self-hosted: Use Let's Encrypt with Certbot

## Monitoring and Maintenance

### Health Checks

Create a health check endpoint:

```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok', timestamp: new Date().toISOString() });
}
```

### Logging

Consider adding a logging service:
- Vercel: Built-in logging
- Self-hosted: PM2 logs, Winston, or Pino
- Cloud: CloudWatch (AWS), Stackdriver (GCP)

### Error Tracking

Integrate error tracking:

```bash
pnpm add @sentry/nextjs
```

Configure in `sentry.client.config.ts` and `sentry.server.config.ts`

### Backup Strategy

No database in current version, but backup:
- Environment variables
- Application code (Git)
- Configuration files

## Scaling Considerations

### Horizontal Scaling

Current architecture is stateless and can scale horizontally:

1. **Vercel/Netlify**: Automatic scaling
2. **AWS**: Use Auto Scaling Groups
3. **Docker**: Use Kubernetes or Docker Swarm
4. **Load Balancer**: Nginx, AWS ALB, or Cloudflare

### Performance Optimization

1. **Caching**: Add Redis for response caching
2. **CDN**: Use Cloudflare or AWS CloudFront
3. **Database**: Add PostgreSQL for conversation history
4. **Queue**: Add Bull/BullMQ for background jobs

### Cost Optimization

Monitor OpenAI API costs:

1. Implement rate limiting
2. Cache common queries
3. Set usage quotas
4. Monitor token consumption

```typescript
// Example: Track token usage
const completion = await openai.chat.completions.create({
  model: 'gpt-4o',
  messages,
});

const tokensUsed = completion.usage?.total_tokens;
console.log(`Tokens used: ${tokensUsed}`);
```

## Troubleshooting

### Common Issues

#### 1. "Invalid API key" Error

**Solution**: Verify `OPENAI_API_KEY` is set correctly
```bash
echo $OPENAI_API_KEY
```

#### 2. Build Failures

**Solution**: 
- Clear cache: `rm -rf .next`
- Reinstall: `rm -rf node_modules && pnpm install`
- Check Node version: `node --version`

#### 3. Timeout Errors

**Solution**: 
- Increase timeout in hosting platform
- Optimize OpenAI requests
- Implement request queuing

#### 4. Rate Limit Errors

**Solution**:
- Implement exponential backoff
- Add rate limiting on your end
- Upgrade OpenAI plan

### Debug Mode

Enable debug logging:

```typescript
// lib/openai.ts
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
  dangerouslyAllowBrowser: false,
  maxRetries: 3,
  timeout: 30000, // 30 seconds
});
```

## Security Best Practices

1. **Never commit `.env` files**
2. **Use environment variables** for all secrets
3. **Enable CORS** only for trusted domains
4. **Implement rate limiting**
5. **Keep dependencies updated**: `pnpm update`
6. **Regular security audits**: `pnpm audit`
7. **Use HTTPS** in production
8. **Implement input validation**

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
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8
          
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
        
      - name: Run linter
        run: pnpm lint
        
      - name: Build
        run: pnpm build
        
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## Rollback Strategy

### Vercel

```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback <deployment-url>
```

### Docker

```bash
# Keep previous images tagged
docker tag satomi:latest satomi:backup

# Rollback
docker stop satomi && docker rm satomi
docker run -d --name satomi satomi:backup
```

### Self-Hosted

```bash
# Keep previous builds
git checkout <previous-commit>
pnpm install
pnpm build
pm2 restart satomi
```

## Support and Resources

- Next.js Documentation: https://nextjs.org/docs
- OpenAI API Reference: https://platform.openai.com/docs
- Vercel Documentation: https://vercel.com/docs
- pnpm Documentation: https://pnpm.io

## Conclusion

Choose the deployment option that best fits your needs:
- **Quick start**: Vercel
- **Custom infrastructure**: Docker + AWS/GCP
- **Full control**: Self-hosted with PM2

Remember to monitor your application and OpenAI API usage to optimize costs and performance.

